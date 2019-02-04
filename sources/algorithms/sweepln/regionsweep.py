#!/usr/bin/env python

"""
One-Pass Sweep-line Algorithm for RegionSet

Implements an one-pass sweep-line algorithm over a set of Regions.
Implements RegionSweep class that executes the specific details and actions of
the sweep-line algorithm, when encountering: Init, Begin, End or Done events.
Adds and handles the Intersect event.

Classes:
- RegionSweepEvtKind
- RegionSweep
"""

from enum import IntEnum, auto, unique
from typing import Dict, Iterator, List

from sources.abstract import Event, Publisher
from sources.core import \
     Region, RegionEvent, RegionEvtKind, RegionGrp, RegionPair, RegionSet

from .onesweep import OneSweep


@unique
class RegionSweepEvtKind(IntEnum):
  """
  Extended RegionEvtKind enumerator.

  Enumeration of allowed event `kind` values. The values denote the beginning
  and ending event of an Region's interval in a particular dimension.

  Extends:
    IntEnum

  Values:
    Init:       At the beginning of a sweep-line pass.
    Begin:      At the beginning of a Region.
    End:        At the ending of a Region.
    Done:       At the ending of a sweep-line pass.
    Intersect:  When two or more Regions intersect.
  """
  Init      = RegionEvtKind.Init.value
  Begin     = RegionEvtKind.Begin.value
  End       = RegionEvtKind.End.value
  Done      = RegionEvtKind.Done.value
  Intersect = auto()


class RegionSweep(OneSweep[RegionGrp]):
  """
  An one-pass sweep-line algorithm over a set of Regions.

  Subscribes to and is evaluated by the one-pass sweep-line algorithm
  along a dimension on the set of Regions.

  Extends:
    OneSweep[RegionGrp]

  Attributes:
    regions:    The RegionSet to evaluate sweep-line over.
    dimension:  The dimension to evaluate sweep-line over.
    actives:    The active Regions during sweep-line.
    bbuffer:    The broadcast buffer to ensure correct,
                broadcast ordering.
  """
  regions:    RegionSet
  dimension:  int
  actives:    Dict[str, Region]
  bbuffer:    List[Event[RegionGrp]]

  def __init__(self, regions: RegionSet):
    """
    Initialize the sweep-line algorithm over Regions.

    Args:
      regions:
        The set of Regions to evaluate
        sweep-line algorithm over.
    """
    OneSweep.__init__(self, regions.timeline, RegionSweepEvtKind)

    self.regions = regions
    self.dimension = None
    self.actives = None
    self.bbuffer = []
    self.subscribe(self)

  ### Properties

  @property
  def is_active(self) -> bool:
    """
    Determine whether or not the sweep-line algorithm is initialized.

    Returns:
      True:   If the algorithm is initialized
      False:  Otherwise.
    """
    return isinstance(self.dimension, int) and self.dimension >= 0

  ### Methods: Broadcast

  def broadcast(self, event: Event[RegionGrp], **kwargs):
    """
    Broadcast the given event to subscribed Observers.

    Overrides:
      Publisher.broadcast

    Args:
      event:
        The Event to be broadcasted.
      kwargs:
        The parameters to be added or modified
        within the given Event.
    """
    kwargs = {
      'depth': len(self.actives) if self.actives else 0,
      'actives': self.actives,
      **kwargs
    }

    Publisher.broadcast(self, event, **kwargs)

    for buffered_event in self.bbuffer:
      Publisher.broadcast(self, buffered_event, **kwargs)

    if len(self.bbuffer) > 0:
      self.bbuffer = []

  ### Methods: Intersections

  def findintersects(self, region: Region) -> Iterator[RegionPair]:
    """
    Return an iterator over all the pairs of overlaps between the
    given Region and the currently active Regions, as RegionPairs.

    Args:
      region:   The Region to find pairs of overlaps with
                currently active Regions, as RegionPairs.

    Returns:
      An iterator over all the pairs of overlaps between
      the Region and currently active Regions.
    """
    for _, active in self.actives.items():
      assert active[self.dimension].lower <= region[self.dimension].lower
      if region.overlaps(active):
        yield (active, region)

  ### Methods: Event Handlers

  def on_init(self, event: RegionEvent):
    """
    Handle Event when sweep-line algorithm initializes.

    Args:
      event:
        The initialization Event.
    """
    assert not self.is_active
    assert event.kind == RegionSweepEvtKind.Init
    assert 0 <= event.dimension < self.regions.dimension

    self.dimension = event.dimension
    self.actives = {}

  def on_begin(self, event: RegionEvent):
    """
    Handle Event when sweep-line algorithm encounters
    the beginning of a Region.

    Args:
      event:
        The Region beginning Event.
    """
    assert self.is_active
    assert event.kind == RegionSweepEvtKind.Begin
    assert event.context.id not in self.actives

    region = event.context

    for a, b in self.findintersects(region):
      self.on_intersect(Event(RegionSweepEvtKind.Intersect, (a, b)))

    self.actives[region.id] = region

  def on_intersect(self, event: Event[RegionPair]):
    """
    Handle Event when sweep-line algorithm encounters the two or
    more Regions intersecting. Buffers Events for broadcasting.

    Args:
      event:
        The intersecting Regions Event.
    """
    assert self.is_active
    assert event.kind == RegionSweepEvtKind.Intersect

    self.bbuffer.append(event)

  def on_end(self, event: RegionEvent):
    """
    Handle Event when sweep-line algorithm encounters
    the ending of a Region.

    Args:
      event:
        The Region ending Event.
    """
    assert self.is_active
    assert event.kind == RegionSweepEvtKind.End
    assert event.context.id in self.actives

    region = event.context

    del self.actives[region.id]

  def on_done(self, event: RegionEvent):
    """
    Handle Event when sweep-line algorithm completes.

    Args:
      event:
        The completion Event.
    """
    assert self.is_active
    assert event.kind == RegionSweepEvtKind.Done
    assert len(self.actives) == 0

    self.dimension = None
