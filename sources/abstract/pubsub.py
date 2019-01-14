#!/usr/env/python

"""
Base Event Publisher and Subscriber

Implements the Event, Publisher and Subscriber classes, that provides a pub-
sub interface for broadcasting Events from Publishers (Subject) to Subscribers
(Observers). The Publisher is an Observer as well that enables rebroadcasting
of Events.

Classes:
- Event
- Subscriber
- Publisher
"""

from collections import abc
from dataclasses import dataclass
from enum import IntEnum
from typing import Callable, Generic, TypeVar, Union

from rx import Observer
from rx.subjects import Subject


T = TypeVar('T')


@dataclass
class Event(Generic[T]): # pylint: disable=E1136
  """
  Data class for an event. Each event has a specified event type,
  and the object associated with the event as context.

  Generics:
    T:  Contextual object associated with each Event.

  Attributes:
    kind:     The type of event.
    context:  The object associated with this event.
  """
  kind: IntEnum
  context: T

  def setparams(self, **kwargs):
    """
    Assigns the given keyword arguments as attributes to this Event.

    Args:
      kwargs:
        The arguments to set as attributes.
    """
    for k, v in kwargs.items():
      setattr(self, k, v)


class Subscriber(Observer, Generic[T]): # pylint: disable=E1136
  """
  Implements the wrapper for an Observer.

  Each Event is paired with an IntEnum event type (or kind), and invokes
  specific event handler methods for each Event type.

  Generics:
    T:  Contextual object associated with each Event.

  Extends:
    Observer

  Attributes:
    events:
      The registered Event types (kind).
      If None, no register Event types.
    eventmapper:
      A lambda method that maps each Event to a
      method name for a specific event handler.
    strict:
      Boolean flag whether or not to raise an exception
      when Event handler not found.
      - True:  Raise exception when handler not found.
      - False: Otherwise. Default.
  """
  events:       Union[IntEnum, None]
  eventmapper:  Callable[[Event[T]], str]
  strict:       bool

  def __init__(self, events: Union[IntEnum, None] = None):
    """
    Initialize this Subscriber with the given Event types.

    Args:
      events:
        The registered Event types (kind).
        If None, no register Event types.
    """
    def eventmapper(event: Event[T]) -> str:
      assert isinstance(event, Event)
      assert isinstance(event.kind, IntEnum)

      return f'on_{event.kind.name}'.lower()

    self.events = events
    self.eventmapper = eventmapper
    self.strict = False

  ### Methods: Event Handlers

  def on_next(self, event: Event[T]):
    """
    The Event handler when an Event occurs.

    Args:
      event:
        The next Event to occur.

    Raises:
      AttributeError:
        Event handler not found.
    """
    handle = self.eventmapper(event)
    if hasattr(self, handle):
      #print(f'{type(self).__name__}.{handle}')
      getattr(self, handle)(event)
    elif self.strict:
      raise AttributeError(handle)

  def on_completed(self):
    """
    The Event handler when no more Events.
    Subscription completed.
    """
    pass # Do nothing

  def on_error(self, exception: Exception):
    """
    The Event handler when an error occurs.

    Args:
      exception:
        The error that occurred.
    """
    pass # Do nothing

class Publisher(Subscriber[T], abc.Container):
  """
  Implements the wrapper for an Observer and a Subject.

  Broadcasts the Events to the subscribed Observers on the Subject.
  Each Event is paired with an IntEnum event type (or kind), and invokes
  specific event handler methods for each Event type.

  Generics:
    T:  Contextual object associated with each Event.

  Extends:
    Subscriber[T]
    abc.Container

  Attributes:
    subject:
      The Subject for Observers to subscribe to.
    presubj:
      The Subject for Observers to subscribe to, whose
      on_next are always called before, self.on_next
      and the subjects' on_next.
  """
  subject: Subject
  presubj: Subject

  def __init__(self, events: Union[IntEnum, None] = None):
    """
    Initialize this Publisher with the given Event types.

    Args:
      events:
        The registered Event types (kind).
        If None, no register Event types.
    """
    Subscriber.__init__(self, events)

    self.presubj = Subject()
    self.subject = Subject()

  ### Methods: Queries

  def __contains__(self, observer: Observer) -> bool:
    """
    Determine whether or not the given is already subscribed
    to this Publisher.

    Args:
      observer:
        The Observer to test whether or not
        already subscribed to this Publisher.

    Returns:
      True:   If already subscribed.
      False:  Otherwise.
    """
    return observer in self.subject.observers or \
           observer in self.presubj.observers

  ### Methods: Subscribe

  def subscribe(self, observer: Observer, before: bool = False):
    """
    Subscribes the given Observer to the subject of
    this Publisher when an Event occurs.

    Args:
      observer:
        The Observer to subscribe to.
      before:
        Boolean flag for whether or not to receive Event
        before self.on_next or after self.on_next.
        True, for before; False, otherwise.
    """
    assert observer not in self

    subject = self.presubj if before else self.subject
    subject.subscribe(observer)

  ### Methods: Broadcast

  def broadcast(self, event: Event, **kwargs):
    """
    Broadcast the given event to subscribed Observers.

    Args:
      event:
        The Event to be broadcasted.
      kwargs:
        The parameters to be added or modified
        within the given Event.
    """
    if hasattr(event, 'source') and event.source is self:
      return

    event.setparams(source=self, **kwargs)
    self.subject.on_next(event)

  ### Methods: Event Handlers

  def on_next(self, event: Event[T]):
    """
    The Event handler when an Event occurs.
    Broadcast next Event.

    Overrides:
      Subscriber.on_next

    Args:
      event:
        The next Event to occur.
    """
    if hasattr(event, 'source') and event.source is self:
      return

    self.presubj.on_next(event)

    try:
      if self.events:
        Subscriber.on_next(self, event)
    finally:
      self.broadcast(event)

  def on_completed(self):
    """
    The Event handler when no more Events. Subscription completed.
    Broadcast completion Event.

    Overrides:
      Subscriber.on_completed
    """
    self.presubj.on_completed()
    self.subject.on_completed()

  def on_error(self, exception: Exception):
    """
    The Event handler when an error occurs.
    Broadcast error Event.

    Overrides:
      Subscriber.on_error

    Args:
      exception:
        The error that occurred.
    """
    self.presubj.on_error(exception)
    self.subject.on_error(exception)
