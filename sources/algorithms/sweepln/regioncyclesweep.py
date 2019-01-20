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

from typing import Iterator, List, Tuple

from sources.abstract.pubsub import Event
from sources.algorithms.sweepln.cyclesweep import CycleSweep
from sources.algorithms.sweepln.regionsweep import RegionSweep, RegionSweepEvtKind
from sources.datastructs.datasets.regionset import RegionSet
from sources.datastructs.datasets.regiontime import RegionEvent
from sources.datastructs.shapes.region import Region, RegionGrp, RegionIntxn, RegionPair


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
  """
  iteration: int
  levels: List[List[Region]]

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

  ### Methods: Intersections

  def findintersects(self, region: Region) -> Iterator[RegionPair]:
    """
    Return an iterator over all the pairs of overlaps between the
    given Region and the currently active Regions, as RegionPairs.

    Overrides:
      RegionSweep.findintersects

    Args:
      region:   The Region to find pairs of overlaps with
                currently active Regions, as RegionPairs.

    Returns:
      An iterator over all the pairs of overlaps between
      the Region and currently active Regions.
    """
    assert len(self.levels) == self.iteration + 1

    if self.iteration == 0:
      for a, b in RegionSweep.findintersects(self, region):
        yield (a, b)
    else:
      for intersect in self.levels[-2]:
        if intersect[self.dimension].lower > region[self.dimension].lower:
          break
        if region in intersect['intersect']:
          break
        if region.overlaps(intersect):
          yield (intersect, region)

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

    self.levels[-1].append(region)
    self.bbuffer.append(event)

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
