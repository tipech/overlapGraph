#!/usr/bin/env python

"""
Multi-dimensional Sweep-line Algorithm for RegionSet (Non-threaded)

Implements a multi-dimensional sweep-line algorithm over a set of Regions.
Implements RegionMdSweep class that executes the specific details and actions
of the sweep-line algorithm over each dimension, when encountering: Init,
Begin, End or Done events. Adds and handles the Intersect event.

Classes:
- RegionMdSweep
"""

from typing import Iterator

from sources.abstract import Event
from sources.core import \
     Region, RegionEvent, RegionGrp, RegionPair, RegionSet, RegionTimeln

from .multidimensweep import MultidimenSweep
from .regionsweep import RegionSweep, RegionSweepEvtKind


class RegionMdSweep(RegionSweep, MultidimenSweep[RegionGrp]):
  """
  An multi-dimensional sweep-line algorithm over a set of Regions.
  This implementation is not parallelized; not threaded.

  Subscribes to and is evaluated by the multi-dimensional sweep-line
  algorithm along each dimension in the set of Regions.

  Extends:
    RegionSweep
    MultidimenSweep[RegionGrp]
  """

  def __init__(self, regions: RegionSet):
    """
    Initialize the sweep-line algorithm over Regions.

    Args:
      regions:
        The set of Regions to evaluate
        sweep-line algorithm over.
    """
    assert isinstance(regions, RegionSet)
    assert isinstance(regions.timeline, RegionTimeln)

    RegionSweep.__init__(self, regions)

  ### Methods: Evaluation

  def evaluate(self, *args, **kwargs):
    """
    Execute the multi-dimensional sweep-line algorithm
    over each dimension in the attached MdTimeline.
    Broadcast Events to the Observers.

    Overrides:
      RegionSweep.evaluate
      MultidimenSweep.evaluate

    Args:
      args, kwargs:
        Arguments for MultidimenSweep.evaluate.
    """
    MultidimenSweep.evaluate(self, *args, **kwargs)

  ### Methods: Broadcast

  def broadcast(self, event: Event[RegionGrp], **kwargs):
    """
    Broadcast the given event to subscribed Observers.

    Overrides:
      RegionSweep.broadcast

    Args:
      event:
        The Event to be broadcasted.
      kwargs:
        The parameters to be added or modified
        within the given Event.
    """
    dimension = kwargs.pop('dimension', self.dimension)

    RegionSweep.broadcast(self, event, dimension=dimension, **kwargs)

  ### Methods: Intersections

  def findintersects(self, region: Region) -> Iterator[RegionPair]:
    """
    Return an iterator over all the pairs between the given Region and
    the currently active Regions, as RegionPairs, regardless of overlaps.
    Unlike RegionSweep, this method does not check whether or not Region and
    the currently active Regions actually overlap. Assumes that check requires
    processing the other dimensions first.

    Args:
      region:   The Region to pairs with currently
                active Regions, as RegionPairs.

    Returns:
      An iterator over all the pairs between the Region and
      currently active Regions, regardless of overlaps.
    """
    for _, active in self.actives.items():
      assert active[self.dimension].lower <= region[self.dimension].lower
      yield (active, region)
