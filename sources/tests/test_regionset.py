#!/usr/bin/env python

#
# tests/test_regionset.py - Unit tests for generators/regionet.py
#
# This script implements the following tests:
#   - test_create_regionset
#   - test_regionset_dimension_mismatch
#   - test_regionset_outofbounds
#

from dataclasses import asdict, astuple
from typing import List
from unittest import TestCase
from ..shapes.regionset import RegionSet
from ..shapes.region import Region

class TestRegionSet(TestCase):

  def test_create_regionset(self):
    bounds = Region([0, 0], [100, 100])
    regionset = RegionSet(bounds = bounds)
    regions = bounds.random_regions(10)
    for region in regions:
      regionset.add(region)

    #print(f'{regionset}')
    self.assertEqual(regionset.size, len(regions))
    self.assertTrue(bounds.encloses(regionset.minbounds))
    for i, region in enumerate(regions):
      self.assertEqual(region, regionset[i])
      self.assertEqual(region, regionset[region.id])
      self.assertTrue(region in regionset)
      self.assertTrue(region.id in regionset)
      self.assertTrue(bounds.encloses(region))

  def test_regionset_dimension_mismatch(self):
    regionset = RegionSet(dimension = 2)
    with self.assertRaises(AssertionError):
      regionset.add(Region([0]*3,[1]*3))

  def test_regionset_outofbounds(self):
    regionset = RegionSet(bounds = Region([0, 0], [10, 10]))
    with self.assertRaises(AssertionError):
      regionset.add(Region([-1, -1],[5, 5]))
