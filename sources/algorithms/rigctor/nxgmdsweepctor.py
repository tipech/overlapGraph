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

from typing import Any, Callable, Iterable, List, Tuple

from sources.abstract import Event, Subscriber
from sources.core import \
     Interval, NxGraph, Region, RegionGrp, RegionPair, RegionSet

from ..sweepln import RegionMdSweep, RegionSweepEvtKind, SweepTaskRunner
from .nxgsweepctor import NxGraphSweepCtor


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
    assert 0 <= event.dimension < self.dimension

    default = [None]*self.dimension
    dim_intersect = lambda a, b, d: a[d].intersect(b[d])

    if event.context in self.G:
      intersect, data = self.G[event.context]
      dim = data.get('dimensions', default)
    else:
      intersect = None
      dim = default

    dim[event.dimension] = dim_intersect(*event.context, event.dimension)
    self.G.put_overlap(event.context, intersect=intersect, dimensions=dim)

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
    for a, b, intersect, data in list(G.overlaps):
      # Buffer G.overlaps into a list to prevent 'dictionary changed size
      # during iteration' runtime error.
      if intersect is not None:
        continue

      if 'dimensions' in data:
        dim = data['dimensions']
        assert isinstance(dim, List) and len(dim) == self.dimension
        if all([isinstance(d, Interval) for d in dim]):
          intersect = Region.from_intervals(dim)
          intersect['intersect'] = [G.region(a), G.region(b)]
          G.put_overlap((a, b), intersect=intersect)
          continue

      # 'dimensions' not in data OR any([d is None for d in dim])
      del G[a, b]

  ### Class Methods: Evaluation

  @classmethod
  def prepare(cls, regions: RegionSet,
                   *subscribers: Iterable[Subscriber[RegionGrp]]) \
                   -> Callable[[Any], NxGraph]:
    """
    Factory function for constructing a new Region intersecting graph, based
    on NetworkX, using the multi-dimensional sweep-line algorithm.

    Overrides:
      NxGraphSweepCtor.prepare

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
    return SweepTaskRunner.prepare(cls, RegionMdSweep, **{
      'subscribers': subscribers,
      'alg_args': [regions],
      'task_args': [regions]
    })
