#!/usr/bin/env python

"""
Event Timeline for Region Sets

This script implements the Timeline class along with its helper
classes EventKind and Event. The Timeline class generates a sorted
iteration of Events for each dimension in the Regions, each Region
results in a beginning and an ending event.

Classes:
- EventKind (IntEnum)
- Event
- Timeline
"""

from dataclasses import dataclass, field
from enum import IntEnum
from functools import total_ordering
from typing import Iterator, List, Union

from sortedcontainers import SortedList

from sources.datastructs.shapes.region import Region

try: # cyclic codependency
  from sources.datastructs.datasets.regionset import RegionSet
except ImportError:
  pass


class EventKind(IntEnum):
  """
  Enumeration of allowed Event `kind` values. The values denote the beginning
  and ending event of an Region's interval in a particular dimension.

  Values:
    Begin:  Flag for the beginning of a Region.
    End:    Flag for the ending of a Region.
  """
  Begin = 0
  End   = 1


@dataclass
@total_ordering
class Event:
  """
  Data class for an Event. Each event has a value for when the event occurs,
  a specified event type, the Region context associated with the Event, and
  dimension along which the event occurs. Events are ordered by when the event
  occurs, the kind of Event and if the Region is zero-length or non-zero length
  along the timeline dimension.

  Attributes:
    when:       The value (time) along the sorted dimension
                where this Event takes place.
    kind:       The type of Event: Begin or End of Region.
    context:    The Region associated with this Event.
    dimension:  The dimension along which Events occur.
    order:      The sort priority of the Events with the
                same 'when', occurs at the same time.

  Methods:
    Special:  __init__, __eq__, __lt__
  """
  when:       float
  kind:       EventKind
  context:    Region
  dimension:  int
  order:      int

  def __init__(self, kind: Union[EventKind, str], when: float,
                     context: Region, dimension: int = 0):
    """
    Initialize a new Event with the specified kind, when, context & dimension.
    The kind of event can be the EventKind enum value or the string name
    equivalent.

    Args:
      kind:       The type of Event: Begin or End of Region.
      when:       The value/time along the sorted dimension
                  where this Event takes place.
      context:    The Region associated with this Event.
      dimension:  The dimension along which Events occur.
    """
    if isinstance(kind, str):
      kind = EventKind[kind]

    assert isinstance(kind, EventKind)
    assert 0 <= dimension < context.dimension

    self.kind = kind
    self.when = when
    self.context = context
    self.dimension = dimension
    self.order = (0 if context[dimension].length == 0 else 1) * \
                 (-1 if kind == EventKind.End else 1)

  def __eq__(self, that: 'Event') -> bool:
    """
    Determine if the events are equal. Equality between Events
    is defined as equal when, kind and same context. Return True if
    equal otherwise False.

    Args:
      that:
        The other Event to determine if it is equal
        in when, kind and context to this Event.

    Returns:
      True:   If the two Events equal.
      False:  Otherwise.
    """
    return all([isinstance(that, Event),
                self.when == that.when,
                self.kind == that.kind,
                self.context is that.context])

  def __lt__(self, that: 'Event') -> bool:
    """
    Determine if this Event is less than the given other Event;
    ordered before the other Event. Order between the Events is
    defined as:

    1. Lesser `when` first
    2. Order by 'order':
        - -1: For non-zero-length Region End events
        -  0: For zero-length Region Begin and End events
        -  1: For non-zero-length Region Begin events
    3. If same context then beginning Events first, and
    4. Same 'order' order by context.id.

    The ordering within the same 'when':
      <End>... <0-length Begin><0-length End> <Begin>...

    Args:
      that:
        The other Event to determine if this Event
        is less than (ordered before) that Event.

    Returns:
      True:   If this Event is less than the other Event.
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
class Timeline:
  """
  Data class that provides methods for generating sorted iterations of Events
  for each dimension in the Regions within an assigned RegionSet; each Region
  results in a beginning and an ending event.

  Attributes:
    regions

  Methods:
    Special:  __getitem__
    Instance: events
  """
  regions: 'RegionSet'

  def _events(self, dimension: int = 0) -> Iterator[Event]:
    """
    Generator for converting the Regions within the RegionSet to an
    Iterator, unordered sequence of Events; a beginning Event and a ending
    Event for each Region.

    Args:
      dimension:
        The dimension along which Events occur.

    Returns:
      An Iterator of unordered Events (Region
      beginning and ending events).
    """
    assert 0 <= dimension < self.regions.dimension

    for region in self.regions:
      yield Event(EventKind.Begin, region[dimension].lower, region, dimension)
      yield Event(EventKind.End,   region[dimension].upper, region, dimension)

  def _sorted_events(self, dimension: int = 0) -> Iterator[Event]:
    """
    Generator for converting the Regions within the RegionSet to an iterator,
    ordered sequence of Events; a beginning Event and a ending Event for each
    Region. The output from self._events method is passed to the SortedList
    data structure that outputs a sorted iterator.

    Args:
      dimension:
        The dimension along which Events occur.

    Returns:
      An Iterator of sorted Events (Region
      beginning and ending events).
    """
    return SortedList(self._events(dimension)).__iter__()

  def events(self, dimension: int = 0) -> Iterator[Event]:
    """
    Returns an iterator of sorted Events generated from a set of RegionSet
    along a given dimension. Each Region maps to two Events: a beginning
    Event and a ending Event.

    Alias for:
      self._sorted_events(dimension)

    Args:
      dimension:
        The dimension along which Events occur.

    Returns:
      An Iterator of sorted Events (Region
      beginning and ending events).
    """
    return self._sorted_events(dimension)

  def __getitem__(self, dimension: int = 0) -> Iterator[Event]:
    """
    Returns an iterator of sorted Events generated from a set of RegionSet
    along a given dimension. Each Region maps to two Events: a beginning
    Event and a ending Event.

    Alias for:
      self.events(dimension)

    Is syntactic sugar for:
      self[dimension]

    Args:
      dimension:
        The dimension along which Events occur.

    Returns:
      An Iterator of sorted Events (Region
      beginning and ending events).
    """
    return self.events(dimension)
