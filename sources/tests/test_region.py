#!/usr/bin/env python

"""
Unit tests for Region Data Class

- test_create_region
- test_region_dimension_mismatch
- test_region_properties
- test_region_getsetitem
- test_region_contains
- test_region_equality
- test_region_overlaps
- test_region_intersect
- test_region_union
- test_region_linked_intersect
- test_region_linked_union
- test_region_project
- test_region_random_points
- test_region_random_regions
- test_region_from_intervals
- test_region_from_interval
- test_region_from_intersect
- test_region_from_union
- test_region_from_dict
- test_region_from_object
- test_region_from_text
"""

from dataclasses import asdict, astuple
from functools import reduce
from typing import List, Tuple
from unittest import TestCase

from numpy import mean

from sources.datastructs.shapes.interval import Interval
from sources.datastructs.shapes.region import Region


class TestRegion(TestCase):

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
    test_regions.append(Region([0, 5, 0], [5, 0, 5]))

    for i, region in enumerate(test_regions):
      #print(region)
      self.assertEqual(region.dimension, i + 1)
      self.assertEqual(region.dimension, len(region.dimensions))
      self.assertEqual(region.dimension, len(region.lower))
      self.assertEqual(region.dimension, len(region.upper))
      self.assertTrue(all([d == Interval(0,5) for d in region.dimensions]))
      self.assertTrue(all([d == 0 for d in region.lower]))
      self.assertTrue(all([d == 5 for d in region.upper]))
      self.assertTrue(all([region.lower[i] <= region.upper[i] for i in range(region.dimension)]))
      self.assertTrue(all([region.lower[i] == region[i].lower for i in range(region.dimension)]))
      self.assertTrue(all([region.upper[i] == region[i].upper for i in range(region.dimension)]))

  def test_region_dimension_mismatch(self):
    with self.assertRaises(AssertionError):
      Region([0, 0], [10, 10], dimension=3)
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

  def test_region_getsetitem(self):
    data = {'data': 'value', 'datalist': ['list', 'of', 'items'], 'dataprop': 'dataprop'}
    intervals = [Interval(0, 10)]*3
    region = Region.from_intervals(intervals, dataprop=data['dataprop'])

    def check_region(region: Region, intervals: List[Interval]):
      self.assertTrue(all([region[i] == interval for i, interval in enumerate(intervals)]))
      self.assertEqual(list(map(lambda i: i.lower, intervals)), region.lower)
      self.assertEqual(list(map(lambda i: i.upper, intervals)), region.upper)

    check_region(region, intervals)
    #print(f'{region}')
    #print(f'{region.data}')
    #print(f'{asdict(region)}')
    intervals = [Interval(interval.lower, interval.upper + i) for i, interval in enumerate(intervals)]
    for i, interval in enumerate(intervals): region[i] = interval
    check_region(region, intervals)

    region['data'] = data['data']
    region['datalist'] = data['datalist']
    #print(f'{region}')
    #print(f'{region.data}')
    #print(f'{asdict(region)}')
    self.assertEqual(data['data'], region['data'])
    self.assertEqual(data['datalist'], region['datalist'])
    self.assertEqual(data['dataprop'], region['dataprop'])
    self.assertDictEqual(data, region.data)

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
    self.assertFalse(region.contains(region.lower, inc_lower=False))
    self.assertFalse(region.contains(region.upper, inc_upper=False))
    self.assertFalse([v - 0.1 for v in region.lower] in region)
    self.assertFalse([v + 0.1 for v in region.upper] in region)
    self.assertFalse([region.lower[0] - 0.1, region.lower[1]]       in region)
    self.assertFalse([region.lower[0]      , region.lower[1] - 0.1] in region)
    self.assertFalse([region.upper[0] + 0.1, region.upper[1]]       in region)
    self.assertFalse([region.upper[0]      , region.upper[1] + 0.1] in region)

  def test_region_encloses(self):
    region = Region([-5, 5], [0, 10])
    test_regions = []
    test_regions.append(Region([-5, 5], [0, 10]))
    test_regions.append(Region([-6, 4], [1, 11]))
    test_regions.append(Region([-4, 6], [-1, 9]))
    test_regions.append(Region([-4, 6], [1, 9]))
    test_regions.append(Region([-6, 5], [0, 10]))
    test_regions.append(Region([-2, 7], [-2, 7]))

    for subregion in test_regions:
      comparsion = all([region.lower[i] <= subregion.lower[i] <= subregion.upper[i] <= region.upper[i] for i in
                        range(region.dimension)])
      #print(f'{subregion} in\n{region}:')
      #print(f'  expect={comparsion}')
      #print(f'  actual={subregion in region}')
      self.assertEqual(subregion in region, comparsion)

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

  def test_region_intersect(self):
    for i, first in enumerate(self.test_regions):
      for j, second in enumerate(self.test_regions):
        intersect = first.intersect(second)
        if self.overlaps[i][j]:
          #print(f'{first}\n{second}:')
          #print(f'  actual={intersect}')
          #print(f'  size={intersect.size}')
          for x, d in enumerate(first.dimensions):
            self.assertEqual(d.intersect(second.dimensions[x]),
                             intersect.dimensions[x])
        else:
          #print(f'{first}\n{second}:')
          #print(f'  expect=None')
          #print(f'  actual={intersect}')
          self.assertEqual(intersect, None)

  def test_region_union(self):
    for first in self.test_regions:
      for second in self.test_regions:
        union = first.union(second)
        #print(f'{first},\n{second}:')
        #print(f'  union={union}')
        #print(f'  lengths={union.lengths}')
        #print(f'  size={union.size}')
        self.assertTrue(first in union)
        self.assertTrue(second in union)

  def test_region_linked_intersect(self):
    base_region = Region([0]*2, [10]*2)
    regions = [Region([0]*2, [i]*2) for i in range(5, 1, -1)]
    ref_region = base_region
    agg_region = base_region
    agg_regions = [base_region]

    for region in regions:
      old_region = ref_region
      agg_regions.append(region)
      ref_region = ref_region.intersect(region, 'reference')
      agg_region = agg_region.intersect(region, 'aggregate')
      #print(f'{asdict(ref_region)}')
      #print(f'{asdict(agg_region)}')
      self.assertListEqual([old_region, region], ref_region['intersect'])
      self.assertListEqual(agg_regions, agg_region['intersect'])

  def test_region_linked_union(self):
    base_region = Region([0]*2, [1]*2)
    regions = [Region([0, i], [1, i + 1]) for i in range(1, 5)]
    ref_region = base_region
    agg_region = base_region
    agg_regions = [base_region]

    for region in regions:
      old_region = ref_region
      agg_regions.append(region)
      ref_region = ref_region.union(region, 'reference')
      agg_region = agg_region.union(region, 'aggregate')
      #print(f'{asdict(ref_region)}')
      #print(f'{asdict(agg_region)}')
      self.assertListEqual([old_region, region], ref_region['union'])
      self.assertListEqual(agg_regions, agg_region['union'])

  def test_region_project(self):
    dimlimit = 7
    test_interval = Interval(1, 5)
    region = Region([-5, 5, 0], [15, 10, 50])
    for d in range(1, dimlimit):
      new_region = region.project(d, test_interval)
      #print(f'{new_region}')
      self.assertEqual(new_region.dimension, d)
      for i in range(0, d):
        interval = region[i] if i < region.dimension else test_interval
        self.assertEqual(new_region[i], interval)

  def test_region_random_points(self):
    region2d = Region([-5, 0], [15, 10])
    region3d = Region([-5, 0, 0], [15, 10, 50])
    points2d = region2d.random_points(5)
    points3d = region3d.random_points(5)
    #print(f'{region2d}: random={points2d}')
    #print(f'{region3d}: random={points3d}')
    for point in points2d:
      self.assertTrue(region2d.contains(list(point), inc_upper=False))
    for point in points3d:
      self.assertTrue(region3d.contains(list(point), inc_upper=False))

  def test_region_random_regions(self):
    region = Region([-5, 0], [15, 10])
    randoms  = region.random_regions(5, Region([0.25, 0.25], [0.75, 0.75]))
    randoms += region.random_regions(5, Region([0.25, 0.25], [0.75, 0.75]), precision = 0)
    #print(f'{region}:')
    for subregion in randoms:
      #print(f'- {subregion}')
      self.assertTrue(subregion in region)

  def test_region_from_intervals(self):
    ndimens = 5
    base_interval = Interval(1, 5)
    intervals = [Interval(base_interval.lower + d,
                          base_interval.upper + d) for d in range(ndimens)]
    region = Region.from_intervals(intervals)
    #print(f'{region}')
    self.assertEqual(region.dimension, ndimens)
    self.assertEqual(region.lower, [base_interval.lower + d for d in range(ndimens)])
    self.assertEqual(region.upper, [base_interval.upper + d for d in range(ndimens)])
    for d, dimension in enumerate(region.dimensions):
      self.assertEqual(dimension, intervals[d])

  def test_region_from_interval(self):
    ndimens = 5
    interval = Interval(-5, 5)
    for d in range(1, ndimens):
      region = Region.from_interval(interval, d)
      #print(f'{region}')
      self.assertEqual(region.dimension, d)
      for dimen in region.dimensions:
        self.assertEqual(dimen, interval)

  def test_region_from_intersect(self):
    regions = [Region([-i]*2, [i]*2) for i in range(5, 1, -1)]
    for i in range(1, len(regions)):
      expected_intersect = reduce(lambda a, b: a.intersect(b, 'aggregate'), regions[0:i+1])
      intersect = Region.from_intersect(regions[0:i+1], True)
      #print(f'Expected: {expected_intersect}')
      #print(f'Expected["intersect"]: {expected_intersect["intersect"]}')
      #print(f'Actual: {intersect}')
      #print(f'Actual["intersect"]: {intersect["intersect"]}')
      self.assertEqual(regions[i], intersect)
      self.assertListEqual(regions[0:i+1], intersect['intersect'])
      self.assertEqual(expected_intersect, intersect)
      self.assertListEqual(expected_intersect['intersect'], intersect['intersect'])

  def test_region_from_union(self):
    region = Region([0]*2, [100]*2)
    regions = region.random_regions(5, Region([0.1]*2, [0.25]*2), precision = 0)
    expected_union = reduce(lambda a, b: a.union(b, 'aggregate'), regions)
    union = Region.from_union(regions, True)
    #print(f'Expected: {expected_union}')
    #print(f'Actual: {union}')
    #print(f'Expected["union"]: {expected_union["union"]}')
    #print(f'Actual["union"]: {union["union"]}')
    self.assertEqual(expected_union, union)
    self.assertListEqual(expected_union['union'], union['union'])
    self.assertTrue(all([union.encloses(r) for r in regions]))
    self.assertTrue(region.encloses(union))

  def test_region_from_dict(self):
    test_region = Region([10]*3, [50]*3)
    objects = []
    objects.append({"lower": [10]*3, "upper": [50]*3})
    objects.append({"dimension": 3, "lower": 10, "upper": [50]*3})
    objects.append({"dimension": 3, "lower": 10, "upper": 50})
    objects.append({"dimension": 3, "lower": [10]*3, "upper": 50})
    objects.append({"dimension": 3, "interval": [10, 50]})
    objects.append({"dimension": 3, "interval": (10, 50)})
    objects.append({"dimension": 3, "interval": {"lower": 10, "upper": 50}})
    objects.append({"dimensions": [[10, 50]]*3})
    objects.append({"dimensions": [(10, 50)]*3})
    objects.append({"dimensions": [{"lower": 10, "upper": 50}]*3})

    for object in objects:
      #print(f'{object}')
      self.assertEqual(test_region, Region.from_dict(object))

  def test_region_from_object(self):
    test_region = Region([10]*3, [50]*3)
    objects = []
    objects.append({"lower": [10]*3, "upper": [50]*3})
    objects.append({"dimension": 3, "lower": 10, "upper": [50]*3})
    objects.append({"dimension": 3, "lower": 10, "upper": 50})
    objects.append({"dimension": 3, "lower": [10]*3, "upper": 50})
    objects.append({"dimension": 3, "interval": [10, 50]})
    objects.append({"dimension": 3, "interval": (10, 50)})
    objects.append({"dimension": 3, "interval": {"lower": 10, "upper": 50}})
    objects.append({"dimensions": [[10, 50]]*3})
    objects.append({"dimensions": [(10, 50)]*3})
    objects.append({"dimensions": [{"lower": 10, "upper": 50}]*3})
    objects.append([[10, 50]]*3)
    objects.append([(10, 50)]*3)
    objects.append([{"lower": 10, "upper": 50}]*3)
    objects.append((3, [10, 50]))
    objects.append((3, (10, 50)))
    objects.append((3, {"lower": 10, "upper": 50}))

    for object in objects:
      #print(f'{object}')
      self.assertEqual(test_region, Region.from_object(object))

  def test_region_from_text(self):
    test_region = Region([10]*3, [50]*3)
    texts = []
    texts.append(('{"lower": [10,10,10], "upper": [50,50,50]}', 'json'))
    texts.append(('{"dimension": 3, "lower": 10, "upper": 50}', 'literal'))
    texts.append(('{"dimension": 3, "lower": 10, "upper": 50}', 'json'))
    texts.append(('{"dimension": 3, "interval": [10, 50]}', 'json'))
    texts.append(('{"dimension": 3, "interval": [10, 50]}', 'literal'))
    texts.append(('{"dimension": 3, "interval": (10, 50)}', 'literal'))
    texts.append(('[[10, 50],[10, 50],[10, 50]]', 'json'))
    texts.append(('[[10, 50],[10, 50],[10, 50]]', 'literal'))
    texts.append(('[(10, 50),(10, 50),(10, 50)]', 'literal'))
    texts.append(('[{"lower": 10, "upper": 50},{"lower": 10, "upper": 50},{"lower": 10, "upper": 50}]', 'json'))
    texts.append(('[{"lower": 10, "upper": 50},{"lower": 10, "upper": 50},{"lower": 10, "upper": 50}]', 'literal'))
    texts.append(('(3, [10, 50])', 'literal'))
    texts.append(('(3, (10, 50))', 'literal'))

    for text in texts:
      #print(f'text="{text[0]}"' if "'" in text else f"text='{text[0]}'")
      #print(f'format={text[1]}')
      self.assertEqual(test_region, Region.from_text(*text))
