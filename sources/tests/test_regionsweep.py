#!/usr/bin/env python

"""
Unit tests for Generalized One-Pass Sweep-line Algorithm

- test_regionsweep_simple
- test_regionsweep_random
"""

from typing import List
from unittest import TestCase

from sources.algorithms import \
     RegionSweep, RegionSweepDebug, RegionSweepOverlaps
from sources.core import \
     Region, RegionPair, RegionSet


class TestRegionSweep(TestCase):

  def _evaluate_regionsweep(self, regions: RegionSet, i: int) -> List[RegionPair]:
    subscribers = [] #[RegionSweepDebug()]
    return RegionSweepOverlaps.evaluate(regions, *subscribers)(i)

  def test_regionsweep_simple(self):
    regionset = RegionSet(dimension=2)
    regionset.add(Region([0, 0], [3, 5]))
    regionset.add(Region([3, 1], [5, 5]))
    regionset.add(Region([2, 4], [6, 6]))

    for i in range(regionset.dimension):
      expect = regionset.overlaps(i)
      actual = self._evaluate_regionsweep(regionset, i)
      #for pair in expect: print(f'Expect {i}:\t{pair[0]}\n\t{pair[1]}')
      #for pair in actual: print(f'Actual {i}:\t{pair[0]}\n\t{pair[1]}')
      for pair in expect:
        #passed = "Passed" if pair in actual else "Failed"
        #print(f'{passed} {i}: {pair[0]} {pair[1]}')
        self.assertTrue(pair in actual)
      self.assertEqual(len(expect), len(actual))

  def test_regionsweep_random(self):
    regionset = RegionSet.from_random(30, Region([0]*3, [100]*3), sizepc=Region([0]*3, [0.5]*3), precision=0)
    actuals = []
    #for region in regionset: print(f'{region}')
    for i in range(regionset.dimension):
      #print(f'Dimension: {i}')
      expect = regionset.overlaps(i)
      actual = self._evaluate_regionsweep(regionset, i)
      #for pair in expect: print(f'Expect {i}: {pair[0].id} {pair[1].id}')
      #for pair in actual: print(f'Actual {i}: {pair[0].id} {pair[1].id}')
      for pair in expect: 
        #passed = "Passed" if pair in actual else "Failed"
        #print(f'{passed} {i}: {pair[0].id} {pair[1].id}')
        self.assertTrue(pair in actual)
      self.assertEqual(len(expect), len(actual))
      actuals.append(actual)

    self.assertTrue(all([len(actual) for actual in actuals]))
    for pair in actuals[0]:
      for d in range(1, regionset.dimension):
        self.assertTrue(pair in actuals[d] or (pair[1], pair[0]) in actuals[d])
