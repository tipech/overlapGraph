#!/usr/bin/env python

"""
Unit tests for SLIG algorithm Class

- 
"""

from dataclasses import asdict, astuple
from functools import reduce
from typing import List, Tuple
from unittest import TestCase

from numpy import mean
from pprint import pprint

from slig.datastructs import Interval, Region, RegionSet
from slig import SLIG


class TestSLIG(TestCase):

  test_regions: List[Region]

  def setUp(self):
    self.test_regions = []
    self.test_regions.append(Region([0, 0], [5, 5]))
    self.test_regions.append(Region([2, 2], [5, 10]))
    self.test_regions.append(Region([1, 5], [3, 7]))
    self.test_regions.append(Region([3, 5], [1, 7]))
    self.test_regions.append(Region([4, 8], [2, 7]))
    self.overlaps = [
      [True,  True,  False, False, False], #  [0, 0], [5, 5]
      [True,  True,  True,  False, False], #  [2, 2], [5, 10]
      [False, True,  True,  False, True],  #  [1, 5], [3, 7]
      [False, False, False, True,  True],  # [-5, 5], [1, 7]
      [False, False, True,  True,  True]   # [-5, 5], [2, 7]
    ]
    self.test_regionset = RegionSet(dimension=2)
    for r in self.test_regions:
      self.test_regionset.add(r)

  def test_init(self):
    test = SLIG(self.test_regionset)
    self.assertTrue( isinstance(test.regionset, RegionSet))
    self.assertEqual( test.regionset.id, self.test_regionset.id)

  def test_prepare(self):
    test = SLIG(self.test_regionset)
    test.prepare()
    self.assertEqual(len(test.iterator), self.test_regionset.dimension)
    self.assertTrue(all(dim[i][0] <= dim[i+1][0] for dim in test.iterator
      for i in range(len(dim)-1)))

  def test_sweep(self):
    test = SLIG(self.test_regionset)
    test.prepare()
    graph = test.sweep()
    self.assertEqual(len(graph.G.edges), 3)