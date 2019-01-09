#!/usr/bin/env python

"""
Abstract Multi-dimensional Event Timeline

This script defines the MdTEvent and MdTimeline classes, where 
MdTimeline is an abstract definition for several sorted sequences of 
MdEvents (each sorted sequence is one of dimensions within the 
MdTimeline system), and each MdTEvent is a data representation of a
multi-dimensional point along the MdTimeline in a particular dimension and
with a particular event type or 'kind'. The MdTimeline class defines
methods for generating a sorted Iterators of MdEvents for each dimension,
within the multi-dimensional space of MdTimeline.

Classes:
- MdTEvent (TEvent)
- MdTimelineOneDimen (Timeline)

Abstract Classes:
- MdTimeline (Timeline)
"""

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from functools import total_ordering
from typing import Generic, Iterator, TypeVar

from sources.datastructs.abstract.timeline import TEvent, Timeline


T = TypeVar('T')


@dataclass
@total_ordering
class MdTEvent(TEvent[T]):
  """
  Data class for a mult-dimensional event. Each event has a value for when 
  the event occurs, a specified event type, the object associated with the
  event as context, and the dimension along which events occur within the
  multi-dimensional timeline, MdTimeline. Events should be ordered by when
  the event occurs and the kind of event.

  Generics:
    T:  Contextual object associated
        with each MdTEvent.

  Attributes:
    dimension:  The dimension along which events occur.

  Inherited from TEvent:
    Attributes:
      when:     The value (time) along the timeline,
                where this event takes place.
      kind:     The type of event.
      context:  The object associated with this event.

    Methods:
      Instance: setparams
      Special:  __eq__, __lt__
  """
  dimension: int


@dataclass
class MdTimeline(Timeline[T]):
  """
  Abstract data class is a multi-dimensional timeline that provides
  methods for generating sorted Iterators of MdEvents.

  Generics:
    T:  Contextual object associated
        with each MdTEvent.

  Attributes:
    dimension:
      The number of dimensions within the 
      multi-dimensional contextual object.

  Methods:
    Special:  __getitem__

  Abstract Methods:
    Instance: events
  """
  __metaclass__ = ABCMeta
  dimension: int

  @abstractmethod
  def events(self, dimension: int = 0) -> Iterator[MdTEvent[T]]:
    """
    Returns an Iterator of sorted MdTEvent along the given dimension.

    Args:
      dimension:
        The dimension along which MdEvents occur.

    Returns:
      An Iterator of sorted MdTEvent along
      specified dimension.
    """
    raise NotImplementedError

  def __getitem__(self, dimension: int = 0) -> Timeline[MdTEvent[T]]:
    """
    Returns a binded Timeline of sorted MdTEvent along the given dimension.

    Is syntactic sugar for:
      self[dimension]

    Args:
      dimension:
        The dimension along which MdEvents occur.

    Returns:
      A binded Timeline of sorted MdTEvent along
      specified dimension.
    """
    assert 0 <= dimension < self.dimension

    return MdTimelineOneDimen(self, dimension)


@dataclass
class MdTimelineOneDimen(Timeline[T]):
  """
  Data class for a Timeline along a single dimension.

  Generics:
    T:  Contextual object associated
        with each MdTEvent.

  Attributes:
    timeline: 
      The reference to parent MdTimeline object.
    dimension:
      The dimension along which MdEvents occur.

  Methods:
    Instance: events

  Inherited for Timeline:
    Abstract Methods:
      Instance: events
  """
  timeline  : MdTimeline[T]
  dimension : int

  def events(self) -> Iterator[MdTEvent[T]]:
    """
    Returns an Iterator of sorted MdEvents.

    Returns:
      An Iterator of sorted MdEvents.
    """
    assert isinstance(self.timeline, MdTimeline)
    assert isinstance(self.dimension, int)
    assert 0 <= self.dimension < self.timeline.dimension

    return self.timeline.events(self.dimension)
