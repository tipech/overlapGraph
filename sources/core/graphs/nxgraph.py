#!/usr/bin/env python

"""
Regional Intersection Graph -- NetworkX

Implements the programming interface for representing and constructing a
NetworkX graph of intersecting or overlapping multidimensional Regions. This
data structure represents each Region as a node within the graph and
intersecting Regions between them as edges within the graph.

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

from typing import \
     Any, Callable, Dict, Generic, Iterator, List, Tuple, TypeVar, Union

from networkx import networkx as nx
from networkx.readwrite import json_graph

from sources.abstract import IOable

from ..shapes import Region, RegionId, RegionIdPair, RegionPair
from .rigraph import RIGraph


class NxGraph(RIGraph[nx.Graph], IOable):
  """
  Wrapper for a NetworkX graph of intersecting and overlapping Regions.
  Provides a programming interface for accessing and constructing
  the NetworkX data representation.

  Extends:
    RIGraph[nx.Graph]
    IOable

  Class Attributes:
    NodeRegion:   The data property for the Region
                  associated with each node.
    EdgeRegion:   The data property for the intersecting
                  Region associated with each node.
  """
  NodeRegion = 'region'
  EdgeRegion = 'intersect'

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
    nodekey = self.NodeRegion
    region  = lambda d: d[nodekey] if nodekey in d else None

    for node, data in self.G.nodes(data=True):
      yield (node, region(data), data)

  @property
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
    edgekey   = self.EdgeRegion
    intersect = lambda d: d[edgekey] if edgekey in d else None

    for u, v, data in self.G.edges(data=True):
      yield (u, v, intersect(data), data)

  ### Methods: Private Helpers

  def _convert(self, key: Union[RegionId, RegionIdPair]) -> Union[str, Tuple[str,str]]:
    """
    Converts the given Region or pair of Regions into the corresponding
    Region ID or pair of Region IDs.

    Args:
      key:  The Region or pair of Regions 
            to convert to IDs.

    Returns:
      The Region ID or pair of Region IDs.
    """
    def regionid(r) -> str:
      return r.id if isinstance(r, Region) else r

    if isinstance(key, Tuple) and any([isinstance(k, Region) for k in key]):
      return tuple(regionid(k) for k in key)
    else:
      return regionid(key)

  ### Methods: Queries

  def __getitem__(self, key: Union[RegionId, RegionIdPair]) -> Tuple[Region, Dict]:
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
    get = lambda d, k: d[k] if k in d else None

    if key not in self:
      return None

    key = self._convert(key)

    if isinstance(key, Tuple):
      data = self.G.edges[key]
      region = get(data, self.EdgeRegion)
    else:
      data = self.G.nodes[key]
      region = get(data, self.NodeRegion)

    return (region, data)

  def __delitem__(self, key: Union[RegionId, RegionIdPair]):
    """
    Remove the Region (node) or intersecting Region (edge) associated
    with the given Region ID or pair of Regions IDs within the graph.

    Syntactic Sugar:
      del self[key]

    Args:
      key:  The unique identifier for Region or
            intersecting Region to be removed.
    """
    key = self._convert(key)

    if key not in self:
      return
    elif isinstance(key, Tuple):
      self.G.remove_edge(*key)
    else:
      self.G.remove_node(key)

  def __contains__(self, key: Union[RegionId, RegionIdPair]) -> bool:
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
    key = self._convert(key)

    if isinstance(key, Tuple):
      return key in self.G.edges
    else:
      return key in self.G.nodes

  ### Methods: Insertion

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
    datakey = self.NodeRegion
    self.G.add_node(region.id, **{datakey: region})

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
          and assigns the value as the 'intersect' data
          property. Check if the Regions actually
          intersects; removes edge if not.
        False:
          Don't assign any value as the 'intersect'
          data property.
        Any:
          Value to assign as the 'intersect'
          data property.
      kwargs:
        Additional data properties to be added
        to the newly created edge.
    """
    assert isinstance(overlap, Tuple) and len(overlap) == 2
    assert all([isinstance(r, (Region, str)) for r in overlap])

    region   = lambda r: r if isinstance(r, Region) else self.region(r)
    regionid = lambda r: r.id if isinstance(r, Region) else r
    a, b     = tuple(regionid(r) for r in overlap)

    assert isinstance(a, str) and a in self
    assert isinstance(b, str) and b in self

    if intersect == True:
      intersect = region(a).intersect(region(b), 'reference')
      if intersect is None:
        return

    if (a, b) in self:
      del self[a, b]

    if intersect == False:
      self.G.add_edge(a, b, **kwargs)
    else:
      self.G.add_edge(a, b, intersect=intersect, **kwargs)

  ### Class Methods: Serialization

  @classmethod
  def to_object(cls, object: 'NxGraph', format: str = 'json', **kwargs) -> Any:
    """
    Generates an object (dict, list, or tuple) from the given NxGraph object
    that can be converted or serialized.

    Args:
      object:   The NxGraph object to be converted to an
                object (dict, list, or tuple).
      format:   The output serialization format: 'json'.
      kwargs:   Additional arguments to be used to
                customize and tweak the object generation
                process.

    kwargs:
      json_graph:
        Allowed graph formats: 'node_link' or 'adjacency'.
        If not provided, defaults to: 'node_link'.

    Returns:
      The generated object (dict, list, or tuple).

    Raises:
      ValueError: If json_graph is unsupported format.
    """
    assert isinstance(object, NxGraph) and isinstance(object.G, nx.Graph)
    assert isinstance(object.dimension, int) and object.dimension > 0

    def to_data(G, datafmt):
      method_name = f'{datafmt}_data'
      if hasattr(json_graph, method_name):
        method = getattr(json_graph, method_name)
        assert isinstance(method, Callable)
        return method(G)
      else:
        raise ValueError(f'Unsupported json_graph format.')

    datafmt = kwargs['json_graph'] if 'json_graph' in kwargs else 'node_link'
    data = {
      'dimension': object.dimension,
      'json_graph': datafmt,
      'graph': to_data(object.G, datafmt)
    }

    return data

  ### Class Methods: Deserialization

  @classmethod
  def from_object(cls, object: Any, **kwargs) -> 'NxGraph':
    """
    Construct a new NxGraph object from the conversion of the given object.

    Args:
      object:   The object (dict, list, or tuple)
                to be converted into an NxGraph object.
      kwargs:   Additional arguments for customizing
                and tweaking the NxGraph object
                generation process.

    kwargs:
      json_graph:
        Allowed graph formats: 'node_link' or 'adjacency'.
        If not provided, defaults to: 'node_link'.

    Returns:
      The newly constructed NxGraph object.

    Raises:
      ValueError: If json_graph is unsupported format.
    """
    types = { 'graph': Dict, 'json_graph': str, 'dimension': int }

    assert isinstance(object, Dict)
    assert all([k in object and isinstance(object[k], t) for k, t in types.items()])
    assert object['dimension'] > 0

    def to_graph(data: Dict, datafmt: str) -> nx.Graph:
      method_name = f'{datafmt}_graph'
      if hasattr(json_graph, method_name):
        method = getattr(json_graph, method_name)
        assert isinstance(method, Callable)
        return method(data)
      else:
        raise ValueError(f'Unsupported json_graph format.')

    def to_regions(G: nx.Graph, regions: List[str], edge: Tuple[str, str]) -> List[Region]:
      assert isinstance(regions, List) and len(regions) >= 2
      assert all([isinstance(r, str) for r in regions])
      assert all([r in regions for r in edge])
      assert all([r in G.node for r in regions])

      return list(map(lambda r: G.node[r]['region'], regions))

    nxgraph = NxGraph(object['dimension'])
    nxgraph.G = to_graph(object['graph'], object['json_graph'])
    G = nxgraph.G

    assert nxgraph.dimension == G.graph['dimension']

    # Rematerialize Regions
    for node, region_data in G.nodes(data='region'):
      region = Region.from_object(region_data)
      assert region.dimension == nxgraph.dimension
      G.node[node]['region'] = region

    # Resolve backlinks amongst the edge, Region intersections
    for (u, v, region_data) in G.edges(data='intersect'):
      region = Region.from_object(region_data)
      assert region.dimension == nxgraph.dimension

      if 'intersect' in region:
        region['intersect'] = to_regions(G, region['intersect'], (u, v))
      if 'union' in region:
        region['union'] = to_regions(G, region['union'], (u, v))

      G.edges[u, v]['intersect'] = region

    return nxgraph
