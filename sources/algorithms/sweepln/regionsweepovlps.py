#!/usr/bin/env python

"""
Compute Region Pairwise Overlaps by One-pass Sweep-line Algorithm

Implements the RegionSweepOverlaps class that computes a list of all of the
pairwise overlapping Regions using the one-pass sweep-line algorithm, through
a subscription to RegionSweep.

Classes:
- RegionSweepOverlaps
"""

from typing import List, Tuple

from sources.algorithms.sweepln.regionsweep import RegionSweepEvtKind
from sources.datastructs.abstract.pubsub import Event, Subscriber
from sources.datastructs.datasets.regiontime import RegionEvent
from sources.datastructs.shapes.region import Region, RegionGrp, RegionPair


class RegionSweepOverlaps(Subscriber[RegionGrp]):
  """
  Computes a list of all of the pairwise overlapping Regions
  using the one-pass sweep-line algorithm, through a subscription
  to RegionSweep.

  Extends:
    Subscriber[RegionGrp]

  Attributes:
    overlaps:
      The List of pairwise overlapping Regions.
  """
  overlaps: List[RegionPair]

  def __init__(self):
    """
    Initialize this class to compute a list of all of the pairwise
    overlapping Regions using the one-pass sweep-line algorithm.
    Sets the events as RegionSweepEvtKind.
    """
    Subscriber.__init__(self, RegionSweepEvtKind)

    self.overlaps = None

  ### Properties

  @property
  def results(self) -> List[RegionPair]:
    """
    The resulting List of pairwise overlapping Regions.
    Alias for: self.overlaps

    Returns:
      The resulting List of pairwise
      overlapping Regions.
    """
    return self.overlaps

  ### Methods: Event Handlers

  def on_init(self, event: RegionEvent):
    """
    Handle Event when sweep-line algorithm initializes.

    Args:
      event:
        The initialization Event.
    """
    assert event.kind == RegionSweepEvtKind.Init

    self.overlaps = []

  def on_intersect(self, event: Event[RegionPair]):
    """
    Handle Event when sweep-line algorithm encounters
    the two or more Regions intersecting.

    Args:
      event:
        The intersecting Regions Event.
    """
    assert event.kind == RegionSweepEvtKind.Intersect
    assert isinstance(event.context, Tuple) and len(event.context) == 2
    assert all([isinstance(r, Region) for r in event.context])

    self.overlaps.append(event.context)
