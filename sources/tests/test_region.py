#!/usr/bin/env python

#
# tests/test_region.py - Unit tests for shapes/region.py
#
# This script implements the following tests:
#   - test_create_region
#   - test_dimension_mismatch
#   - test_region_properties
#   - test_region_contains
#   - test_region_equality
#   - test_region_overlaps
#   - test_region_difference
#

from dataclasses import asdict, astuple
from functools import reduce
from numpy import mean
from typing import List
from unittest import TestCase
from ..shapes.interval import Interval
from ..shapes.region import Region

class TestRegionNoSetup(TestCase):

  test_regions: List[Region]
  overlaps: List[List[bool]]

  def setUp(self):
    self.test_regions = []
    self.test_regions.append(Region([0, 0], [5, 5]))
    self.test_regions.append(Region([2, 2], [5, 10]))
    self.test_regions.append(Region([1, 5], [3, 7]))
    self.test_regions.append(Region([-5, 5], [1, 7]))
    self.test_regions.append(Region([-5, 5], [2, 7]))
    self.overlaps = [
      [True,  True,  False, False, False], #  [0, 0], [5, 5]
      [True,  True,  True,  False, False], #  [2, 2], [5, 10]
      [False, True,  True,  False, True],  #  [1, 5], [3, 7]
      [False, False, False, True,  True],  # [-5, 5], [1, 7]
      [False, False, True,  True,  True]   # [-5, 5], [2, 7]
    ]

  def test_create_region(self):
    test_regions = []
    test_regions.append(Region([0], [5]))
    test_regions.append(Region([0, 0], [5, 5]))
    test_regions.append(Region([0, 0, 0], [5, 5, 5]))

    for i, region in enumerate(test_regions):
      #print(region)
      self.assertEqual(region.dimension, i + 1)
      self.assertEqual(region.dimension, len(region.lower))
      self.assertEqual(region.dimension, len(region.upper))
      self.assertTrue(all([d == 0 for d in region.lower]))
      self.assertTrue(all([d == 5 for d in region.upper]))

  def test_dimension_mismatch(self):
    with self.assertRaises(AssertionError):
      Region([0, 0], [10, 10], dimension = 3)
    with self.assertRaises(AssertionError):
      Region([0, 0, 0], [10, 10])

  def test_region_properties(self):
    for region in self.test_regions:
      #print('\n  '.join([
      #  f'{region}:',
      #  f'dimensions={[astuple(d) for d in region.dimensions]}',
      #  f'lengths={region.lengths}',
      #  f'midpoint={region.midpoint}',
      #  f'size={region.size}'
      #]))
      self.assertEqual(region.dimensions, [Interval(region.lower[i], region.upper[i]) for i in range(region.dimension)])
      self.assertEqual(region.lengths, [d.upper - d.lower for d in region.dimensions])
      self.assertEqual(region.midpoint, [mean([d.lower, d.upper]) for d in region.dimensions])
      self.assertEqual(region.size, reduce(lambda x, y: x*y, region.lengths))

  def test_region_contains(self):
    region = Region([-5, 0], [15, 10])
    self.assertTrue(region.lower in region)
    self.assertTrue(region.upper in region)
    self.assertTrue(region.midpoint in region)
    self.assertTrue([v + 0.1 for v in region.lower] in region)
    self.assertTrue([v - 0.1 for v in region.upper] in region)
    self.assertTrue([region.lower[0] + 0.1, region.lower[1]]       in region)
    self.assertTrue([region.lower[0]      , region.lower[1] + 0.1] in region)
    self.assertTrue([region.upper[0] - 0.1, region.upper[1]]       in region)
    self.assertTrue([region.upper[0]      , region.upper[1] - 0.1] in region)
    self.assertFalse(region.contains(region.lower, inc_lower = False))
    self.assertFalse(region.contains(region.upper, inc_upper = False))
    self.assertFalse([v - 0.1 for v in region.lower] in region)
    self.assertFalse([v + 0.1 for v in region.upper] in region)
    self.assertFalse([region.lower[0] - 0.1, region.lower[1]]       in region)
    self.assertFalse([region.lower[0]      , region.lower[1] - 0.1] in region)
    self.assertFalse([region.upper[0] + 0.1, region.upper[1]]       in region)
    self.assertFalse([region.upper[0]      , region.upper[1] + 0.1] in region)

  def test_region_equality(self):
    test_regions = []
    test_regions.append(Region([-5, 0], [15, 10]))
    test_regions.append(Region([-5, 1], [15, 10]))
    test_regions.append(Region([-6, 0], [15, 10]))
    test_regions.append(Region([-5, 0], [14, 10]))
    test_regions.append(Region([-5, 0], [15, 11]))
    match_region = Region([-5, 0], [15, 10])

    for region in test_regions:
      self.assertNotEqual(region.id, match_region.id)
      if all([region.lower[i] == match_region.lower[i] and \
              region.upper[i] == match_region.upper[i] for i in range(match_region.dimension)]):
        self.assertListEqual(region.lower, match_region.lower)
        self.assertListEqual(region.upper, match_region.upper)
        self.assertEqual(region, match_region)

  def test_region_overlaps(self):
    for i, first in enumerate(self.test_regions):
      for j, second in enumerate(self.test_regions):
        overlap = first.overlaps(second)
        #print(f'{first}\n{second}:')
        #print(f'  expect={self.overlaps[i][j]}')
        #print(f'  actual={overlap}')
        self.assertEqual(overlap, self.overlaps[i][j])

  def test_region_difference(self):
    for i, first in enumerate(self.test_regions):
      for j, second in enumerate(self.test_regions):
        difference = first.difference(second)
        if self.overlaps[i][j]:
          #print(f'{first}\n{second}:')
          #print(f'  actual={difference}')
          #print(f'  size={difference.size}')
          for x, d in enumerate(first.dimensions):
            self.assertEqual(d.difference(second.dimensions[x]), 
                             difference.dimensions[x])
        else:
          #print(f'{first}\n{second}:')
          #print(f'  expect=None')
          #print(f'  actual={difference}')
          self.assertEqual(difference, None)
