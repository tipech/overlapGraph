#!/usr/bin/env python

"""
Unit tests for Enumeration of Region Intersections

- test_enumerate_results
"""

from time import perf_counter
from typing import Dict, Iterator, List, NamedTuple, Tuple
from unittest import TestCase

from sources.algorithms.queries.enumerate import RegionIntersect
from sources.algorithms.queries.enumerate.bynxgraph import EnumerateByNxGSweepCtor
from sources.algorithms.queries.enumerate.byregioncyclesweep import EnumerateByRegionCycleSweep
from sources.algorithms.sweepln.basesweep import SweepTaskRunner
from sources.algorithms.sweepln.regionsweepdebug import RegionSweepDebug
from sources.datastructs.datasets.regionset import RegionSet
from sources.datastructs.shapes.region import Region, RegionIntxn


class TestEnumerateResult(NamedTuple):
  length: int
  levels: Dict[int, int]
  intersects: List[Tuple[str]]


class TestEnumerate(TestCase):

  regions: Dict[str, RegionSet]

  def setUp(self):
    definedset = RegionSet(dimension=2)
    definedset.streamadd([
      Region([0, 0], [5, 5], 'A'),
      Region([2, 2], [5, 10], 'B'),
      Region([1, 5], [3, 7], 'C'),
      Region([3, 3], [4, 7], 'D'),
      Region([-5, 5], [1, 7], 'E'),
      Region([-5, 5], [2, 7], 'F'),
      Region([3, 4], [5, 6], 'G')
    ])

    bounds = Region([0]*2, [1000]*2)

    self.regions = {'definedset': definedset}

    for nregions in [pow(10, n) for n in range(1, 4)]:
      for sizepc in [0.01, 0.05, *([] if nregions > 100 else [0.1])]:
        sizerng = Region([0]*2, [sizepc]*2)
        regions = RegionSet.from_random(nregions, bounds, sizepc_range=sizerng, precision=1)
        self.regions[f'{nregions},{sizepc:.2f}'] = regions

  def run_evaluator(self, name: str, clazz: SweepTaskRunner):
    regions = self.regions[name]
    subscribers = [] #[RegionSweepDebug()]
    length, lvl = 0, 0
    levels, enumeration = {}, []
    evaluator = clazz.evaluate(regions, *subscribers)
    starttime = perf_counter()

    for _, (_, intersect) in enumerate(evaluator()):
      enumeration.append(intersect)

    endtime = perf_counter()
    elapsetime = endtime - starttime

    for i, intersect in enumerate(enumeration):
      enumeration[i] = tuple(sorted([r.id for r in intersect]))

      if lvl < len(intersect):
        lvl = len(intersect)
        levels[lvl] = 0

      self.assertEqual(len(intersect), lvl)

      levels[lvl] += 1
      length += 1

    with open(f'data/test_enumerate_results.txt', 'a') as output:
      text = f'{"%30s" % clazz.__name__}[{name}] [{elapsetime:.4f}s]: {(length, levels)}'
      output.write(f'{text}\n') #; print(text)
      #for intersect in enumeration:
      #  output.write(f'{[r[0:8] for r in intersect]}\n')

    return TestEnumerateResult(length, levels, enumeration)

  def test_enumerate_results(self):
    for name in self.regions.keys():
      nxg = self.run_evaluator(name, EnumerateByNxGSweepCtor)
      rcs = self.run_evaluator(name, EnumerateByRegionCycleSweep)

      self.assertEqual(nxg.length, rcs.length)
      self.assertDictEqual(nxg.levels, rcs.levels)

      for intersect in nxg.intersects:
        self.assertIn(intersect, rcs.intersects)
