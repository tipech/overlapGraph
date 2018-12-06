#!/usr/bin/env python

#
# datastructs/timeline.py - Event Timeline for Region Sets
#
# This script implements the Timeline class along with its helper
# classes EventKind and Event. The Timeline class generates a sorted
# iteration of Events for each dimension in the Regions, each Region
# results in a beginning and an ending event.
#

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Iterable, Iterator, List, Union

from sortedcontainers import SortedList

from .region import Region

try: # cyclic codependency
  from .regionset import RegionSet
except ImportError:
  pass


class EventKind(IntEnum):
  """
  Enumeration of allowed Event `kind` values. The values denote the beginning and 
  ending event of an Region's interval in a particular dimension.

  Values: Begin, End
  """
  Begin = 0
  End   = 1

@dataclass
class Event:
  """
  Data class for an Event. Each event has a value for when the event
  occurs, a specified event type, the Region context associated with
  the Event, and dimension along which the event occurs. Events are ordered
  by when the event occurs and the kind of Event. If the contexts are for
  the same Region (i.e.: Region of zero length, begin == end), begin is
  ordered before end. If the contexts are different Regions and if the
  kind is the same, no change in order. But if the contexts and kind are
  different (i.e.: the Regions are adjacent), the ending events are ordered
  before the beginning events.

  Properties:       when, kind, context, dimension
  Special Methods:  __init__, __eq__, __lt__
  """
  when:       float
  kind:       EventKind
  context:    Region
  dimension:  int

  def __init__(self, kind: Union[EventKind, str], when: float, context: Region, dimension: int = 0):
    """
    Initialize a new Event with the specified kind, when, context and dimension.
    The kind of event can be the EventKind enum value or the string name equivalent.

    :param kind:
    :param when:
    :param context:
    :param dimension:
    """
    if isinstance(kind, str):
      kind = EventKind[kind]

    assert isinstance(kind, EventKind)
    assert 0 <= dimension < context.dimension

    self.kind = kind
    self.when = when
    self.context = context
    self.dimension = dimension

  def __eq__(self, that: 'Event') -> bool:
    """
    Determine if the events are equal. Equality between Events
    is defined as equal when and equal kind. Return True if
    equal otherwise False.

    :param that:
    """
    return all([isinstance(that, Event),
                self.when == that.when,
                self.kind == that.kind])

  def __lt__(self, that: 'Event') -> bool:
    """
    Determine if this Event is less than the given other Event;
    ordered before the other Event. Order between the Events is
    defined as: (1) lesser `when` first, (2) if same context then
    beginning Events first, (3) and (4) context with length 0 first,
    otherwise (5) ending Events first. The ordering within the same
    'when': <End>... <0-length Begin><0-length End> <Begin>...
    Return True if less than the given other Event, otherwise False.

    :param that:
    """
    if self == that:
      return False
    if self.when != that.when:
      return self.when < that.when
    if self.context is that.context:
      return self.kind < that.kind
    if self.context[self.dimension].length == 0:
      return that.kind == EventKind.Begin
    if self.kind == EventKind.End:
      return that.context[that.dimension].length == 0
    if self.kind == EventKind.Begin:
      return self.kind > that.kind

@dataclass
class Timeline:
  """
  Data class that provides methods for generating sorted
  iterations of Events for each dimension in the Regions within an
  assigned RegionSet; each Region results in a beginning and an
  ending event.

  Properties:       regions
  Special Methods:  __getitem__
  Methods:          events
  """
  regions: 'RegionSet'

  def _events(self, dimension: int = 0) -> Iterable[Event]:
    """
    Generator for converting the Regions within the RegionSet
    to an iterable, unordered sequence of Events; a beginning Event
    and a ending Event for each Region.

    :param dimension:
    """
    assert 0 <= dimension < self.regions.dimension

    for region in self.regions:
      yield Event(EventKind.Begin, region[dimension].lower, region, dimension)
      yield Event(EventKind.End,   region[dimension].upper, region, dimension)

  def _sorted_events(self, dimension: int = 0) -> Iterable[Event]:
    """
    Generator for converting the Regions within the RegionSet
    to an iterable, ordered sequence of Events; a beginning Event
    and a ending Event for each Region. The output from self._events
    method is passed to the SortedList data structure that outputs
    a sorted iterator.

    :param dimension:
    """
    return SortedList(self._events(dimension)).__iter__()

  def events(self, dimension: int = 0) -> Iterable[Event]:
    """
    Returns an iterator of sorted Events generated from a set of
    RegionSet along a given dimension. Each Region maps to two
    Events: a beginning Event and a ending Event.

    :param dimension:
    """
    return self._sorted_events(dimension)

  def __getitem__(self, dimension: int = 0) -> Iterable[Event]:
    """
    Returns an iterator of sorted Events generated from a set of
    RegionSet along a given dimension. Each Region maps to two
    Events: a beginning Event and a ending Event.
    Same as: self.events method.
    Syntactic Sugar: self[dimension]

    :param dimension:
    """
    return self.events(dimension)
