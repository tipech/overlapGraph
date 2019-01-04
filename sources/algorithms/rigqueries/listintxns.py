#!/usr/bin/env python

"""
Querying List of All Intersecting Regions

This script implements the ListIntxns class that provides methods for
computing the list of all intersecting Regions within a set of Regions.
Each method returns an iterator of RegionIntxns, each of which is a list of
Regions (containing at least or more 2 Regions). The lists are ordered
according to number of Regions involved in the intersections: 2-Region
intersects, 3-Region intersects, up to K-Region intersects, where K is the
maximum number of Regions involved in an intersection, within the RegionSet.

Classes:
- ListIntxns
"""

from dataclasses import dataclass
from typing import Iterator

from networkx import networkx as nx

from sources.algorithms.rigctor.nxgsweepctor import NxGraphSweepCtor
from sources.algorithms.sweepln.msweepln import MSweepln
from sources.algorithms.sweepln.regionmsweep import RegionMSweep
from sources.datastructs.datasets.regionset import RegionSet
from sources.datastructs.rigraphs.nxgraph import NxGraph
from sources.datastructs.shapes.region import Region, RegionIntxn


@dataclass
class ListIntxns:
  """
  A dataclass that implements methods for computing the list of all 
  intersecting Regions within a set of Regions. Each method returns an
  iterator of RegionIntxns, each of which is a list of Regions (containing
  at least or more 2 Regions). The lists are ordered according to number of
  Regions involved in the intersections: 2-Region intersects, 3-Region
  intersects, up to K-Region intersects, where K is the maximum number of
  Regions involved in an intersection, within the RegionSet.

  Attributes:
    regions:
      The RegionSet to list all intersecting Regions.

  Methods:
    Instance: with_rigraph
              with_multisweep
  """
  regions: RegionSet

  ### Methods: Enumeration

  def with_rigraph(self) -> Iterator[RegionIntxn]:
    """
    Compute the list of all intersecting Regions within a set of Regions.
    This method employs to construction of a Region Intersection Graph,
    followed by the enumeration of all of cliques within the graph.
    The graph construction is performed via a one-pass sweep-line algorithm.

    Returns:
      A iterator of intersecting Regions, each
      as a list of Regions.
    """
    nxgsweepctor = NxGraphSweepCtor(self.regions, 'nxgraphctor')
    nxgraph = nxgsweepctor.evaluate()['nxgraphctor']

    for clique in nx.enumerate_all_cliques(nxgraph.G):
      if len(clique) > 1:
        yield list(map(lambda rid: self.regions[rid], clique))

  def with_multisweep(self) -> Iterator[RegionIntxn]:
    """
    Compute the list of all intersecting Regions within a set of Regions.
    This method employs to a multi-pass sweep-line algorithm, where each pass
    computes the intersecting Regions involving increasing number of Regions,
    and generates the Timeline Events in the subsequent passes.
    
    - Starts with 2-Region intersects, as first
      sweep-line pass; generates Events for 3-Region
      candidates, second sweep-line pass;
    - Computes 3-Region intersects, where AB and AC are
      2-Region intersects and ABC is a valid 3-Region
      intersect; generates Events for 4-Region candidates,
      second sweep-line pass;
    - Continues computing intersection Regions with
      increasing number of Regions involved, and generating
      Event for next sweep-line pass, until no Events can
      be generated for next pass.

    Returns:
      A iterator of intersecting Regions, each
      as a list of Regions.
    """
    master = RegionMSweep('regionmsweep')
    msweep = MSweepln(self.regions.timeline, master)

    for intxn in msweep.evaluate()['regionmsweep']:
      yield intxn
