#!/usr/bin/env python

"""
Regional Intersection Graph -- NetworkX

This script implements the programming interface for representing
and constructing a NetworkX graph of intersecting or overlapping
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
- NxGraph
"""

from typing import Any, Generic, Iterator, Tuple, TypeVar

from networkx import networkx as nx

from sources.datastructs.datasets.ioable import IOable
from sources.datastructs.rigraphs.rigraph import RIGraph
from sources.datastructs.shapes.region import Region, RegionPair


class NxGraph(RIGraph[nx.Graph], IOable):
  """
  Wrapper for a NetworkX graph of intersecting and overlapping
  Regions. Provides a programming interface for accessing and constructing
  the NetworkX data representation.

  Inherited from RIGraph:

    Attributes:
      G:
        The internal NetworkX graph representation or
        implementation for a graph of intersecting or
        overlapping Regions.

    Properties:
      graph:
        The internal NetworkX graph representation or
        implementation for a graph of intersecting or
        overlapping Regions.

    Overridden Properties:
      regions:
        An Iterator of Regions within the graph along with
        the Region ID or node ID within the graph.
      overlaps:
        An Iterator of overlapping Regions within the
        graph along with the two Region IDs or node IDs
        within the graph for which the two Regions are
        involved.

    Overridden Methods:
      Special:    __init__
      Instance:   put_region
                  put_overlap

  Inherited from IOable:
    Methods:        to_output
    Class Methods:  from_text, from_source
      Overridden:   to_object, from_object
  """

  def __init__(self, dimension: int, graph: nx.Graph = None):
    """
    Initializes the NetworkX graph representation of
    intersecting and overlapping Regions.

    Args:
      dimension:
        The number of dimensions in all of the Regions
        within the graph; the dimensionality of all Regions.
      graph:
        The internal NetworkX graph representation or
        implementation for a graph of intersecting or
        overlapping Regions.
    """
    assert isinstance(dimension, int) and dimension > 0
    assert graph == None or isinstance(graph, nx.Graph)

    self.dimension = dimension

    if graph == None:
      self.G = nx.Graph(dimension=dimension)
    else:
      self.G = graph

  ### Properties: Getters

  @property
  def regions(self) -> Iterator[Tuple[str, Region]]:
    """
    Returns an Iterator of Regions within the graph
    along with the Region ID or node ID within the graph
    as a Tuple.

    Returns:
      An Iterator of Regions and their IDs.
    """
    return self.G.nodes(data='region')

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
    return self.G.edges(data='intersect')

  ### Methods: Insertion

  def put_region(self, region: Region):
    """
    Add the given Region as a newly created node in the graph.

    Args:
      region:
        The Region to be added.
    """
    self.G.add_node(region.id, region=region)

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
    assert isinstance(overlap, Tuple) and len(overlap) == 2
    assert all([isinstance(r, Region) for r in overlap])

    self.G.add_edge(overlap[0].id, overlap[1].id, \
                    intersect=overlap[0].intersect(overlap[1], 'reference'))
