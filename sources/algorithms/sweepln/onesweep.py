#!/usr/env/python

"""
Generalized One-Pass Sweep-line Algorithm

This script implements a generalized version of a one-pass sweep-line
algorithm. Implements OneSweep class that iterates over the Timeline
and broadcasts Events to subscribed Observers to execute the specific
details of the algorithm.

Classes:
- OneSweep
"""

from typing import Generic, TypeVar

from rx import Observer
from rx.subjects import Subject

from sources.datastructs.abstract.timeline import Timeline


T = TypeVar('T')


class OneSweep(Generic[T]): # pylint: disable=E1136
  """
  The generalized one-pass sweep-line algorithm.

  Generics:
    T:  Objects type within the Timeline.

  Attributes:
    subject:
      The Rx Subject that the Observers can
      subscribe to.
    timeline:
      The Timeline to evaluate the 
      algorithm over.

  Methods:
    Special:    __init__
    Instance:   subscribe, evaluate
  """
  subject:  Subject
  timeline: Timeline[T]

  def __init__(self, timeline: Timeline[T]):
    """
    Initialize the sweep-line algorithm.

    Args:
      timeline:
        The Timeline to evaluate the algorithm over.
    """
    self.subject = Subject()
    self.timeline = timeline

  ### Methods: Subscribe

  def subscribe(self, observer: Observer):
    """
    Subscribes the given Observer to the subject of this sweep-line
    algorithm to receive notifications when evaluating the input timeline.

    Args:
      observer:
        The Observer to subscribe to this OneSweep.
    """
    self.subject.subscribe(observer)

  ### Methods: Evaluation

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
    for event in self.timeline.events(*args):
      event.setparams(**kwargs)
      self.subject.on_next(event)

    self.subject.on_completed()
