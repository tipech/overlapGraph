#!/usr/bin/env python

"""
Abstract Event Timeline

Defines the Event and Timeline classes, where Timeline is an abstract
definition for a sorted sequence of Events, and each Event is a data
representation of a point along the Timeline with a particular event type or
'kind'. The Timeline class defines methods for generating a sorted Iterators
of Events.

Classes:
- TEvent

Abstract Classes:
- Timeline
"""

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from functools import total_ordering
from typing import Generic, Iterator, TypeVar

from .pubsub import Event


T = TypeVar('T')


@dataclass
@total_ordering
class TEvent(Event[T]):
  """
  A timeline event.

  Each timeline event has a value for when the event occurs, a specified event
  type, and the object associated with the event as context. Timeline Events
  should be ordered by when the event occurs and the kind of event.

  Generics:
    T:  Contextual object associated
        with each Event.

  Extends:
    Event[T]

  Attributes:
    when:   The value (time) along the timeline,
            where this event takes place.
  """
  when: float

  def __eq__(self, that: 'TEvent[T]') -> bool:
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
    return all([isinstance(that, TEvent),
                self.when == that.when,
                self.kind == that.kind,
                self.context is that.context])

  def __lt__(self, that: 'TEvent[T]') -> bool:
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
  Abstract Class

  A timeline that provides methods for generating sorted Iterators of Events.

  Generics:
    T:  Contextual object associated with each Event.
  """
  __metaclass__ = ABCMeta

  @abstractmethod
  def events(self) -> Iterator[TEvent[T]]:
    """
    Returns an Iterator of sorted Events.

    Returns:
      An Iterator of sorted Events.
    """
    raise NotImplementedError
