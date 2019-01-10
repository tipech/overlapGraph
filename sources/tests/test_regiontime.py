#!/usr/bin/env python

"""
Unit tests for Event Timeline for Region Sets

This script implements the following tests:
  - test_regiontimeln_event_create
  - test_regiontimeln_ordering
"""

from unittest import TestCase

from sources.datastructs.datasets.regionset import RegionSet
from sources.datastructs.datasets.regiontime import RegionEvent, RegionEvtKind
from sources.datastructs.shapes.region import Region


class TestRegionTimeln(TestCase):

  def test_regiontimeln_event_create(self):
    self.assertEqual(RegionEvtKind.Begin, RegionEvtKind['Begin'])
    self.assertEqual(RegionEvtKind.End,   RegionEvtKind['End'])
    
    region = Region([0]*2, [1]*2)
    lower = [RegionEvent(RegionEvtKind.Begin, region, i) for i in range(region.dimension)]
    upper = [RegionEvent(RegionEvtKind.End,   region, i) for i in range(region.dimension)]

    self.assertTrue(all([RegionEvtKind.Begin == e.kind for e in lower]))
    self.assertTrue(all([RegionEvtKind.End   == e.kind for e in upper]))
    self.assertTrue(all([e.when == region[i].lower for i, e in enumerate(lower)]))
    self.assertTrue(all([e.when == region[i].upper for i, e in enumerate(upper)]))
    self.assertTrue(all([e.context is region for e in upper + lower]))

  def test_regiontimeln_ordering(self):
    regions = RegionSet(dimension=2)
    regions.add(Region([0, 0], [3, 5], 'A'))
    regions.add(Region([3, 1], [5, 5], 'B'))
    regions.add(Region([2, 5], [6, 5], 'C'))
    bbox = regions.bbox
    oracle = [
      [("Init" , 0, bbox),
       ("Begin", 0, regions[0]), ("Begin", 2, regions[2]),
       ("End"  , 3, regions[0]), ("Begin", 3, regions[1]),
       ("End"  , 5, regions[1]), ("End"  , 6, regions[2]),
       ("Done" , 6, bbox)],
      [("Init" , 0, bbox),
       ("Begin", 0, regions[0]), ("Begin", 1, regions[1]),
       ("End"  , 5, regions[0]), ("End"  , 5, regions[1]),
       ("Begin", 5, regions[2]), ("End"  , 5, regions[2]),
       ("Done" , 5, bbox)]
    ]

    for d in range(regions.dimension):
      for i, event in enumerate(regions.timeline.events(d)):
        #print(f'{d},{i}: {event}')
        self.assertEqual(event.kind, RegionEvtKind[oracle[d][i][0]])
        self.assertEqual(event.when, float(oracle[d][i][1]))
        if event.kind == RegionEvtKind.Begin or event.kind == RegionEvtKind.End:
          self.assertIs(event.context, oracle[d][i][2])
          self.assertTrue(-1 <= event.order <= 1)
        elif event.kind == RegionEvtKind.Init:
          self.assertEqual(i, 0)
          self.assertEqual(event.order, -2)
        else:
          self.assertEqual(event.order, 2)
