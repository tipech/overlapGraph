#!/usr/bin/env python

"""
Unit tests for Restricted Enumeration of Region Intersections

- test_rstdenumerate_subset_results
- test_rstdenumerate_neighbor_results
"""

from inspect import stack
from math import ceil
from time import perf_counter
from typing import Dict, Iterator, List, NamedTuple, Tuple, Union
from unittest import TestCase

from sources.algorithms import \
     NeighboredEnumByNxGraph, NeighboredEnumByRCSweep, \
     RegionIntersect, RegionSweepDebug, \
     SubsettedEnumByNxGraph, SubsettedEnumByRCSweep, SweepTaskRunner
from sources.datastructs import \
     Region, RegionIntxn, RegionSet


class TestRestrictedEnumerateResult(NamedTuple):
  length: int
  levels: Dict[int, int]
  intersects: List[Tuple[str]]


class TestRestrictedEnumerate(TestCase):

  regions: Dict[str, RegionSet]
  subsets: Dict[str, List[str]]

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
    self.subsets = {'definedset': {'G1': ['A', 'C', 'E', 'G'],
                                   'G2': ['B', 'D', 'F'],
                                   'G3': ['A', 'B', 'C', 'D']}}

    for nregions in [pow(10, n) for n in range(1, 4)]:
      for sizepc in [0.01, 0.05, 0.1]:
        name = f'{nregions},{sizepc:.2f}'
        sizepcr = Region([0]*2, [sizepc]*2)
        regions = RegionSet.from_random(nregions, bounds, sizepc=sizepcr, precision=1)

        self.regions[name] = regions
        self.subsets[name] = {}

        for subsetpc in [0.01, 0.05, 0.1, 0.15, 0.2]:
          size = round(subsetpc * len(regions))
          if 0 < size < len(regions):
            subname = f'{subsetpc:.2f}'
            shuffled = regions.shuffle()
            self.subsets[name][subname] = [r.id for i, r in enumerate(shuffled) if i < size]

  def run_evaluator(self, name: str, subname: str, 
                          context: Union[List[str],Region],
                          clazz: SweepTaskRunner):

    regions = self.regions[name]
    subscribers = [] #[RegionSweepDebug()]
    length, lvl = 0, 0
    levels, results = {}, []
    evaluator = clazz.evaluate(regions, context, *subscribers)
    starttime = perf_counter()

    for _, (_, intersect) in enumerate(evaluator()):
      results.append(intersect)

    endtime = perf_counter()
    elapsetime = endtime - starttime

    for i, intersect in enumerate(results):
      results[i] = tuple(sorted([r.id for r in intersect]))

      if lvl < len(intersect):
        lvl = len(intersect)
        levels[lvl] = 0

      self.assertEqual(len(intersect), lvl)

      levels[lvl] += 1
      length += 1

    with open(f'data/{stack()[1][3]}.txt', 'a') as output:
      text = f'{clazz.__name__}[{name},{subname}] [{elapsetime:.4f}s]: {(length, levels)}'
      output.write(f'{text}\n') #; print(text)
      #for intersect in results:
      #  output.write(f'{[r[0:8] for r in intersect]}\n')

    return TestRestrictedEnumerateResult(length, levels, results)

  def test_rstdenumerate_subset_results(self):

    for name in self.regions.keys():
      for s, subset in self.subsets[name].items():
        nxg = self.run_evaluator(name, s, subset, SubsettedEnumByNxGraph)
        rcs = self.run_evaluator(name, s, subset, SubsettedEnumByRCSweep)

        self.assertEqual(nxg.length, rcs.length)
        self.assertDictEqual(nxg.levels, rcs.levels)

        for intersect in nxg.intersects:
          self.assertIn(intersect, rcs.intersects)

  def test_rstdenumerate_neighbor_results(self):

    for name in self.regions.keys():
      shuffled = self.regions[name].shuffle()

      for region in shuffled[0:ceil(0.01 * len(shuffled))]:
        r = region.id
        nxg = self.run_evaluator(name, r, region, NeighboredEnumByNxGraph)
        rcs = self.run_evaluator(name, r, region, NeighboredEnumByRCSweep)

        self.assertEqual(nxg.length, rcs.length)
        self.assertDictEqual(nxg.levels, rcs.levels)

        for intersect in nxg.intersects:
          self.assertIn(intersect, rcs.intersects)
