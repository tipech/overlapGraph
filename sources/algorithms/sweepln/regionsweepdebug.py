#!/usr/bin/env python

"""
Debugging for One-pass Sweep-line Algorithm over Regions

Implements the RegionSweepDebug class that prints a block of debugging output
for every Event broadcasted from the one-pass sweep-line algorithm, through a
subscription to RegionSweep.

Classes:
- RegionSweepDebug
"""

from typing import Tuple

from sources.algorithms.sweepln.regionsweep import RegionSweepEvtKind
from sources.datastructs.abstract.pubsub import Event, Subscriber
from sources.datastructs.datasets.regiontime import RegionEvent
from sources.datastructs.shapes.region import RegionGrp


class RegionSweepDebug(Subscriber[RegionGrp]):
  """
  Debugging for One-pass Sweep-line over Regions

  For every Event broadcasted from the one-pass sweep-line algorithm,
  prints a block of debugging output, through a subscription
  to RegionSweep.

  Extends:
    Subscriber[RegionGrp]

  Attributes:
    counter:  The Event sequence number.
              The number of Events previously seen.
  """
  counter: int

  def __init__(self):
    """
    Initialize this class to prints a block of debugging output for
    every Event broadcasted from the one-pass sweep-line algorithm.
    Sets the events as RegionSweepEvtKind.
    """
    Subscriber.__init__(self, RegionSweepEvtKind)

    self.counter = 0

  ### Methods: Event Handlers

  def on_next(self, event: Event[RegionGrp]):
    """
    Print Events for sweep-line algorithm.

    Overrides:
      Subscriber.on_next

    Args:
      event:
        The next Event.
    """
    print()
    print(f'{self.counter}:')
    print(f'\tkind: {event.kind.name}')
    print(f'\tdepth: {event.depth}')
    print(f'\tactives: {[k[0:8] for k in event.actives]}')

    if isinstance(event, RegionEvent):
      print(f'\tdimension: {event.dimension}, ' +
            f'when: {event.when}, ' +
            f'order: {event.order}')
      print(f'\tcontext: {event.context.id[0:8]}, ' +
            f'lower: {event.context.lower}, ' +
            f'upper: {event.context.upper}')

    if isinstance(event.context, Tuple):
      print(f'\tcontext:')
      print(f'\t\t0: {event.context[0].id[0:8]}, ' +
            f'lower: {event.context[0].lower}, ' +
            f'upper: {event.context[0].upper}')
      print(f'\t\t0: {event.context[1].id[0:8]}, ' +
            f'lower: {event.context[1].lower}, ' +
            f'upper: {event.context[1].upper}')

    self.counter += 1
