#!/usr/bin/env python

"""
Abstract Event Timeline

This script defines the Event and Timeline classes, where Timeline is an
abstract definition for a sorted sequence of Events, and each Event is a data
representation of a point along the Timeline with a particular event type or
'kind'. The Timeline class defines methods for generating a sorted Iterators
of Events.

Classes:
- Event

Abstract Classes:
- Timeline
"""

from dataclasses import dataclass
from enum import IntEnum
from functools import total_ordering
from typing import Generic, Iterator, TypeVar


T = TypeVar('T')


@dataclass
@total_ordering
class Event(Generic[T]): # pylint: disable=E1136
  """
  Data class for an event. Each event has a value for when the event occurs,
  a specified event type, and the object associated with the event as context.
  Events should be ordered by when the event occurs and the kind of event.

  Generic:
    T:  Contextual object associated
        with each Event.

  Attributes:
    when:     The value (time) along the timeline,
              where this event takes place.
    kind:     The type of event.
    context:  The object associated with this event.

  Methods:
    Special:  __eq__, __lt__
  """
  when: float
  kind: IntEnum
  context: T

  def __eq__(self, that: 'Event') -> bool:
    """
    Determine if the Events are equal. Equality between Events
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
    ordered before the other Event.

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
    elif self.context is that.context:
      return self.kind < that.kind
    else:
      return self.kind < that.kind


@dataclass
class Timeline(Generic[T]): # pylint: disable=E1136
  """
  Abstract data class for a timeline that provides methods for 
  generating sorted Iterators of Events.

  Generic:
    T:  Contextual object associated
        with each Event.

  Abstract Methods:
    Instance: events
  """

  def events(self, **kwargs) -> Iterator[Event[T]]:
    """
    Returns an Iterator of sorted Events.

    Args:
      kwargs: Additional arguments.

    Returns:
      An Iterator of sorted Events.
    """
    raise NotImplementedError
