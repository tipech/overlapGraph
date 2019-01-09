#!/usr/bin/env python

"""
Event Timeline for Region Sets

This script implements the RegionTimeln class along with its helper
classes RegionEvtKind and RegionEvent. The RegionTimeln class generates a
sorted iteration of events for each dimension in the Regions, each Region
results in a beginning and an ending event.

Classes:
- RegionEvtKind   (IntEnum)
- RegionEvent     (MdTEvent)
- RegionTimeln    (MdTimeline)
"""

from dataclasses import dataclass, field
from enum import IntEnum
from functools import total_ordering
from typing import Iterator, List, Union

from sortedcontainers import SortedList

from sources.datastructs.abstract.mdtimeln import MdTEvent, MdTimeline
from sources.datastructs.abstract.timeline import Timeline
from sources.datastructs.shapes.region import Region

try: # cyclic codependency
  from sources.datastructs.datasets.regionset import RegionSet
except ImportError:
  pass


class RegionEvtKind(IntEnum):
  """
  Enumeration of allowed event `kind` values. The values denote the beginning
  and ending event of an Region's interval in a particular dimension.

  Values:
    Init:   Flag at the beginning of a sweep-line pass.
    Begin:  Flag for the beginning of a Region.
    End:    Flag for the ending of a Region.
    Done:   Flag at the ending of a sweep-line pass.
  """
  Init  = 0
  Begin = 1
  End   = 2
  Done  = 3


@dataclass
@total_ordering
class RegionEvent(MdTEvent[Region]):
  """
  Data class for an event. Each event has a value for when the event occurs,
  a specified event type, the Region context associated with the event, and
  dimension along which the event occurs. Events are ordered by when the event
  occurs, the kind of event and if the Region is zero-length or non-zero length
  along the timeline dimension.

  Attributes:
    when:       The value (time) along the sorted
                dimension, where this event takes place.
    kind:       The type of event: Begin or End of Region.
    context:    The Region associated with this event.
    dimension:  The dimension along which events occur.
    order:      The sort priority of the events with the
                same 'when', occurs at the same time.

  Methods:
    Special:    __init__, __eq__, __lt__

  Inherited from MdTEvent:
    Attributes:
      when:       The value (time) along the sorted
                  timeline, where this event takes place.
      context:    The object associated with this event.
      dimension:  The dimension along which events occur.
    Overridden Attributes:
      kind:       The type of event.

    Methods:
      Instance:   setparams
    Overridden Methods:
      Special:    __eq__, __lt__
  """
  kind:   RegionEvtKind
  order:  int

  def __init__(self, kind: Union[RegionEvtKind, str], when: float,
                     context: Region, dimension: int = 0):
    """
    Initialize a new RegionEvent with the specified kind, when, context & 
    dimension. The kind of event can be the RegionEvtKind enum value or
    the string name equivalent.

    Args:
      kind:       The type of event: Begin or End of Region.
      when:       The value/time along the sorted dimension
                  where this event takes place.
      context:    The Region associated with this event.
      dimension:  The dimension along which events occur.
    """
    if isinstance(kind, str):
      kind = RegionEvtKind[kind]

    assert isinstance(kind, RegionEvtKind)
    assert 0 <= dimension < context.dimension

    self.kind = kind
    self.when = when
    self.context = context
    self.dimension = dimension
    self.order = (0 if context[dimension].length == 0 else 1) * \
                 (-1 if kind == RegionEvtKind.End else 1)

    if kind == RegionEvtKind.Init:
      self.order = -2
    if kind == RegionEvtKind.Done:
      self.order = 2

  def __eq__(self, that: 'RegionEvent') -> bool:
    """
    Determine if the RegionEvents are equal. Equality between RegionEvents
    is defined as equal when, kind and same context. Return True if
    equal otherwise False.

    Args:
      that:
        The other RegionEvent to determine if it is equal
        in when, kind and context to this RegionEvent.

    Returns:
      True:   If the two RegionEvents equal.
      False:  Otherwise.
    """
    return all([isinstance(that, RegionEvent),
                self.when == that.when,
                self.kind == that.kind,
                self.context is that.context])

  def __lt__(self, that: 'RegionEvent') -> bool:
    """
    Determine if this RegionEvent is less than the given other RegionEvent;
    ordered before the other RegionEvent. Order between the RegionEvents is
    defined as:

    1. Lesser `when` first
    2. Order by 'order':
        - -2: For sweep-line pass Init event
        - -1: For non-zero-length Region End events
        -  0: For zero-length Region Begin and End events
        -  1: For non-zero-length Region Begin events
        -  2: For sweep-line pass Done event
    3. If same context then beginning events first, and
    4. Same 'order' order by context.id.

    The ordering within the same 'when':
      <End>... <0-length Begin><0-length End> <Begin>...

    Args:
      that:
        The other RegionEvent to determine if this 
        RegionEvent is less than (ordered before) 
        that RegionEvent.

    Returns:
      True:   If this RegionEvent is less than 
              the other RegionEvent.
      False:  Otherwise.
    """
    if self == that:
      return False
    elif self.when != that.when:
      return self.when < that.when
    elif self.order != that.order:
      return self.order < that.order
    elif self.context is that.context or self.context.id == that.context.id:
      return self.kind < that.kind
    else:
      return self.context.id < that.context.id


@dataclass
class RegionTimeln(MdTimeline[Region]):
  """
  Data class that provides methods for generating sorted iterations of 
  RegionEvents for each dimension in the Regions within an assigned RegionSet; 
  each Region results in a beginning and an ending event.

  Attributes:
    dimension:
      The number of dimensions within the 
      multi-dimensional Region objects.
    regions:
      The RegionSet associated with this timeline.

  Methods:
    Special:  __init__
    Instance: events

  Inherited from MdTimeline:
    Attributes:
      dimension
    Methods:
      Special:  __getitem__
    Abstract Methods:
      Instance: events
  """
  regions: 'RegionSet'

  def __init__(self, regions: 'RegionSet'):
    """
    Initialize this timeline of Regions with the given RegionSet.

    Args:
      regions:
        The RegionSet to bind to this
        timeline of Regions.
    """
    self.regions = regions
    self.dimension = regions.dimension

  def events(self, dimension: int = 0) -> Iterator[RegionEvent]:
    """
    Returns an iterator of sorted RegionEvents generated from a set of
    RegionSet along a given dimension. Each Region maps to two RegionEvents:
    a beginning RegionEvent and a ending RegionEvent.

    Args:
      dimension:
        The dimension along which RegionEvents occur.

    Returns:
      An Iterator of sorted RegionEvents (Region
      beginning and ending events).
    """
    assert 0 <= dimension < self.regions.dimension

    def _events() -> Iterator[RegionEvent]:
      bbox = self.regions.bbox
      yield RegionEvent(RegionEvtKind.Init, bbox[dimension].lower, bbox, dimension)
      yield RegionEvent(RegionEvtKind.Done, bbox[dimension].upper, bbox, dimension)

      for region in self.regions:
        yield RegionEvent(RegionEvtKind.Begin, region[dimension].lower, region, dimension)
        yield RegionEvent(RegionEvtKind.End,   region[dimension].upper, region, dimension)

    return iter(SortedList(_events()))
