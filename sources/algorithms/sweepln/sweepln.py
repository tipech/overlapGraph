#!/usr/env/python

"""
Abstract Sweep-line Algorithm

Defines an abstract sweep-line algorithm, Sweepln class, that
iterates over the Timeline and broadcasts Events to subscribed Observers to
execute the specific details of the algorithm.

Classes:
- Sweepln
"""

from abc import ABCMeta, abstractmethod
from collections import abc
from typing import Callable, TypeVar

from sources.datastructs.abstract.pubsub import Publisher
from sources.datastructs.abstract.timeline import Timeline


T = TypeVar('T')


class Sweepln(Publisher[T], abc.Callable, metaclass=ABCMeta):
  """
  Abstract class

  Definition of a sweep-line algorithm.

  Generics:
    T:  Objects type within the Timeline.

  Extends:
    Publisher[T]
    abc.Callable

  Attributes:
    timeline:
      The Timeline to evaluate the algorithm over.
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
      args, kwargs:
        Additional arguments.
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
