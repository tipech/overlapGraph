#!/usr/bin/env python

"""
Regional Intersection Graph (RIG) Construction by
One-pass Sweep-line Algorithm -- NetworkX

Implements the NxGraphSweepCtor (or one-pass sweep-line regional intersection
graph construction algorithm). This algorithm builds an undirected, labelled
graph of all the pair-wise intersections or overlapping regions between a
collection of regions with the same dimensionality. The graph representation
is implemented as a NetworkX graph.

Classes:
- NxGraphSweepCtor
"""

from typing import Any, Callable, Iterable, Tuple, Union

from sources.abstract.pubsub import Event, Subscriber
from sources.algorithms.sweepln.basesweep import SweepTaskRunner
from sources.algorithms.sweepln.regionsweep import RegionSweep, RegionSweepEvtKind
from sources.datastructs.datasets.regionset import RegionSet
from sources.datastructs.rigraphs.nxgraph import NxGraph
from sources.datastructs.shapes.region import Region, RegionGrp, RegionPair


class NxGraphSweepCtor(SweepTaskRunner[RegionGrp, NxGraph]):
  """
  Implementation of regional intersection graph construction based on a one-
  pass sweep-line algorithm. This algorithm builds an undirected, weighted
  graph of all the pair-wise intersections or overlapping regions within a
  RegionSet, through a subscription to RegionSweep.

  The graph representation is implemented as a NetworkX graph.

  Extends:
    SweepTaskRunner[RegionGrp, NxGraph]

  Attributes:
    G:
      The NetworkX graph representation of
      intersecting Regions.
    regions:
      The RegionSet to construct the Region
      intersection graph from.
  """
  regions: RegionSet
  G: NxGraph

  def __init__(self, regions: RegionSet):
    """
    Initialize the intersection graph construction
    using the one-pass sweep-line algorithm.
    Sets the events as RegionSweepEvtKind.

    Args
      regions:
        The RegionSet to construct the Region
        intersection graph from.
    """
    Subscriber.__init__(self, RegionSweepEvtKind)

    self.regions = regions
    self.G = NxGraph(self.regions.dimension)

    for region in self.regions:
      self.G.put_region(region)

  ### Properties

  @property
  def results(self) -> NxGraph:
    """
    The resulting NetworkX graph of intersecting Regions.
    Alias for: self.G.

    Returns:
      The newly constructed NetworkX graph of
      intersecting Regions.
    """
    return self.G

  ### Methods: Event Handlers

  def on_intersect(self, event: Event[RegionPair]):
    """
    Handle Event when sweep-line algorithm encounters the two or more
    Regions intersecting. Add the given Event's context, pairs of Regions,
    to the intersection graph as an edge. The intersection Region is added
    to the edge as an data attribute.

    Args:
      event:
        The intersecting Regions Event.
    """
    assert event.kind == RegionSweepEvtKind.Intersect
    assert isinstance(event.context, Tuple) and len(event.context) == 2
    assert all([isinstance(r, Region) for r in event.context])

    self.G.put_overlap(event.context)

  ### Class Methods: Evaluation

  @classmethod
  def evaluate(cls, context: Union[RegionSet, RegionSweep] = None,
                    *subscribers: Iterable[Subscriber[RegionGrp]]) \
                    -> Callable[[Any], NxGraph]:
    """
    Factory function for constructing a new Region intersecting graph, based
    on NetworkX, using the one-pass sweep-line algorithm.

    Overrides:
      SweepTaskRunner.evaluate

    Args:
      context:
        Region:
          The set of Regions to construct a new
          Region intersection graph from.
        RegionSweep:
          An existing instance of the one-pass
          sweep-line algorithm. If None, constructs
          a new RegionSweep instance.
      subscribers:
        List of other Subscribers to observe the
        one-pass sweep-line algorithm.

    Returns:
      A function to evaluate the one-pass sweep-line
      algorithm and construct the NetworkX-based
      Region intersection graph.

      Args:
        args, kwargs:
          Arguments for alg.evaluate()

      Returns:
        The newly constructed NetworkX-based
        Region intersection graph.
    """
    assert isinstance(context, (RegionSet, RegionSweep))

    kwargs = {'subscribers': subscribers}

    if isinstance(context, RegionSet):
      kwargs['alg_args']  = [context]
      kwargs['task_args'] = [context]
      alg = RegionSweep
    else:
      kwargs['task_args'] = [context.regions]
      alg = context

    return SweepTaskRunner.evaluate(cls, alg, **kwargs)
