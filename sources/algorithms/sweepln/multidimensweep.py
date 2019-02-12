#!/usr/env/python

"""
Generalized Multi-dimensional Sweep-line Algorithm (Non-threaded)

Implements a generalized version of a multi-dimensional sweep-line algorithm.
Implements MultidimenSweep class that iterates over the MdTimeline in each
dimension and broadcasts Events to subscribed Observers to execute the specific
details of the algorithm.

Classes:
- MultidimenSweep
"""

from typing import TypeVar

from sources.abstract import MdTimeline

from .basesweep import Sweepline


T = TypeVar('T')


class MultidimenSweep(Sweepline[T]):
  """
  The generalized multi-dimensional sweep-line algorithm.
  This implementation is not parallelized; not threaded.

  Generics:
    T:  Objects type within the MdTimeline.

  Extends:
    Sweepline[T]

  Attributes:
    timeline:
      The multi-dimensional Timeline to evaluate
      the algorithm over each dimension.

      Redefines:
        Sweepline.timeline
  """
  timeline: MdTimeline[T]

  def __init__(self, timeline: MdTimeline[T], *args, **kwargs):
    """
    Initialize the sweep-line algorithm.

    Args:
      timeline:
        The multi-dimensional Timeline to evaluate
        the algorithm over each dimension.
      args, kwargs:
        Additional arguments.
    """
    assert isinstance(self.timeline, MdTimeline)

    Sweepline.__init__(self, timeline, *args, **kwargs)

  ### Methods: Evaluation

  def evaluate(self, *args, evparams_kw = {}, **kwargs):
    """
    Execute the multi-dimensional sweep-line algorithm
    over each dimension in the attached MdTimeline.
    Broadcast Events to the Observers.

    Args:
      evparams_kw:
        Arguments for event.setparams().
      args, kwargs:
        Arguments for timeline.events().
    """
    for dimension in range(self.timeline.dimension):
      for event in self.timeline.events(dimension, *args, **kwargs):
        event.setparams(**evparams_kw)
        self.on_next(event)

    self.on_completed()
