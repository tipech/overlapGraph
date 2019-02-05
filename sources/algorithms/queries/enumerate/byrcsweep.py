#!/usr/bin/env python

"""
Enumeration of all Intersecting Regions with Cyclic
Multi-pass Sweep-line Algorithm

Implements the enumeration of all intersecting Regions within a RegionSet via
a subscription to RegionCycleSweep. The enumeration outputs an Iterator of the
intersecting Regions as tuple of Region intersection and RegionIntns in order
of the number of intersecting Regions and the position of the last intersecting
Region's Begin Event.

Classes:
- EnumerateByRCSweep
"""

from typing import Any, Callable, Iterable, Iterator, List, Tuple

from sources.abstract import Event, Subscriber
from sources.algorithms import \
     RegionCycleSweep, RegionSweepEvtKind, SweepTaskRunner
from sources.core import \
     Region, RegionEvent, RegionGrp, RegionIntxn, RegionPair, RegionSet

from .common import EnumerateRegionIntersect, RegionIntersect


class EnumerateByRCSweep(EnumerateRegionIntersect):
  """
  Enumeration of all intersecting Regions by Cyclic Multi-pass
  Sweep-line Algorithm

  Computes an Iterator of all of the intersecting Regions using the 
  cyclic multi-pass sweep-line algorithm, through a subscription
  to RegionCycleSweep.

  Extends:
    SweepTaskRunner[RegionGrp, Iterator[RegionIntersect]]

  Attributes:
    intersects:
      The List of intersecting Regions.
  """
  intersects: List[RegionIntersect]

  def __init__(self):
    """
    Initialize this class to compute a list of all of the intersecting
    Regions using the cyclic multi-pass sweep-line algorithm.
    Sets the events as RegionSweepEvtKind.
    """
    Subscriber.__init__(self, RegionSweepEvtKind)

    self.intersects = []

  ### Properties

  @property
  def results(self) -> Iterator[RegionIntersect]:
    """
    The resulting Iterator of intersecting Regions as tuple of
    Region intersection and RegionIntns.

    Returns:
      The resulting Iterator of intersecting Regions as
      tuple of Region intersection and RegionIntns.
    """
    yield from self.compute()

  ### Methods: Computations

  def compute(self) -> Iterator[RegionIntersect]:
    """
    The resulting Iterator of intersecting Regions as tuple of
    Region intersection and RegionIntns.

    Returns:
      The resulting Iterator of intersecting Regions as
      tuple of Region intersection and RegionIntns.
    """
    return iter(self.intersects)

  ### Methods: Event Handlers

  def on_intersect(self, event: Event[RegionPair]):
    """
    Handle Event when sweep-line algorithm encounters
    the two or more Regions intersecting.

    Args:
      event:
        The intersecting Regions Event.

    Event should have addition attributes:
    - iteration:  The current iteration of algorithm
    - intersect:  The Region intersection
    - aggregate:  The list of Regions intersecting.
    - levels:     The list of list of level-wise,
                  intersecting Region found by the
                  algorithm thus far.
    """
    assert event.kind == RegionSweepEvtKind.Intersect

    def check_event_attrs(intersect, aggregate):
      assert isinstance(intersect, Region) and isinstance(aggregate, List)
      assert 'intersect' in intersect and intersect['intersect'] is aggregate
      return intersect, aggregate

    def check_event_context(context):
      assert isinstance(context, Tuple) and len(context) == 2
      assert all([isinstance(r, Region) for r in context])
      assert Region.overlaps(*context)
      return context

    if hasattr(event, 'intersect') and hasattr(event, 'aggregate'):
      region, intersect = check_event_attrs(event.intersect, event.aggregate)
    else:
      a, b = check_event_context(event.context)
      region = a.intersect(b, 'aggregate')
      intersect = region['intersect']

    self.intersects.append((region, intersect))

  ### Class Methods: Evaluation

  @classmethod
  def prepare(cls, regions: RegionSet,
                   *subscribers: Iterable[Subscriber[RegionGrp]]) \
                   -> Callable[[Any], Iterator[RegionIntersect]]:
    """
    Factory function for computes an Iterator of all of the intersecting
    Regions using the cyclic multi-pass sweep-line algorithm.

    Overrides:
      SweepTaskRunner.prepare

    Args:
      regions:
        The set of Regions to compute the Iterator
        of the intersecting Regions from.
      subscribers:
        The other Subscribers to observe the cyclic
        multi-pass sweep-line algorithm.

    Returns:
      A function to evaluate the cyclic multi-pass
      sweep-line algorithm and compute the Iterator of the
      intersecting Regions.

      Args:
        args, kwargs:
          Arguments for alg.evaluate()

      Returns:
        The resulting Iterator of intersecting Regions.
    """
    assert isinstance(regions, RegionSet)
    return SweepTaskRunner.prepare(cls, RegionCycleSweep, **{
      'subscribers': subscribers,
      'alg_args': [regions]
    })
