#!/usr/bin/env python

"""
Unit tests for Interval Data Class

- test_create_interval
- test_interval_properties
- test_interval_conversion
- test_interval_hash
- test_interval_contains
- test_interval_overlaps
- test_interval_intersect
- test_interval_union
- test_interval_random_values
- test_interval_random_intervals
- test_interval_from_intersect
- test_interval_from_union
- test_interval_from_object
- test_interval_from_text
"""

from dataclasses import asdict, astuple
from typing import List
from unittest import TestCase

from numpy import mean

from slig.datastructs import Interval


class TestInterval(TestCase):

  test_intervals: List[Interval]
  overlaps: List[List[bool]]

  def setUp(self):
    self.test_intervals = []
    self.test_intervals.append(Interval(-10, 25))
    self.test_intervals.append(Interval(10.5, 45))
    self.test_intervals.append(Interval(-10.5, 45))
    self.test_intervals.append(Interval(10.5, -45))
    self.test_intervals.append(Interval(-10.5, -45))
    self.test_intervals.append(Interval(5, 5))
    self.test_intervals.append(Interval(5, 6))
    self.overlaps = [
      [True,  True,  True,  True,  False, True,  True],
      [True,  True,  True,  False, False, False, False],
      [True,  True,  True,  True,  False, True,  True],
      [True,  False, True,  True,  True,  True,  True],
      [False, False, False, True,  True,  False, False],
      [True,  False, True,  True,  False, True,  False],
      [True,  False, True,  True,  False, False, True]
    ]

  def test_create_interval(self):
    test_intervals = []
    test_intervals.append(Interval(10.5, 20))
    test_intervals.append(Interval(20, '10.5'))
    test_intervals.append(Interval(**{'lower': 10.5, 'upper': 20}))
    test_intervals.append(Interval(*('20', '10.5')))

    for interval in test_intervals:
      self.assertEqual(interval.lower, 10.5)
      self.assertEqual(interval.upper, 20)
      self.assertTrue(isinstance(interval.lower, float))
      self.assertTrue(isinstance(interval.upper, float))

  def test_interval_properties(self):
    for interval in self.test_intervals:
      #print(f'{interval}: length={interval.length} midpoint={interval.midpoint}')
      self.assertEqual(interval.length, interval.upper - interval.lower)
      self.assertEqual(interval.midpoint, mean([interval.lower, interval.upper]))

  def test_interval_conversion(self):
    for interval in self.test_intervals:
      #print(f'{interval}: dict={asdict(interval)}, tuple={astuple(interval)}')
      self.assertEqual(asdict(interval), {'lower': interval.lower, 'upper': interval.upper})
      self.assertEqual(astuple(interval), (interval.lower, interval.upper))

  def test_interval_hash(self):
    intervals = {}
    for interval in self.test_intervals:
      intervals[interval] = interval.length
    for interval in self.test_intervals:
      other = Interval(interval.lower, interval.upper)
      self.assertTrue(interval in intervals)
      self.assertEqual(interval.length, intervals[interval])
      self.assertTrue(interval == other)
      self.assertTrue(hash(interval) == hash(other))

  def test_interval_contains(self):
    interval = Interval(-5, 15)
    self.assertTrue(interval.lower in interval)
    self.assertTrue(interval.upper in interval)
    self.assertTrue(interval.midpoint in interval)
    self.assertTrue((interval.lower + 0.1) in interval)
    self.assertTrue((interval.upper - 0.1) in interval)
    self.assertFalse(interval.contains(interval.lower, inc_lower=False))
    self.assertFalse(interval.contains(interval.upper, inc_upper=False))
    self.assertFalse((interval.lower - 0.1) in interval)
    self.assertFalse((interval.upper + 0.1) in interval)

  def test_interval_encloses(self):
    interval = Interval(-5, 5)
    test_intervals = []
    test_intervals.append(Interval(-6, 4))
    test_intervals.append(Interval(-4, 4))
    test_intervals.append(Interval(-2, 2))
    test_intervals.append(Interval(4, 6))
    test_intervals.append(Interval(-5, 5))
    test_intervals.append(Interval(-6, 6))

    for subinterval in test_intervals:
      comparsion = interval.lower <= subinterval.lower <= subinterval.upper <= interval.upper
      #print(f'{subinterval} in {interval}: expect={comparsion} actual={subinterval in interval}')
      self.assertEqual(subinterval in interval, comparsion)

  def test_interval_overlaps(self):
    for i, first in enumerate(self.test_intervals):
      for j, second in enumerate(self.test_intervals):
        #print(f'{first} and {second}: expect={self.overlaps[i][j]}, actual={first.overlaps(second)}')
        self.assertEqual(first.is_intersecting(second), self.overlaps[i][j])

  def test_interval_intersect(self):
    for i, first in enumerate(self.test_intervals):
      for j, second in enumerate(self.test_intervals):
        intersect = first.get_intersection(second)
        if self.overlaps[i][j]:
          expected = first if first == second \
                           else Interval(max(first.lower, second.lower),
                                         min(first.upper, second.upper))

          #print(f'{first} and {second}:')
          #print(f'  expect={expected}')
          #print(f'  actual={intersect}')
          #print(f'  length={intersect.length}')
          self.assertEqual(intersect, expected)
        else:
          #print(f'{first} and {second}:')
          #print(f'  expect=None')
          #print(f'  actual={intersect}')
          self.assertEqual(intersect, None)

  def test_interval_from_intersect(self):
    intervals = [Interval(-x, x) for x in range(5, 1, -1)]
    for i in range(1, len(intervals)):
      intersect = Interval.from_intersection(intervals[0:i+1])
      #print(f'{intersect}')
      self.assertEqual(intervals[i], intersect)

    intervals = [Interval(x, x + 1) for x in range(5)]
    intersect = Interval.from_intersection(intervals)
    #print(f'{intersect}')
    self.assertEqual(None, intersect)

  def test_interval_from_union(self):
    intervals = [Interval(x, x + 1) for x in range(5)]
    for i in range(1, len(intervals)):
      union = Interval.from_union(intervals[0:i+1])
      #print(f'{union}')
      self.assertEqual(union, Interval(0, i + 1))

  def test_interval_from_dict(self):
    test_interval = Interval(10.5, 20)
    dictobject = {'lower': 10.5, 'upper': 20}

    self.assertEqual(test_interval, Interval.from_dict(dictobject))
      

  def test_interval_from_text(self):
    test_interval = Interval(10.5, 20)
    texts = []
    texts.append('{"lower":10.5,"upper":20}')
    texts.append('{"lower":"10.5","upper":"20"}')

    for text in texts:
      #print(f'text="{text[0]}"' if "'" in text else f"text='{text[0]}'")
      #print(f'format={text[1]}')
      self.assertEqual(test_interval, Interval.from_JSON(text))

      
