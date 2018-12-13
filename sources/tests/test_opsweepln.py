#!/usr/bin/env python

"""
Unit tests for Generalized One-Pass Sweep-line Algorithm

This script implements the following tests:
  - test_opsweepln_simple
  - test_opsweepln_random
"""

from typing import List
from unittest import TestCase

from sources.algorithms.sweepln.opsweepln import OpSLEvaluator, OpSweepln
from sources.datastructs.datasets.regionset import RegionSet
from sources.datastructs.datasets.timeline import Event, EventKind, Timeline
from sources.datastructs.shapes.region import Region, RegionPair


class TestOpSweepln(TestCase):

  def test_opsweepln_simple(self):
    regionset = RegionSet(dimension=2)
    regionset.add(Region([0, 0], [3, 5]))
    regionset.add(Region([3, 1], [5, 5]))
    regionset.add(Region([2, 4], [6, 6]))

    opsweepln = OpSweepln(regionset)
    opsweepln.put(OpSLEvaluator())

    for i in range(regionset.dimension):
      expect = regionset.overlaps(i)
      actual = opsweepln.evaluate(i)[0]
      #for pair in expect: print(f'Expect:\t{pair[0]}\n\t{pair[1]}')
      #for pair in actual: print(f'Actual:\t{pair[0]}\n\t{pair[1]}')
      for pair in expect: self.assertTrue(pair in actual)
      self.assertEqual(len(expect), len(actual))

  def test_opsweepln_random(self):
    regionset = RegionSet.from_random(30, Region([0]*3, [100]*3), sizepc_range=Region([0]*3, [0.5]*3), precision=0)
    opsweepln = OpSweepln(regionset)
    opsweepln.put(OpSLEvaluator())

    actuals = []
    #for region in regionset: print(f'{region}')
    for i in range(regionset.dimension):
      #print(f'Dimension: {i}')
      expect = regionset.overlaps(i)
      actual = opsweepln.evaluate(i)[0]
      #for pair in expect: print(f'Expect: {pair[0].id} {pair[1].id}')
      #for pair in actual: print(f'Actual: {pair[0].id} {pair[1].id}')
      for pair in expect: self.assertTrue(pair in actual)
      self.assertEqual(len(expect), len(actual))
      actuals.append(actual)

    self.assertTrue(all([len(actual) for actual in actuals]))
    for pair in actuals[0]:
      for d in range(1, regionset.dimension):
        self.assertTrue(pair in actuals[d] or (pair[1], pair[0]) in actuals[d])