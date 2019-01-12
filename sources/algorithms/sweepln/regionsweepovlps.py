#!/usr/bin/env python

"""
Compute Region Pairwise Overlaps by One-pass Sweep-line Algorithm

Implements the RegionSweepOverlaps class that computes a list of all of the
pairwise overlapping Regions using the one-pass sweep-line algorithm, through
a subscription to RegionSweep.

Classes:
- RegionSweepOverlaps
"""

from typing import Any, Callable, Iterable, List, Tuple, Union

from sources.algorithms.sweepln.basesweep import SweepTaskRunner
from sources.algorithms.sweepln.regionsweep import RegionSweep, RegionSweepEvtKind
from sources.datastructs.abstract.pubsub import Event, Subscriber
from sources.datastructs.datasets.regionset import RegionSet
from sources.datastructs.datasets.regiontime import RegionEvent
from sources.datastructs.shapes.region import Region, RegionGrp, RegionPair


class RegionSweepOverlaps(SweepTaskRunner[RegionGrp, List[RegionPair]]):
  """
  Computes a list of all of the pairwise overlapping Regions
  using the one-pass sweep-line algorithm, through a subscription
  to RegionSweep.

  Extends:
    SweepTaskRunner[RegionGrp, List[RegionPair]]

  Attributes:
    overlaps:
      The List of pairwise overlapping Regions.
  """
  overlaps: List[RegionPair]

  def __init__(self):
    """
    Initialize this class to compute a list of all of the pairwise
    overlapping Regions using the one-pass sweep-line algorithm.
    Sets the events as RegionSweepEvtKind.
    """
    Subscriber.__init__(self, RegionSweepEvtKind)

    self.overlaps = None

  ### Properties

  @property
  def results(self) -> List[RegionPair]:
    """
    The resulting List of pairwise overlapping Regions.
    Alias for: self.overlaps

    Returns:
      The resulting List of pairwise
      overlapping Regions.
    """
    return self.overlaps

  ### Methods: Event Handlers

  def on_init(self, event: RegionEvent):
    """
    Handle Event when sweep-line algorithm initializes.

    Args:
      event:
        The initialization Event.
    """
    assert event.kind == RegionSweepEvtKind.Init

    self.overlaps = []

  def on_intersect(self, event: Event[RegionPair]):
    """
    Handle Event when sweep-line algorithm encounters
    the two or more Regions intersecting.

    Args:
      event:
        The intersecting Regions Event.
    """
    assert event.kind == RegionSweepEvtKind.Intersect
    assert isinstance(event.context, Tuple) and len(event.context) == 2
    assert all([isinstance(r, Region) for r in event.context])

    self.overlaps.append(event.context)

  ### Class Methods: Evaluation

  @classmethod
  def evaluate(cls, context: Union[RegionSet, RegionSweep] = None,
                    *subscribers: Iterable[Subscriber[RegionGrp]]) \
                    -> Callable[[Any], List[RegionPair]]:
    """
    Factory function for computes a list of all of the pairwise overlapping
    Regions using the one-pass sweep-line algorithm.

    Overrides:
      SweepTaskRunner.evaluate

    Args:
      context:
        Region:
          The set of Regions to compute the list of
          the pairwise overlapping Regions from.
        RegionSweep:
          An existing instance of the one-pass
          sweep-line algorithm. If None, constructs
          a new RegionSweep instance.
      subscribers:
        The other Subscribers to observe the
        one-pass sweep-line algorithm.

    Returns:
      A function to evaluate the one-pass sweep-line
      algorithm and compute the list of the pairwise
      overlapping Regions.

      Args:
        args, kwargs:
          Arguments for alg.evaluate()

      Returns:
        The resulting List of pairwise
        overlapping Regions.
    """
    assert isinstance(context, (RegionSet, RegionSweep))

    kwargs = {'subscribers': subscribers}

    if isinstance(context, RegionSet):
      alg = RegionSweep
      kwargs['alg_args'] = [context]
    else:
      alg = context

    return SweepTaskRunner.evaluate(cls, alg, **kwargs)
