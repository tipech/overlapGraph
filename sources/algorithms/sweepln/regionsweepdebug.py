#!/usr/bin/env python

"""
Compute Region Pairwise Overlaps by One-pass Sweep-line Algorithm

This script implements the RegionSweepOverlaps class that computes a list of
all of the pairwise overlapping Regions using the one-pass sweep-line
algorithm, through a subscription to RegionSweep.

Classes:
- RegionSweepOverlaps
"""

from typing import Tuple, Union

from sources.algorithms.sweepln.regionsweep import RegionSweepEvtKind
from sources.datastructs.abstract.pubsub import Event, Subscriber
from sources.datastructs.datasets.regiontime import RegionEvent
from sources.datastructs.shapes.region import Region, RegionPair


class RegionSweepDebug(Subscriber[Union[Region, RegionPair]]):
  """
  Class that computes a list of all of the pairwise overlapping Regions 
  using the one-pass sweep-line algorithm, through a subscription 
  to RegionSweep.

  Methods:
    Special:  __init__
    Instance: on_next

  Inherited from Subscriber:
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
      Instance: on_next, on_completed, on_error

    Overridden Methods:
      Special:  __init__
      Instance: on_next
  """
  counter: int

  def __init__(self):
    """
    Initialize this class to compute a list of all of the pairwise
    overlapping Regions using the one-pass sweep-line algorithm.
    Sets the events as RegionSweepEvtKind.
    """
    Subscriber.__init__(self, RegionSweepEvtKind)

    self.counter = 0

  ### Methods: Event Handlers

  def on_next(self, event: Event[Union[Region, RegionPair]]):
    """
    Print Events for sweep-line algorithm.

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
