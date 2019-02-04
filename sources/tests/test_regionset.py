#!/usr/bin/env python

"""
Unit tests for Regions Collection

- test_create_regionset
- test_regionset_dimension_mismatch
- test_regionset_outofbounds
- test_regionset_iteration
- test_regionset_from_random
- test_regionset_tofrom_output
- test_regionset_tofrom_output_backlinks
- test_regionset_filter
- test_regionset_subset
"""

from io import StringIO
from typing import Iterable, List
from unittest import TestCase

from sources.core import Region, RegionSet


class TestRegionSet(TestCase):

  def _test_regionset(self, regionset: RegionSet, nregions: int, bounds: Region, regions: Iterable[Region]):
    #print(f'{regionset}')
    self.assertEqual(regionset.length, nregions)
    self.assertTrue(bounds.encloses(regionset.minbounds))
    for i, region in enumerate(regions):
      #print(f'{region}')
      self.assertEqual(region, regionset[i])
      self.assertEqual(region, regionset[region.id])
      self.assertTrue(region in regionset)
      self.assertTrue(region.id in regionset)
      self.assertTrue(bounds.encloses(region))

  def test_create_regionset(self):
    bounds = Region([0, 0], [100, 100])
    regionset = RegionSet(bounds = bounds)
    regions = bounds.random_regions(10)
    for region in regions:
      regionset.add(region)
    self._test_regionset(regionset, len(regions), bounds, regions)

  def test_regionset_dimension_mismatch(self):
    regionset = RegionSet(dimension=2)
    with self.assertRaises(AssertionError):
      regionset.add(Region([0]*3,[1]*3))

  def test_regionset_outofbounds(self):
    regionset = RegionSet(bounds=Region([0, 0], [10, 10]))
    with self.assertRaises(AssertionError):
      regionset.add(Region([-1, -1],[5, 5]))

  def test_regionset_iteration(self):
    regionset = RegionSet.from_random(100, Region([0]*2, [10]*2), sizepc=Region([0]*2, [0.5]*2))

    for region in regionset:
      self.assertIsInstance(region, Region)
      self.assertIn(region, regionset)

    for region in regionset.keys():
      self.assertIsInstance(region, str)
      self.assertIn(region, regionset)

    for rid, region in regionset.items():
      self.assertIsInstance(rid, str)
      self.assertIsInstance(region, Region)
      self.assertIn(rid, regionset)
      self.assertIn(region, regionset)
      self.assertEqual(rid, region.id)

  def test_regionset_from_random(self):
    nregions = 50
    bounds = Region([0]*2, [10]*2)
    sizepc = Region([0]*2, [0.5]*2)
    regionset = RegionSet.from_random(nregions, bounds, sizepc=sizepc, precision=1)
    self._test_regionset(regionset, nregions, bounds, regionset)

  def test_regionset_tofrom_output(self):
    nregions = 10
    bounds = Region([0]*2, [100]*2)
    sizepc = Region([0]*2, [0.5]*2)
    regionset = RegionSet.from_random(nregions, bounds, sizepc=sizepc, precision=1)

    with StringIO() as output:
      RegionSet.to_output(regionset, output, options={'compact': True})
      before = output.getvalue()
      #print(before)
      output.seek(0)
      newregionset = RegionSet.from_source(output, 'json')
      self._test_regionset(newregionset, nregions, bounds, regionset)

      output.truncate(0)
      output.seek(0)
      RegionSet.to_output(newregionset, output, options={'compact': True})
      after = output.getvalue()
      #print(after)
      self.assertEqual(before, after)

  def test_regionset_tofrom_output_backlinks(self):
    nregions = 10
    bounds = Region([0]*2, [100]*2)
    sizepc = Region([0]*2, [0.5]*2)
    regionset = RegionSet.from_random(nregions, bounds, sizepc=sizepc, precision=1)
    regions = []

    for first in regionset:
      for second in regionset:
        if first is not second:
          regions.append(first.union(second, 'reference'))
          if first.overlaps(second):
            regions.append(first.intersect(second, 'reference'))

    for region in regions:
      #print(f'{region}')
      regionset.add(region)

    with StringIO() as output:
      RegionSet.to_output(regionset, output, options={'compact': True})
      #print(output.getvalue())
      output.seek(0)
      newregionset = RegionSet.from_source(output, 'json')

      for region in regions:
        for field in ['intersect', 'union']:
          if field in region:
            self.assertTrue(field in newregionset[region.id])
            self.assertTrue(all([isinstance(r, Region) for r in newregionset[region.id][field]]))
            self.assertListEqual(region[field], newregionset[region.id][field])

  def test_regionset_filter(self):
    nregions = 50
    bounds = Region([0]*2, [10]*2)
    sizepc = Region([0]*2, [0.5]*2)
    regionset = RegionSet.from_random(nregions, bounds, sizepc=sizepc, precision=1)    
    filter_bound = Region([5]*2, [10]*2)
    filtered = regionset.filter(filter_bound)

    self.assertEqual(filter_bound, filtered.bounds)
    for region in regionset:
      #print(f'{region}: {region in filtered}')
      self.assertEqual(filter_bound.encloses(region), region in filtered)
    for region in filtered:
      #print(f'{region}')
      self.assertTrue(filter_bound.encloses(region))

  def test_regionset_subset(self):
    nregions = 50
    bounds = Region([0]*2, [10]*2)
    sizepc = Region([0]*2, [0.5]*2)
    regionset = RegionSet.from_random(nregions, bounds, sizepc=sizepc, precision=1)    
    subset = ['A', 'C', 'E', 'G', 'I', 'K'] + [regionset[r] for r in ['AA', 'P', 'Q', 'R']]
    subsetted = regionset.subset(subset)

    self.assertEqual(regionset.bounds, subsetted.bounds)
    self.assertGreaterEqual(len(regionset), len(subsetted))
    self.assertEqual(len(subset), len(subsetted))
    for r in subset:
      if isinstance(r, str):
        #print(f'{r}: {r in subsetted} {subsetted[r]}')
        self.assertIn(r, subsetted)
        self.assertIs(regionset[r], subsetted[r])
      else:
        #print(f'{r.id}: {r in subsetted} {r}')
        self.assertIsInstance(r, Region)
        self.assertIn(r, subsetted)
        self.assertIs(regionset[r.id], subsetted[r.id])
