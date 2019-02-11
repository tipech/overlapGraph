#!/usr/bin/env python

"""
Regional Intersection Graph -- Definition

Defines the programming interface for representing and constructing a graph of
intersecting or overlapping multidimensional Regions. This data structure
represents each Region as a node within the graph and intersecting Regions
between them as edges within the graph.

Note:
  Within this script, we make the distinction between
  two similar terms: 'overlap' and 'intersect'.

  overlap:
    The intersection between exactly two Regions.
  intersect:
    The intersection between two or more Regions
    It is more general. An overlap is an intersect,
    but an intersect is not an overlap.

Abstract Classes:
- RIGraph
"""

from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Generic, Iterator, Tuple, TypeVar, Union

from ..shapes import Region, RegionIdPair, RegionPair


G = TypeVar('G')


class RIGraph(Generic[G]): # pylint: disable=E1136
  """
  Abstract Class

  A graph representation of intersecting and overlapping Regions.
  Provides a programming interface for accessing and constructing
  the data representation.

  Attributes:
    id:
      The unique identifier for this RIGraph.
    dimension:
      The number of dimensions in all of the Regions
      within the graph; the dimensionality of all Regions.
    G:
      The internal graph representation or implementation
      for a graph of intersecting or overlapping Regions.
  """
  __metaclass__ = ABCMeta

  id: str
  dimension: int
  G: G

  @abstractmethod
  def __init__(self, dimension: int, graph: G = None, id: str = ''):
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
      id:
        The unique identifier for this RIGraph.
        Randonly generated with UUID v4, if not provided.
    """
    raise NotImplementedError

  ### Properties: Getters

  @property
  def graph(self) -> G:
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
  @abstractmethod
  def regions(self) -> Iterator[Tuple[str, Region, Dict]]:
    """
    Returns an Iterator of Regions within the graph
    along with the Region ID or node ID and any additional
    associated data properties for each node within the graph
    as a Tuple.

    Returns:
      An Iterator of Regions, their IDs and
      their node's data properties.
    """
    raise NotImplementedError

  @property
  @abstractmethod
  def overlaps(self) -> Iterator[Tuple[str, str, Region, Dict]]:
    """
    Returns an Iterator of overlapping Regions within the graph
    along with the two Region IDs or node IDs within the graph
    for which the two Regions are involved as a Tuple. Includes
    any additional associated data properties for each edge within
    the graph as the last field in the Tuple.

    Returns:
      An Iterator of overlapping Regions, the
      Region IDs of the two Regions involved, and
      the edge's data properties.
    """
    raise NotImplementedError

  ### Methods: Queries

  @abstractmethod
  def __getitem__(self, key: Union[str, Tuple[str,str]]) -> Tuple[Region, Dict]:
    """
    Retrieve the Region or intersecting Region for the given Region ID or
    pair of Region IDs. Also, retrieves the data properties for the Region
    (node) or intersecting Region (edge). Returns None if Region or
    intersecting Region is not contained as node or edge within the graph.

    Syntactic Sugar:
      self[key]

    Args:
      key:  The unique identifier for Region or
            intersecting Region to be retrieved.
    
    Returns:
      The retrieved Region or intersecting Region
      and the associated data properties.
      None, if Region or intersecting Region is not
      contained as node or edge within the graph.
    """
    raise NotImplementedError

  @abstractmethod
  def __delitem__(self, key: Union[str, Tuple[str,str]]):
    """
    Remove the Region (node) or intersecting Region (edge) associated
    with the given Region ID or pair of Regions IDs within the graph.

    Syntactic Sugar:
      del self[key]

    Args:
      key:  The unique identifier for Region or
            intersecting Region to be removed.
    """
    raise NotImplementedError

  @abstractmethod
  def __contains__(self, key: Union[str, Tuple[str,str]]) -> bool:
    """
    Determine if the given Region ID or pair of Regions IDs are
    contained as nodes or edges within the graph.

    Syntactic Sugar:
      key in self

    Args:
      key:    The unique identifier for Region or
              intersecting Region to be queried.

    Returns:
      True:   If Region or intersecting Region is
              contained as node or edge within the graph.
      False:  Otherwise.
    """
    raise NotImplementedError

  def region(self, key: Union[str, Tuple[str,str]]) -> Region:
    """
    Retrieve the Region or intersecting Region for the given Region ID or
    pair of Region IDs. Returns None if Region or intersecting Region is not
    contained as node or edge within the graph.

    Syntactic Sugar:
      self[key][0]

    Args:
      key:  The unique identifier for Region or
            intersecting Region to be retrieved.
    
    Returns:
      The retrieved Region or intersecting Region.
      None, if Region or intersecting Region is not
      contained as node or edge within the graph.
    """
    if key in self:
      return self[key][0]
    else:
      return None

  def data(self, key: Union[str, Tuple[str,str]]) -> Dict:
    """
    Retrieve the data properties for the given Region ID or pair of Region IDs.
    Returns None if Region or intersecting Region is not contained as node
    or edge within the graph.

    Syntactic Sugar:
      self[key][1]

    Args:
      key:  The unique identifier for Region or
            intersecting Region's data properties
            to be retrieved.

    Returns:
      The retrieved data properties.
      None, if Region or intersecting Region is not
      contained as node or edge within the graph.
    """
    if key in self:
      return self[key][1]
    else:
      return None

  ### Methods: Insertion

  @abstractmethod
  def put_region(self, region: Region, **kwargs):
    """
    Add the given Region as a newly created node in the graph.

    Args:
      region:
        The Region to be added.
      kwargs:
        Additional data properties to be added
        to the newly created node.
    """
    raise NotImplementedError

  @abstractmethod
  def put_overlap(self, overlap: RegionIdPair, intersect = True, **kwargs):
    """
    Add the given pair of Regions as a newly created edge in the graph.
    The two regions must be intersecting or overlapping.

    Args:
      overlap:
        The pair of Regions or Region IDs to be
        added as an intersection.
      intersect:
        True:
          Computes the intersect between the pair of Regions
          and assigns the value as the 'intersect' data property.
          Check if the Regions actually intersects;
          removes edge if not.
        False:
          Don't assign any value as the 'intersect' data property.
        Any:
          Value to assign as the 'intersect' data property.
      kwargs:
        Additional data properties to be added
        to the newly created edge.
    """
    raise NotImplementedError
