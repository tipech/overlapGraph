#!/usr/env/python

"""
Base Event Publisher and Subscriber

This script implements the Event, Publisher and Subscriber classes, that
provides a pub-sub interface for broadcasting Events from Publishers (Subject)
to Subscribers (Observers). The Publisher is an Observer as well that enables
rebroadcasting of Events.

Classes:
- Event
- Subscriber
- Publisher
"""

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

  Methods:
    Instance: setparams
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
  Class that implements the interface for an Observer.
  Each Event is paired with an IntEnum event type (or kind), and invokes
  specific event handler methods for each Event type.

  Generics:
    T:  Contextual object associated with each Event.

  Attributes:
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

  Methods:
    Special:  __init__
    Instance: on_next

  Inherited from Observer:
    Abstract Methods:
      Instance: on_next, on_completed, on_error
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

class Publisher(Subscriber[T]):
  """
  Class that implements the interface for an Observer.
  Broadcasts the Events to the subscribed Observers on the Subject.
  Each Event is paired with an IntEnum event type (or kind), and invokes
  specific event handler methods for each Event type.

  Generics:
    T:  Contextual object associated with each Event.

  Attributes:
    subject:
      The Subject for Observers to subscribe to.

  Methods:
    Special:  __init__
    Instance: subscribe, broadcast,
              on_next, on_completed, on_error

  Inherited from Observer:
    Attributes:
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

    Overridden Methods:
      Special:  __init__
      Instance: on_next

    Abstract Methods:
      Instance: on_completed, on_error
  """
  subject:      Subject

  def __init__(self, events: Union[IntEnum, None] = None):
    """
    Initialize this Publisher with the given Event types.

    Args:
      events:
        The registered Event types (kind).
        If None, no register Event types.
    """
    Subscriber.__init__(self, events)

    self.subject = Subject()

  ### Methods: Subscribe

  def subscribe(self, observer: Observer):
    """
    Subscribes the given Observer to the subject of
    this Publisher when an Event occurs.

    Args:
      observer:
        The Observer to subscribe to.
    """
    if observer == self:
      def on_next(event: Event[T]):
        Subscriber.on_next(self, event)

      self.subject.subscribe(on_next)
    else:
      self.subject.subscribe(observer)

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
    if hasattr(event, 'source') and event.source == self:
      return

    event.setparams(source=self, **kwargs)
    self.subject.on_next(event)

  ### Methods: Event Handlers

  def on_next(self, event: Event[T]):
    """
    The Event handler when an Event occurs.
    Broadcast next Event.

    Args:
      event:
        The next Event to occur.
    """
    try:
      if self.events:
        Subscriber.on_next(self, event)
    finally:
      self.broadcast(event)

  def on_completed(self):
    """
    The Event handler when no more Events. Subscription completed.
    Broadcast completion Event.
    """
    self.subject.on_completed()

  def on_error(self, exception: Exception):
    """
    The Event handler when an error occurs.
    Broadcast error Event.

    Args:
      exception:
        The error that occurred.
    """
    self.subject.on_error(exception)
