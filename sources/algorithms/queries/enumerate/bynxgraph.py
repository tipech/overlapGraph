#!/usr/bin/env python

"""
Enumeration of all Intersecting Regions by Region 
Intersection Graph -- NetworkX

Implements the EnumerateByNxGraph class that takes a Region intersection graph,
based on NetworkX, and enumerates all intersecting Regions (all cliques).
Implements the EnumerateByNxGSweepCtor class that first constructs a Region
intersection graph, based on NetworkX, and enumerates all intersecting Regions
(all cliques). The construction of the Region intersection graph is performed
via the one-pass sweep-line algorithm, through a subscription to RegionSweep.
The enumeration outputs an Iterator of the intersecting Regions as tuple of
Region intersection and RegionIntns in order of the number of intersecting
Regions involved.

Classes:
- EnumerateByNxGraph
- EnumerateByNxGSweepCtor
"""

from typing import Iterator

from networkx import networkx as nx

from sources.algorithms.queries.enumerate import EnumerateRegionIntersect, RegionIntersect
from sources.algorithms.rigctor.nxgsweepctor import NxGraphSweepCtor
from sources.datastructs.rigraphs.nxgraph import NxGraph
from sources.datastructs.shapes.region import Region


class EnumerateByNxGraph:
  """
  Enumeration of all intersecting Regions by Region Intersection Graph

  Computes an Iterator of all of the intersecting Regions by enumerating
  all cliques belonging to a given Region intersection graph.

  Attributes:
    G:
      The NetworkX graph representation of
      intersecting Regions.
  """
  G: NxGraph

  def __init__(self, G: NxGraph):
    """
    Initialize this computation for enumerating all of the intersecting
    Regions within the given Region intersection graph.

    Args:
      G:
        The NetworkX graph representation of
        intersecting Regions.
    """
    self.G = G

  ### Properties

  @property
  def results(self) -> Iterator[RegionIntersect]:
    """
    The resulting Iterator of intersecting Regions as tuple of
    Region intersection and RegionIntns.

    Returns:
      The resulting Iterator of intersecting Regions as
      tuple of Region intersection and RegionIntns.
    """
    yield from self.compute()

  ### Methods: Computations

  def compute(self) -> Iterator[RegionIntersect]:
    """
    The resulting Iterator of intersecting Regions as tuple of
    Region intersection and RegionIntns.

    Returns:
      The resulting Iterator of intersecting Regions as
      tuple of Region intersection and RegionIntns.
    """
    graph = self.G

    for clique in nx.enumerate_all_cliques(graph.G):
      if len(clique) > 1:
        intersect = [graph.G.nodes[r]['region'] for r in clique]
        region    = Region.from_intersect(intersect, linked=True)

        assert isinstance(region, Region)
        yield (region, intersect)


class EnumerateByNxGSweepCtor(NxGraphSweepCtor, EnumerateRegionIntersect):
  """
  Enumeration of all intersecting Regions by Graph Construction
  with One-pass Sweep-line Algorithm

  Computes an Iterator of all of the intersecting Regions via graph
  construction with one-pass sweep-line algorithm, through a subscription
  to RegionSweep.

  Extends:
    NxGraphSweepCtor
    SweepTaskRunner[RegionGrp, Iterator[RegionIntersect]]
  """

  ### Properties

  @property
  def results(self) -> Iterator[RegionIntersect]:
    """
    The resulting Iterator of intersecting Regions as tuple of
    Region intersection and RegionIntns.

    Overrides:
      NxGraphSweepCtor.results

    Returns:
      The resulting Iterator of intersecting Regions as
      tuple of Region intersection and RegionIntns.
    """
    return EnumerateByNxGraph(self.G).results
