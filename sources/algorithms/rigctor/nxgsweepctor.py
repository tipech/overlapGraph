#!/usr/bin/env python

"""
Regional Intersection Graph (RIG) Construction by
One-pass Sweepline Algorithm -- NetworkX

This script implements the NxGraphSweepCtor (or one-pass sweep-line regional
intersection graph construction algorithm). This algorithm builds an
undirected, labelled graph of all the pair-wise intersections or overlapping
regions between a collection of regions with the same dimensionality. The
graph representation is implemented as a NetworkX graph.

Classes:
- NxGraphSweepCtor
"""

from typing import Tuple

from sources.algorithms.sweepln.regionsweep import RegionSweep, RegionSweepRn
from sources.datastructs.datasets.regionset import RegionSet
from sources.datastructs.rigraphs.nxgraph import NxGraph
from sources.datastructs.shapes.region import Region, RegionPair


class NxGraphSweepCtor(RegionSweepRn, RegionSweep):
  """
  Implementation of regional intersection graph construction based on a one-
  pass sweep-line algorithm. This algorithm builds an undirected, weighted
  graph of all the pair-wise intersections or overlapping regions within a
  RegionSet. Inherits from: RegionSweepRn and RegionSweep. The graph
  representation is implemented as a NetworkX graph.

  Attributes:
    G:
      The NetworkX graph representation of
      intersecting Regions.

  Inherited from RegionSweepRn:
    Attributes:
      runtime, regionset, dimension, actives
    Properties:
      binded, initialized
    Methods:
      Special:  __init__
      Instance: bind, unbind, findoverlaps, addoverlap
    Overridden Methods:
      Special:  __init__
      Instance: oninit, onbegin, onend, onfinalize

  Inherited from RegionSweep:
    Attributes:
      regionset, evaluators
    Methods:
      Special:  __init__
      Instance: put, evaluate
    Overridden Methods:
      Special:  __init__
  """
  G: NxGraph

  def __init__(self, regionset: RegionSet):
    """
    Initialize the intersection graph construction
    by sweep-line algorithm with the given RegionSet.

    Args:
      regionset:
        The RegionSet to evaluate sweep-line over.
    """
    RegionSweepRn.__init__(self)
    RegionSweep.__init__(self, regionset)
    RegionSweep.put(self, self)

  def oninit(self, dimension: int):
    """
    Initialize the evaluation of the RegionSet in the RegionSweep with the
    given dimensions. Create a new intersection Graph and populate it with
    nodes for each Region. This method extends the superclass
    implementation.

    Args:
      dimension:
        The dimension to evaluate sweep-line over.
    """
    RegionSweepRn.oninit(self, dimension)

    self.G = NxGraph(self.regionset.dimension)

    for region in self.regionset:
      self.G.put_region(region)

  def addoverlap(self, regionpair: RegionPair):
    """
    Add the given pair of Regions to the intersection graph as an edge.
    The intersection Region is added to the edge as an data attribute.
    This method overrides in superclass implementation.

    Args:
      regionpair:
        The pair of Regions to add as overlaps.
    """
    assert isinstance(regionpair, Tuple) and len(regionpair) == 2
    assert all([isinstance(r, Region) for r in regionpair])

    self.G.put_overlap(regionpair)

  def onfinalize(self) -> NxGraph:
    """
    When the evaluation is complete, this method is invoked.
    Returns the newly constructed intersection NetworkX graph.
    This method extends the superclass implementation.

    Returns:
      The newly constructed intersection NetworkX graph.
    """
    RegionSweepRn.onfinalize(self)

    return self.G
