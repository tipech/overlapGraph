#!/usr/bin/env python

"""
Unit tests for Querying List of All Intersecting Regions

This script implements the following tests:
  - test_listintxns_results
"""

from typing import Dict, Iterator, List
from unittest import TestCase

from sources.algorithms.rigqueries.listintxns import ListIntxns
from sources.datastructs.datasets.regionset import RegionSet
from sources.datastructs.shapes.region import Region, RegionIntxn


class TestListIntxns(TestCase):

  regions: List[RegionSet]

  def setUp(self):
    definedset = RegionSet(dimension=2)
    definedset.streamadd([
      Region([0, 0], [5, 5]),
      Region([2, 2], [5, 10]),
      Region([1, 5], [3, 7]),
      Region([3, 3], [4, 7]),
      Region([-5, 5], [1, 7]),
      Region([-5, 5], [2, 7]),
      Region([3, 4], [5, 6])
    ])
    
    bounds  = Region([0]*2, [100]*2)
    sizerng = Region([0]*2, [0.1]*2)

    self.regions = [
      definedset,
      RegionSet.from_random(10,  bounds, sizepc_range=sizerng, precision=1),
      RegionSet.from_random(100, bounds, sizepc_range=sizerng, precision=1),
    ]

  def test_listintxns_results(self):

    def get_results(i: int, method: Iterator[RegionIntxn], name: str) -> Dict:
      results = {'count': 0, 'maxlen': 0, 'lengths': {}}
      for j, intxns in enumerate(method):
        #print(f'{i}[{j}][{name}]: {[x.id for x in intxns]}')
        intxn = [x.id for x in intxns]
        length = len(intxn)
        results['count'] = j
        results['maxlen'] = length
        results['lengths'][length] = results['lengths'][length] + 1 \
                                     if length in results['lengths'] else 0
      return results

    for i, regions in enumerate(self.regions):
      lintxns = ListIntxns(regions)
      results_rig = get_results(i, lintxns.with_rigraph(), 'rigraph')
      results_msl = get_results(i, lintxns.with_multisweep(), 'msweepln')

      self.assertDictEqual(results_rig, results_msl)
