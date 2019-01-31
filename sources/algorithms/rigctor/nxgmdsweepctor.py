#!/usr/bin/env python

"""
Regional Intersection Graph (RIG) Construction by Multi-dimensional
(Non-threaded) Sweep-line Algorithm -- NetworkX

Implements the NxGraphMdSweepCtor (or multi-dimensional sweep-line regional
intersection graph construction algorithm). This algorithm builds an undirected,
labelled graph of all the pair-wise intersections or overlapping regions
between a collection of regions with the same dimensionality.

- The algorithm first generates a graph of overlapping Region in the first
  dimesnion, with edges with weights of 1.
- Each subsequent dimension, increment the graph edges with each overlap.
- After all dimensions, prune all edges that do not have a weight equal to the
  dimensionality of the Regions.

The graph representation is implemented as a NetworkX graph.

Classes:
- NxGraphMdSweepCtor
"""

from typing import Any, Callable, Iterable, Tuple

from sources.abstract.pubsub import Event, Subscriber
from sources.algorithms.rigctor.nxgsweepctor import NxGraphSweepCtor
from sources.algorithms.sweepln.basesweep import SweepTaskRunner
from sources.algorithms.sweepln.regionsweep import RegionSweepEvtKind
from sources.algorithms.sweepln.regionmdsweep import RegionMdSweep
from sources.datastructs.datasets.regionset import RegionSet
from sources.datastructs.rigraphs.nxgraph import NxGraph
from sources.datastructs.shapes.region import Region, RegionGrp, RegionPair


class NxGraphMdSweepCtor(NxGraphSweepCtor):
  """
  Implementation of regional intersection graph construction based on a multi-
  dimensional sweep-line algorithm. This algorithm builds an undirected,
  weighted graph of all the pair-wise intersections or overlapping regions
  within a RegionSet, through a subscription to RegionMdSweep.

  - The algorithm first generates a graph of overlapping
    Region in the first dimesnion, with edges with
    weights of 1.
  - Each subsequent dimension, increment the graph edges
    with each overlap.
  - After all dimensions, prune all edges that do not have
    a weight equal to the dimensionality of the Regions.

  The graph representation is implemented as a NetworkX graph.

  Extends:
    NxGraphSweepCtor
  """

  ### Properties

  @property
  def dimension(self) -> int:
    """
    The number of dimensions in each Region (dimensionality).

    Returns:
      The dimensionality of the Regions.
    """
    return self.regions.dimension

  ### Methods: Event Handlers

  def on_intersect(self, event: Event[RegionPair]):
    """
    Handle Event when sweep-line algorithm encounters the two or more
    Regions intersecting. Add the given Event's context, pairs of Regions,
    to the intersection graph as an edge. The intersection Region is added
    to the edge as an data attribute.

    Overrides:
      NxGraphSweepCtor.on_intersect

    Args:
      event:
        The intersecting Regions Event.
    """
    assert event.kind == RegionSweepEvtKind.Intersect
    assert isinstance(event.context, Tuple) and len(event.context) == 2
    assert all([isinstance(r, Region) for r in event.context])

    self.G.put_temporary_overlap(event.context)

  def on_completed(self):
    """
    The Event handler when no more Events.
    Subscription completed and finalize the overlaps.

    The overlaps that have same 'count' as the Region dimensionality, replace
    'count' with Region intersection between the two Regions for that edge.
    The overlaps that have 'count' that is less than the Region
    dimensionality, remove the edge.

    Overrides:
      Subscriber.on_completed
    """
    G = self.G
    for a, b, _ in list(G.overlaps):
      G.finalize_overlap((a, b))

  ### Class Methods: Evaluation

  @classmethod
  def evaluate(cls, regions: RegionSet,
                    *subscribers: Iterable[Subscriber[RegionGrp]]) \
                    -> Callable[[Any], NxGraph]:
    """
    Factory function for constructing a new Region intersecting graph, based
    on NetworkX, using the multi-dimensional sweep-line algorithm.

    Overrides:
      NxGraphSweepCtor.evaluate

    Args:
      regions:
        The set of Regions to construct a new
        Region intersection graph from.
      subscribers:
        List of other Subscribers to observe the
        multi-dimensional sweep-line algorithm.

    Returns:
      A function to evaluate the multi-dimensional
      sweep-line algorithm and construct the NetworkX-based
      Region intersection graph.

      Args:
        args, kwargs:
          Arguments for alg.evaluate()

      Returns:
        The newly constructed NetworkX-based
        Region intersection graph.
    """
    assert isinstance(regions, RegionSet)
    return SweepTaskRunner.evaluate(cls, RegionMdSweep, **{
      'subscribers': subscribers,
      'alg_args': [regions],
      'task_args': [regions]
    })
