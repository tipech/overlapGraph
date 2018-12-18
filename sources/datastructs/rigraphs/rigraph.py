#!/usr/bin/env python

"""
Regional Intersection Graph -- Definition

This script defines the programming interface for representing
and constructing a graph of intersecting or overlapping
multidimensional Regions. This data structure represents each Region
as a node within the graph and intersecting Regions between them as
edges within the graph.

Note:
  Within this script, we make the distinction between
  two similar terms: 'overlap' and 'intersect'.

  overlap:
    The intersection between exactly two Regions.
  intersect:
    The intersection between two or more Regions
    It is more general. An overlap is an intersect,
    but an intersect is not an overlap.

Classes:
- RIGraph
"""

from typing import Any, Generic, Iterator, Tuple, TypeVar

from sources.datastructs.shapes.region import Region, RegionPair


Graph = TypeVar('Graph')

class RIGraph(Generic[Graph]):
  """
  Abstract class for a graph representation of intersecting and overlapping
  Regions. Provides a programming interface for accessing and constructing
  the data representation.

  Attributes:
    G:
      The internal graph representation or implementation
      for a graph of intersecting or overlapping Regions.
    dimension:
      The number of dimensions in all of the Regions 
      within the graph; the dimensionality of all Regions.

  Abstract Properties:
    graph:
      The internal graph representation or implementation
      for a graph of intersecting or overlapping Regions.
    regions:
      An Iterator of Regions within the graph along with
      the Region ID or node ID within the graph.
    overlaps:
      An Iterator of overlapping Regions within the graph
      along with the two Region IDs or node IDs within the
      graph for which the two Regions are involved.

  Abstract Methods:
    Special:    __init__
    Instance:   put_region
                put_overlap
  """
  G: Graph
  dimension: int

  def __init__(self, dimension: int, graph: Graph = None):
    """
    Initializes the graph representation of intersecting
    and overlapping Regions.

    Args:
      dimension:
        The number of dimensions in all of the Regions 
        within the graph; the dimensionality of all Regions.
      graph:
        The internal graph representation or implementation
        for a graph of intersecting or overlapping Regions.
    """
    raise NotImplementedError

  ### Properties: Getters

  @property
  def graph(self) -> Graph:
    """
    The internal graph representation or implementation for
    a graph of intersecting or overlapping Regions.
    
    Alias for:
      self.G

    Returns:
      The internal graph representation.
    """
    return self.G

  @property
  def regions(self) -> Iterator[Tuple[str, Region]]:
    """
    Returns an Iterator of Regions within the graph
    along with the Region ID or node ID within the graph
    as a Tuple.

    Returns:
      An Iterator of Regions and their IDs.
    """
    raise NotImplementedError

  @property
  def overlaps(self) -> Iterator[Tuple[str, str, Region]]:
    """
    Returns an Iterator of overlapping Regions within the graph
    along with the two Region IDs or node IDs within the graph
    for which the two Regions are involved as a Tuple.

    Returns:
      An Iterator of overlapping Regions and
      the Region IDs of the two Regions involved.
    """
    raise NotImplementedError

  ### Methods: Insertion

  def put_region(self, region: Region):
    """
    Add the given Region as a newly created node in the graph.

    Args:
      region:
        The Region to be added.
    """
    raise NotImplementedError

  def put_overlap(self, overlap: RegionPair, **kwargs):
    """
    Add the given pair of Regions as a newly created edge in the graph.
    The two regions must be intersecting or overlapping.

    Args:
      overlap:
        The pair of Regions to be added
        as an intersection.
      kwargs:
        Additional arguments.
    """
    raise NotImplementedError
