#!/usr/bin/env python

"""
Cyclic Multi-Pass Sweep-line Algorithm for RegionSet

Implements a cyclic multi-pass sweep-line algorithm over a set of Regions.
Implements RegionCycleSweep class that executes the specific details and
actions of the sweep-line algorithm, when encountering: Init, Begin, End, Done
or Intersect events. Unlike RegionSweep, for each pass the algorithm, updates
a lookup table of intersecting Regions, level-wise. With each subsequent pass,
looks at the previous level's intersecting Regions.

Classes:
- RegionCycleSweep
"""

from typing import Dict, Iterator, List, Tuple

from sources.abstract import Event
from sources.core import \
     Region, RegionEvent, RegionGrp, RegionIntxn, RegionPair, RegionSet

from .cyclesweep import CycleSweep
from .regionsweep import RegionSweep, RegionSweepEvtKind


class RegionCycleSweep(RegionSweep, CycleSweep[RegionGrp]):
  """
  A cyclic multi-pass sweep-line algorithm over a set of Regions.

  Subscribes to and is evaluated by the cyclic multi-pass sweep-line
  algorithm along a dimension on the set of Regions.

  Extends:
    RegionSweep
    CycleSweep[RegionGrp]

  Attributes:
    iteration:
      The number of the current sweep-pass of the
      algorithm, the current level.
    levels:
      A list of list. Each list in the outer list
      represents a single pass of the algorithm, a level.
      Each item in the list is an intersecting Region.
    intersects:
      A mapping from base Regions to intersecting Regions
      involving the corresponding Region.
    nextintxs:
      A mapping from base Regions to intersecting Regions
      involving the corresponding Region for the next
      iteration (pass) of the sweep-line algorithm.
  """
  iteration:  int
  levels:     List[List[Region]]
  intersects: Dict[str, List[Region]]
  nextintxs:  Dict[str, List[Region]]

  def __init__(self, regions: RegionSet):
    """
    Initialize the sweep-line algorithm over Regions.

    Args:
      regions:
        The set of Regions to evaluate
        sweep-line algorithm over.
    """
    RegionSweep.__init__(self, regions)

    self.iteration = -1
    self.levels = []
    self.intersects = {}

    for region in regions:
      self.intersects[region.id] = [region]

  ### Methods: Event Handlers

  def on_init(self, event: RegionEvent):
    """
    Handle Event when sweep-line algorithm initializes
    the current iteration.

    Overrides:
      RegionSweep.on_init

    Args:
      event:
        The initialization Event.
    """
    RegionSweep.on_init(self, event)

    assert hasattr(event, 'iteration')
    assert self.iteration + 1 == event.iteration == len(self.levels)

    self.levels.append([])
    self.iteration += 1
    self.nextintxs = {}

  def on_begin(self, event: RegionEvent):
    """
    Handle Event when sweep-line algorithm encounters
    the beginning of a Region.

    Overrides:
      RegionSweep.on_begin

    Args:
      event:
        The Region beginning Event.
    """
    assert self.is_active
    assert event.kind == RegionSweepEvtKind.Begin

    region = event.context
    self.nextintxs[region.id] = []

    for a, b in self.findintersects(region):
      self.on_intersect(Event(RegionSweepEvtKind.Intersect, (a, b)))

    for intersect in self.intersects[region.id]:
      self.actives[intersect.id] = intersect

  def on_intersect(self, event: Event[RegionPair]):
    """
    Handle Event when sweep-line algorithm encounters the two or
    more Regions intersecting. Buffers Events for broadcasting.

    Overrides:
      RegionSweep.on_intersect

    Args:
      event:
        The intersecting Regions Event.
    """
    assert self.is_active
    assert event.kind == RegionSweepEvtKind.Intersect
    assert len(self.levels) == self.iteration + 1
    assert isinstance(self.levels[-1], List)
    assert isinstance(event.context, Tuple) and len(event.context) == 2

    a, b = event.context
    region = a.intersect(b, 'aggregate')

    assert 'intersect' in region
    assert len(region['intersect']) == self.iteration + 2

    event.setparams(iteration=self.iteration, levels=self.levels,
                    aggregate=region['intersect'], intersect=region)

    self.nextintxs[b.id].append(region)
    self.levels[-1].append(region)
    self.bbuffer.append(event)

  def on_end(self, event: RegionEvent):
    """
    Handle Event when sweep-line algorithm encounters
    the ending of a Region.

    Overrides:
      RegionSweep.on_end

    Args:
      event:
        The Region ending Event.
    """
    assert self.is_active
    assert event.kind == RegionSweepEvtKind.End

    region = event.context

    for intersect in self.intersects[region.id]:
      del self.actives[intersect.id]

  def on_done(self, event: RegionEvent):
    """
    Handle Event when sweep-line algorithm completes
    the current iteration.

    Overrides:
      RegionSweep.on_done

    Args:
      event:
        The completion Event.
    """
    RegionSweep.on_done(self, event)

    assert len(self.levels) == self.iteration + 1
    assert isinstance(self.levels[-1], List)

    if len(self.levels[-1]) == 0:
      assert hasattr(event, 'stopiteration')
      event.stopiteration()

    self.intersects = self.nextintxs

  ### Methods: Evaluation

  def evaluate(self, iterations: int = -1, *args, evparams_kw = {}, **kwargs):
    """
    Execute the cyclic multi-pass sweep-line algorithm over the
    attached Timeline. Broadcast Events to the Observers.

    Overrides:
      CycleSweep.evaluate

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
    kwargs = {'evparams_kw': evparams_kw, **kwargs}

    CycleSweep.evaluate(self, iterations, *args, **kwargs)
