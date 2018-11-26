#!/usr/bin/env python

#
# algorithms/isectgraph.py - Intersection Graph
#
# This script implements the IsectGraph (or Intersection Graph Construction
# Algoritm). This algorithm builds an undirected, weighted (labelled) graph of
# all the pair-wise intersections or overlapping regions between a collection
# of regions with the same dimensionality.
#

from networkx import Graph

from ..datastructs.region import Region, RegionPair
from ..datastructs.regionset import RegionSet
from .sweepline import SweeplineAlg, SweeplineRT


class IsectGraph(SweeplineAlg, SweeplineRT):
  """
  Implementation of the Intersection Graph Construction Algoritm based on a
  single-pass sweepline algorithm. This algorithm builds an undirected, weighted
  graph of all the pair-wise intersections or overlapping regions within a RegionSet.
  Inherits from: SweeplineAlg and SweeplineRT.

  Properties:         graph
  Overridden Methods:
    Special Methods:  __init__
    SweeplineAlg:
      Methods:        oninit, addoverlap, onfinalize
  """
  graph: Graph

  def __init__(self, regionset: RegionSet):
    """
    Initialize the Intersection Graph Construction Algorithm
    with the given RegionSet.

    :param regionset:
    """
    SweeplineAlg.__init__(self)
    SweeplineRT.__init__(self, regionset)
    SweeplineRT.put(self, self)

  def oninit(self, dimension: int):
    """
    Initialize the evaluation of the RegionSet in the SweeplineRT
    with the given dimensions. Create a new intersection Graph and
    populate it with nodes for each Region. This method extends
    the superclass implementation.

    :param dimension:
    """
    SweeplineAlg.oninit(self, dimension)

    self.graph = Graph()

    for region in self.regionset:
      self.graph.add_node(region.id, region=region)

  def addoverlap(self, regionpair: RegionPair):
    """
    Add the given pair of Regions to the intersection graph as an edge.
    The intersection Region is added to the edge as an data attribute.
    This method overrides in superclass implementation.

    :param regionpair:
    """
    self.graph.add_edge(regionpair[0].id, regionpair[1].id, \
                        intersect = regionpair[0].intersect(regionpair[1]))

  def onfinalize(self) -> Graph:
    """
    When the evaluation is complete, this method is invoked.
    Returns the newly constructed intersection Graph.
    This method extends the superclass implementation.
    """
    SweeplineAlg.onfinalize(self)

    return self.graph