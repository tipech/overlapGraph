#!/usr/env/python

"""
Abstract Sweep-line Algorithm

This script defines an abstract sweep-line algorithm, Sweepln class, that
iterates over the Timeline and broadcasts Events to subscribed Observers to
execute the specific details of the algorithm.

Classes:
- Sweepln
"""

from abc import ABCMeta, abstractmethod
from typing import TypeVar

from sources.datastructs.abstract.pubsub import Publisher
from sources.datastructs.abstract.timeline import Timeline


T = TypeVar('T')


class Sweepln(Publisher[T], metaclass=ABCMeta):
  """
  Abstract definition of a sweep-line algorithm.

  Generics:
    T:  Objects type within the Timeline.

  Attributes:
    timeline:
      The Timeline to evaluate the algorithm over.

  Methods:
    Special:  __init__, __call__

  Abstract Methods:
    Instance: evaluate

  Inherited from Publisher:
    Attributes:
      subject:
        The Subject for Observers to subscribe to.
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
      Instance: subscribe, broadcast,
                on_next, on_completed, on_error

    Overridden Methods:
      Special:  __init__
  """
  timeline: Timeline[T]

  def __init__(self, timeline: Timeline[T], *args, **kwargs):
    """
    Initialize the sweep-line algorithm.

    Args:
      timeline:
        The Timeline to evaluate the algorithm over.
      args, kwargs:
        Additional arguments.
    """
    Publisher.__init__(self, *args, **kwargs)

    self.timeline = timeline

  ### Methods: Evaluation

  @abstractmethod
  def evaluate(self, *args, **kwargs):
    """
    Execute the sweep-line algorithm over the attached Timeline.
    Broadcast Events to the Observers.

    Args:
      args:   Arguments to be passed
              to timeline.events().
      kwargs: Keyword arguments to be passed
              to event.setparams().
    """
    raise NotImplementedError

  def __call__(self, *args, **kwargs):
    """
    Execute the sweep-line algorithm over the attached Timeline.
    Broadcast Events to the Observers. Alias for: self.evaluate().

    Args:
      args, kwargs:
        Arguments to be passed to evaluate().
    """
    self.evaluate(*args, **kwargs)
