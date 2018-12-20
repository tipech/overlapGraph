#!/usr/bin/env python

"""
Abstract Multi-dimensional Event Timeline

This script defines the MdEvent and MdTimeline classes, where 
MdTimeline is an abstract definition for several sorted sequences of 
MdEvents (each sorted sequence is one of dimensions within the 
MdTimeline system), and each MdEvent is a data representation of a
multi-dimensional point along the MdTimeline in a particular dimension and
with a particular event type or 'kind'. The MdTimeline class defines
methods for generating a sorted Iterators of MdEvents for each dimension,
within the multi-dimensional space of MdTimeline.

Classes:
- MdEvent (Event)

Abstract Classes:
- MdTimeline (Timeline)
"""

from dataclasses import dataclass
from functools import total_ordering
from typing import Generic, Iterator, TypeVar

from sources.datastructs.datasets.timeline import Event, Timeline


T = TypeVar('T')


@dataclass
@total_ordering
class MdEvent(Event[T]): # pylint: disable=E1136
  """
  Data class for a mult-dimensional event. Each event has a value for when 
  the event occurs, a specified event type, the object associated with the
  event as context, and the dimension along which events occur within the
  multi-dimensional timeline, MdTimeline. Events should be ordered by when
  the event occurs and the kind of event.

  Generic:
    T:  Contextual object associated
        with each MdEvent.

  Attributes:
    dimension:  The dimension along which events occur.

  Inherited from Event:
    Attributes:
      when:     The value (time) along the timeline,
                where this event takes place.
      kind:     The type of event.
      context:  The object associated with this event.

    Methods:
      Special:  __eq__, __lt__
  """
  dimension: int


@dataclass
class MdTimeline(Timeline[T]): # pylint: disable=E1136
  """
  Abstract data class is a multi-dimensional timeline that provides
  methods for generating sorted Iterators of MdEvents.

  Generic:
    T:  Contextual object associated
        with each MdEvent.

  Methods:
    Special:  __getitem__
  Abstract Methods:
    Instance: events
  """

  def events(self, dimension: int = 0, **kwargs) -> Iterator[MdEvent[T]]:
    """
    Returns an Iterator of sorted MdEvent along the given dimension.

    Args:
      dimension:
        The dimension along which MdEvents occur.
      kwargs:
        Additional arguments.

    Returns:
      An Iterator of sorted MdEvent along
      specified dimension.
    """
    raise NotImplementedError

  def __getitem__(self, dimension: int = 0) -> Iterator[MdEvent[T]]:
    """
    Returns an Iterator of sorted MdEvent along the given dimension.

    Is syntactic sugar for:
      self[dimension]

    Args:
      dimension:
        The dimension along which MdEvents occur.

    Returns:
      An Iterator of sorted MdEvent along
      specified dimension.
    """
    return self.events(dimension)
