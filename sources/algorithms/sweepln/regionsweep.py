#!/usr/bin/env python

"""
One-Pass Sweep-line Algorithm for RegionSet

This script implements an one-pass sweep-line algorithm over a set of Regions.
Implements RegionSweep class that executes the specific details and actions of
the sweep-line algorithm, when encountering: Init, Begin, End or Done events.

Classes:
- RegionSweepEvtKind
- RegionSweep
"""

from enum import IntEnum, auto, unique
from typing import Dict, Iterator, List

from rx import Observer
from rx.subjects import Subject

from sources.algorithms.sweepln.onesweep import OneSweep
from sources.datastructs.abstract.pubsub import Event, Publisher
from sources.datastructs.datasets.regionset import RegionSet
from sources.datastructs.datasets.regiontime import RegionEvent, RegionEvtKind
from sources.datastructs.shapes.region import Region, RegionGrp, RegionPair


@unique
class RegionSweepEvtKind(IntEnum):
  """
  Extended RegionEvtKind enumerator.
  Enumeration of allowed event `kind` values. The values denote the beginning
  and ending event of an Region's interval in a particular dimension.

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
  Class for implementing an one-pass sweep-line algorithm over a set of
  Regions. Subscribes to and is evaluated by the one-pass sweep-line algorithm
  along a dimension on the set of Regions.

  Attributes:
    regions:    The RegionSet to evaluate sweep-line over.
    dimension:  The dimension to evaluate sweep-line over.
    actives:    The active Regions during sweep-line.
    bbuffer:    The broadcast buffer to ensure correct,
                broadcast ordering.

  Properties:
    is_active:  Boolean flag for whether or not if the
                sweep-line algorithm is initialized.

  Methods:
    Special:  __init__
    Instance: broadcast, findintersects, on_init,
              on_begin, on_intersect, on_end, on_done

  Inherited from OneSweep:
    Attributes:
      subject:
        The Subject for Observers to subscribe to.
      presubj:
        The Subject for Observers to subscribe to, whose
        on_next are always called before, self.on_next
        and the subjects' on_next.
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
      timeline:
        The Timeline to evaluate the algorithm over.

    Methods:
      Special:  __init__, __call__
      Instance: subscribe, broadcast, evaluate,
                on_next, on_completed, on_error

    Overridden Methods:
      Special:  __init__, broadcast
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
    Determine whether or not if the sweep-line algorithm is initialized.

    Returns:
      True:   If the algorithm is initialized
      False:  Otherwise.
    """
    return isinstance(self.dimension, int) and self.dimension >= 0

  ### Methods: Broadcast

  def broadcast(self, event: Event[RegionGrp], **kwargs):
    """
    Broadcast the given event to subscribed Observers.

    Args:
      event:
        The Event to be broadcasted.
      kwargs:
        The parameters to be added or modified
        within the given Event.
    """
    kwargs = {
      'depth': len(self.actives) if self.actives else 0,
      'actives': list(self.actives.keys()),
      **kwargs
    }

    OneSweep.broadcast(self, event, **kwargs)

    for buffered_events in self.bbuffer:
      OneSweep.broadcast(self, buffered_events, **kwargs)

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
