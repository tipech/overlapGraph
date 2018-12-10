#!/usr/bin/env python

"""
tests/test_timeline.py - Unit tests for datastructs/timeline.py

This script implements the following tests:
  - test_timeline_event_create
  - test_timeline_ordering
"""

from unittest import TestCase

from ..datastructs.region import Region
from ..datastructs.regionset import RegionSet
from ..datastructs.timeline import Event, EventKind, Timeline


class TestRegionSet(TestCase):

  def test_timeline_event_create(self):
    self.assertEqual(EventKind.Begin, EventKind['Begin'])
    self.assertEqual(EventKind.End,   EventKind['End'])
    
    region = Region([0]*2, [1]*2)
    lower = [Event(EventKind.Begin, d.lower, region, i) for i, d in enumerate(region.dimensions)]
    upper = [Event(EventKind.End,   d.upper, region, i) for i, d in enumerate(region.dimensions)]

    self.assertTrue(all([EventKind.Begin == e.kind for e in lower]))
    self.assertTrue(all([EventKind.End   == e.kind for e in upper]))
    self.assertTrue(all([e.when == region[i].lower for i, e in enumerate(lower)]))
    self.assertTrue(all([e.when == region[i].upper for i, e in enumerate(upper)]))
    self.assertTrue(all([e.context is region for e in upper + lower]))

  def test_timeline_ordering(self):
    regions = RegionSet(dimension=2)
    regions.add(Region([0, 0], [3, 5], 'A'))
    regions.add(Region([3, 1], [5, 5], 'B'))
    regions.add(Region([2, 5], [6, 5], 'C'))
    oracle = [
      [("Begin", 0, regions[0]), ("Begin", 2, regions[2]),
       ("End"  , 3, regions[0]), ("Begin", 3, regions[1]),
       ("End"  , 5, regions[1]), ("End"  , 6, regions[2])],
      [("Begin", 0, regions[0]), ("Begin", 1, regions[1]),
       ("End"  , 5, regions[0]), ("End"  , 5, regions[1]),
       ("Begin", 5, regions[2]), ("End"  , 5, regions[2])]
    ]

    self.assertEqual(regions.timeline, regions.timeline)
    for d in range(regions.dimension):
      for i, event in enumerate(regions.timeline[d]):
        #print(f'{d},{i}: {event}')
        self.assertEqual(event.kind, EventKind[oracle[d][i][0]])
        self.assertEqual(event.when, float(oracle[d][i][1]))
        self.assertIs(event.context, oracle[d][i][2])
