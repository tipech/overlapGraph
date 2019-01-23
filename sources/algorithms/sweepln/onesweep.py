#!/usr/env/python

"""
Generalized One-Pass Sweep-line Algorithm

Implements a generalized version of a one-pass sweep-line algorithm.
Implements OneSweep class that iterates over the Timeline and broadcasts
Events to subscribed Observers to execute the specific details of the
algorithm.

Classes:
- OneSweep
"""

from typing import TypeVar

from sources.abstract.timeline import Timeline
from sources.algorithms.sweepln.basesweep import Sweepline


T = TypeVar('T')


class OneSweep(Sweepline[T]):
  """
  The generalized one-pass sweep-line algorithm.

  Generics:
    T:  Objects type within the Timeline.

  Extends:
    Sweepline[T]
  """

  ### Methods: Evaluation

  def evaluate(self, *args, evparams_kw = {}, **kwargs):
    """
    Execute the sweep-line algorithm over the attached Timeline.
    Broadcast Events to the Observers.

    Args:
      evparams_kw:
        Arguments for event.setparams().
      args, kwargs:
        Arguments for timeline.events().
    """
    for event in self.timeline.events(*args, **kwargs):
      event.setparams(**evparams_kw)
      self.on_next(event)

    self.on_completed()
