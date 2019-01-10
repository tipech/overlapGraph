#!/usr/bin/env python

"""
Compute Region Pairwise Overlaps by One-pass Sweep-line Algorithm

This script implements the RegionSweepOverlaps class that computes a list of
all of the pairwise overlapping Regions using the one-pass sweep-line
algorithm, through a subscription to RegionSweep.

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
  Class that computes a list of all of the pairwise overlapping Regions 
  using the one-pass sweep-line algorithm, through a subscription 
  to RegionSweep.

  Attributes:
    overlaps:
      The List of pairwise overlapping Regions.

  Properties:
    results:
      The resulting List of pairwise overlapping Regions.

  Methods:
    Special:  __init__
    Instance: on_init, on_intersect

  Inherited from Subscriber:
    Attributes:
      events:
        The registered Event types (kind).
        If None, no register Event types.
      eventmapper:
        A lambda method that maps each Event to a method
        name for a specific event handler.
      strict:
        Boolean flag whether or not to raise an exception
        when Event handler not found. True, raises
        exception; False, otherwise. Default: False.

    Methods:
      Special:  __init__
      Instance: on_next, on_completed, on_error

    Overridden Methods:
      Special:  __init__
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
