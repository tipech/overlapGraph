#!/usr/env/python

"""
Generalized Cyclic Multi-Pass Sweep-line Algorithm

The cyclic multi-pass sweep-line algorithm, simply repeatedly
sweeps across the same Timeline, until a specified number of passes
has been completed or some signal is given to stop sweeping.

Classes:
- CycleSweep
"""

from typing import TypeVar, Union

from sources.algorithms.sweepln.basesweep import Sweepline
from sources.datastructs.abstract.pubsub import Subscriber
from sources.datastructs.abstract.timeline import Timeline


T = TypeVar('T')


class CycleSweep(Sweepline[T]):
  """
  The generalized cyclic multi-pass sweep-line algorithm.

  Generics:
    T:  Objects type within the Timeline.

  Extends:
    Sweepline[T]
  """

  ### Methods: Evaluation

  def evaluate(self, iterations: int = -1, *args, evparams_kw = {}, **kwargs):
    """
    Execute the cyclic multi-pass sweep-line algorithm over the
    attached Timeline. Broadcast Events to the Observers.

    Args:
      iterations:
        The number of passes to run the algorithm over
        the Timeline. If negative value, the algorithm will
        continue until one of the subscriber calls the added
        stopiteration() method in the Events as a parameter.
      evparams_kw:
        Arguments for event.setparams().
      args, kwargs:
        Arguments for timeline.events().
    """
    N = 0
    status = {'stop': False}

    def stopiter():
      status['stop'] = True

    while 0 > iterations or iterations > N:
      # cycle through each event in the timeline, one-pass
      for event in self.timeline.events(*args, **kwargs):
        event.setparams(iteration=N, stopiteration=stopiter, **evparams_kw)
        self.on_next(event)
      # stopiteration called
      if status['stop']:
        iterations = 0
      # increment sweep counter
      N += 1

    self.on_completed()
