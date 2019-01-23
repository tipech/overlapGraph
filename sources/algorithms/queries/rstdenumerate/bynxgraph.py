#!/usr/bin/env python

"""
Enumeration of subsetted Intersecting Regions by Region
Intersection Graph -- NetworkX

Implements the enumeration of intersecting Regions from a subsetted set of
Regions or intersecting Regions to intersect with a specified Region, via a
Region intersection graph.

Implements the SubsettedEnumByNxGraph class that takes a Region intersection
graph, based on NetworkX and a subset of Regions. Subgraphs the given Region
intersection graph with the given Region subset and enumerates all intersecting
Regions (all cliques) with the generated subgraph.

Implements the NeighboredEnumByNxGraph class that takes a Region intersection
graph, based on NetworkX and a specific Region within the graph. Subgraphs the
given Region intersection graph with the specified Region and its neighbors,
then enumerates all intersecting Regions (all cliques) with the generated
subgraph, and outputs only the intersecting Regions that all intersect with
the specified Region.

The construction of the Region intersection graph is performed via the one-pass
sweep-line algorithm, through a subscription to RegionSweep. The enumeration
outputs an Iterator of the intersecting Regions as tuple of Region intersection
and RegionIntns in order of the number of intersecting Regions involved.

Classes:
- SubsettedEnumByNxGraph
- NeighboredEnumByNxGraph
"""

from typing import Any, Callable, Iterable, Iterator, List, Union

from networkx import networkx as nx

from sources.abstract.pubsub import Subscriber
from sources.algorithms.queries.enumerate import RegionIntersect
from sources.algorithms.queries.enumerate.bynxgraph import EnumerateByNxGraph
from sources.algorithms.rigctor.nxgsweepctor import NxGraphSweepCtor
from sources.datastructs.datasets.regionset import RegionSet
from sources.datastructs.rigraphs.nxgraph import NxGraph
from sources.datastructs.shapes.region import Region, RegionGrp


class SubsettedEnumByNxGraph(EnumerateByNxGraph):
  """
  Enumeration of subsetted intersecting Regions by Region Intersection Graph

  Computes an Iterator of subsetted intersecting Regions by enumerating
  all cliques belonging to a subgraph of the given Region intersection graph.
  Subgraph the given Region intersection graph and enumerates all intersecting
  Regions (all cliques) with the generated subgraph.

  Extends:
    EnumerateByNxGraph

  Attributes:
    subset:
      The list of Region unique identifiers to include
      within the enumeration of intersecting Regions.
  """
  subset: List[str]

  def __init__(self, graph: NxGraph, subset: List[Union[Region, str]]):
    """
    Initialize this computation for enumerating subsetted intersecting
    Regions within the given Region intersection graph and the given
    subset of Regions.

    Args:
      graph:  The NetworkX graph representation of
              intersecting Regions.
      subset: The list of Regions or Region unique
              identifiers to include within the
              enumeration of intersecting Regions.
    """
    assert isinstance(graph, NxGraph)
    assert isinstance(subset, List)
    assert all([isinstance(r, (Region, str)) for r in subset])

    region_id = lambda r: r.id if isinstance(r, Region) else r
    G, subset = graph.G, [region_id(r) for r in subset]

    assert all([isinstance(r, str) and r in G.nodes for r in subset])

    G = nx.subgraph(G, subset)
    EnumerateByNxGraph.__init__(self, NxGraph(graph.dimension, G))
    self.subset = subset

  ### Class Methods: Evaluation

  @classmethod
  def evaluate(cls, context: Union[RegionSet, NxGraph],
                    subset: List[Union[Region, str]],
                    *subscribers: Iterable[Subscriber[RegionGrp]]) \
                    -> Callable[[Any], Iterator[RegionIntersect]]:
    """
    Factory function for computing an Iterator of subsetted intersecting
    Regions using the newly constructed or given Region intersection graph
    by one-pass sweep-line algorithm. Wraps NxGraphSweepCtor.evaluate().

    Overrides:
      EnumerateByNxGraph.evaluate

    Args:
      context:
        RegionSet:  The set of Regions to construct a new
                    Region intersection graph from.
        NxGraph:    The NetworkX graph representation of
                    intersecting Regions.
      subset:       The list of Regions or Region unique
                    identifiers to include within the
                    enumeration of intersecting Regions.
      subscribers:  List of other Subscribers to observe
                    the one-pass sweep-line algorithm.

    Returns:
      A function to evaluate the one-pass sweep-line alg.
      to construct the Region intersecting graph and compute
      the Iterator of subsetted intersecting Regions.

      Args:
        args, kwargs: Arguments for alg.evaluate()

      Returns:
        The resulting Iterator of subsetted
        intersecting Regions.
    """
    assert isinstance(context, (RegionSet, NxGraph))

    def evaluate(*args, **kwargs):
      if isinstance(context, NxGraph):
        return cls(context, subset).results
      else:
        fn = NxGraphSweepCtor.evaluate(context, *subscribers)
        return cls(fn(*args, **kwargs), subset).results

    return evaluate


class NeighboredEnumByNxGraph(SubsettedEnumByNxGraph):
  """
  Enumeration of the intersecting Regions that all intersect with
  a specific Region by Region Intersection Graph

  Computes an Iterator of intersecting Regions that all intersect with a
  specific Region by enumerating all cliques belonging to a subgraph of the
  given Region intersection graph, where the subgraph is generated by only
  keeping the specified Region and its neighbors. The output only includes
  cliques that include the specified Region.

  Extends:
    SubsettedEnumByNxGraph

  Attributes:
    region:
      The specific Region that filters
      resulting intersections.
  """
  region: Region

  def __init__(self, graph: NxGraph, region: Union[Region, str]):
    """
    Initialize this computation for enumerating intersecting
    Regions within the given Region intersection graph that all
    intersect with the given specific Region.

    Args:
      graph:  The NetworkX graph representation of
              intersecting Regions.
      region: The specific Region that filters
              resulting intersections.
    """
    assert isinstance(graph, NxGraph)
    assert isinstance(region, (Region, str))

    region_id = lambda r: r.id if isinstance(r, Region) else r
    G, r = graph.G, region_id(region)

    assert r in G.nodes

    SubsettedEnumByNxGraph.__init__(self, graph, [r, *nx.neighbors(G, r)])
    self.region = G.nodes[r]['region']

  ### Methods: Computations

  def compute(self) -> Iterator[RegionIntersect]:
    """
    The resulting Iterator of intersecting Regions that all intersect with
    the specified Region as tuple of Region intersection and RegionIntns.

    Overrides:
      EnumerateByNxGraph.compute

    Returns:
      The resulting Iterator of intersecting Regions
      that all intersect with the specified Region as
      tuple of Region intersection and RegionIntns.
    """
    for region, intersect in EnumerateByNxGraph.compute(self):
      if self.region in intersect:
        yield (region, intersect)

  ### Class Methods: Evaluation

  @classmethod
  def evaluate(cls, context: Union[RegionSet, NxGraph],
                    region: Union[Region, str],
                    *subscribers: Iterable[Subscriber[RegionGrp]]) \
                    -> Callable[[Any], Iterator[RegionIntersect]]:
    """
    Factory function for computing an Iterator of intersecting Regions that
    all intersect with a specific Region using the newly constructed or given
    Region intersection graph by one-pass sweep-line algorithm.
    Wraps NxGraphSweepCtor.evaluate().

    Overrides:
      EnumerateByNxGraph.evaluate

    Args:
      context:
        RegionSet:  The set of Regions to construct a new
                    Region intersection graph from.
        NxGraph:    The NetworkX graph representation of
                    intersecting Regions.
      region:       The specific Region that filters
                    resulting intersections.
      subscribers:  List of other Subscribers to observe
                    the one-pass sweep-line algorithm.

    Returns:
      A function to evaluate the one-pass sweep-line
      algorithm to construct the Region intersecting graph
      and compute the Iterator of intersecting Regions
      that all intersect with the specified Region.

      Args:
        args, kwargs: Arguments for alg.evaluate()

      Returns:
        The resulting Iterator of intersecting
        Regions that all intersect with the
        specified Region.
    """
    assert isinstance(context, (RegionSet, NxGraph))

    def evaluate(*args, **kwargs):
      if isinstance(context, NxGraph):
        return cls(context, region).results
      else:
        fn = NxGraphSweepCtor.evaluate(context, *subscribers)
        return cls(fn(*args, **kwargs), region).results

    return evaluate
