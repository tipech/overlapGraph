#!/usr/bin/env python

"""
Regional Intersection Graph

Implements the programming interface for representing and constructing a
graph of intersecting or overlapping multidimensional Regions. This data
structure represents each Region as a node within the graph and intersecting
Regions between them as edges within the graph.

Classes:
- 
"""

from typing import Any, Callable, Dict, Iterator, List, Tuple, Union
from uuid import uuid4

from networkx import networkx as nx
from networkx.readwrite import json_graph

from sources.abstract import IOable

from ..shapes import Region, RegionId, RegionIdPair, RegionPair
from .rigraph import RIGraph


class RIGraph(IOable):
  """
  A graph representation of intersecting and overlapping Regions.
  Provides a programming interface for accessing and constructing
  the data representation.

  Extends:
    IOable

  Class Attributes:
    id:
      The unique identifier for this RIGraph.
    dimension:
      The number of dimensions in all of the Regions
      within the graph; the dimensionality of all Regions.
    G:
      The internal graph representation or implementation
      for a graph of intersecting or overlapping Regions.
    NodeRegion:   The data property for the Region
                  associated with each node.
    EdgeRegion:   The data property for the intersecting
                  Region associated with each node.
  """
  id: str
  dimension: int
  G: G
  datakey = 'region'

  def __init__(self, dimension: int, graph: nx.Graph = None, id: str = ''):
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
      id:
        The unique identifier for this RIGraph.
        Randonly generated with UUID v4, if not provided.
    """
    assert dimension > 0

    # TODO maybe add 'assert all(isinstance( self.G.nodes(... , Region)))' ?

    self.dimension = dimension
    self.id = id = id if len(id) > 0 else str(uuid4())

    if graph == None:
      self.G = nx.Graph()
    else:
      self.G = graph


  ### Properties: Getters

  @property
  def regions(self) -> Iterator[Region]:
    """
    Returns an Iterator of Regions within the graph.

    Returns:
      An Iterator of Regions.
    """

    for _, region in self.G.nodes(data=self.datakey):
      yield region


  @property
  def intersections(self) -> Iterator[Region]:
    """
    Returns an Iterator of intersecting Regions within the graph.

    Returns:
      An Iterator of overlapping Regions.
    """

    for _, _, region in self.G.edges(data=self.datakey):
      yield region


  ### Methods: Queries

  def __getitem__(self, key: Union[str, RegionIdPair]) -> Tuple[Region, Dict]:
    """
    Retrieve the Region or intersecting Region for the given Region ID or
    pair of Region IDs. Returns None if Region or intersecting Region is not
    contained as node or edge within the graph.

    Syntactic Sugar:
      self[key]

    Args:
      key:  The unique identifier for Region or
            intersecting Region to be retrieved.
    
    Returns:
      The retrieved Region or intersecting Region.
      None, if Region or intersecting Region is not
      contained as node or edge within the graph.
    """

    if key not in self:
      return None

    key = self._convert(key)

    if isinstance(key, Tuple):
      return self.G.edges[key][self.datakey]
    else:
      return self.G.nodes[key][self.datakey]


  def __delitem__(self, key: Union[str, RegionIdPair]):
    """
    Remove the Region (node) or intersecting Region (edge) associated
    with the given Region ID or pair of Regions IDs within the graph.

    Syntactic Sugar:
      del self[key]

    Args:
      key:  The unique identifier for Region or
            intersecting Region to be removed.
    """

    if key not in self:
      return

    elif isinstance(key, Tuple):
      self.G.remove_edge(*key)
    else:
      self.G.remove_node(key)


  def __len__(self) -> int:
    """
    Determine the size of this graph. The size of this graph
    is measured by the number of nodes (or Regions) within graph.

    Returns:
      The number of Regions as nodes
      within this graph.
    """
    return len(self.G)


  def __contains__(self, key: Union[str, RegionIdPair]) -> bool:
    """
    Determine if the given Region ID or pair of Regions IDs are
    contained as nodes or edges within the graph.

    Syntactic Sugar:
      key in self

    Args:
      key:    The unique identifier for Region.

    Returns:
      True:   If Region or intersecting Region is
              contained as node or edge within the graph.
      False:  Otherwise.
    """

    if isinstance(key, Tuple):
      return key in self.G.edges
    else:
      return key in self.G.nodes


  def region(self, key: Union[str, Tuple[str,str]]) -> Region:
    """
    Retrieve the Region or intersecting Region for the given Region ID or
    pair of Region IDs. Returns None if Region or intersecting Region is not
    contained as node or edge within the graph.

    Args:
      key:  The unique identifier for Region or
            intersecting Region to be retrieved.
    
    Returns:
      The retrieved Region or intersecting Region.
      None, if Region or intersecting Region is not
      contained as node or edge within the graph.
    """
    if key in self:
      return self[key][datakey]
    else:
      return None


  ### Methods: Insertion

  def put_region(self, region: Region):
    """
    Add the given Region as a newly created node in the graph.

    Args:
      region:
        The Region to be added.
    """

    self.G.add_node(region.id, **{self.datakey: region})


  def put_overlap(self, overlap: Union[Tuple[Region, Region], RegionIdPair]):
    """
    Add the given pair of Regions as a newly created edge in the graph.
    The two regions must be intersecting or overlapping.

    Args:
      overlap:
        The pair of Regions or Region IDs to be
        added as an intersection.
    """

    region   = lambda r: r if isinstance(r, Region) else self.region(r)
    regionid = lambda r: r.id if isinstance(r, Region) else r
    a, b     = tuple(regionid(r) for r in overlap)

    assert isinstance(a, str) and a in self
    assert isinstance(b, str) and b in self

    if intersect == True:
      intersect = region(a).is_intersecting(region(b))
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
      'id': object.id,
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

    Keyword Args:
      id:
        The unique identifier for the generated RIGraph.
      json_graph:
        Allowed graph formats: 'node_link' or 'adjacency'.
        If not provided, defaults to: 'node_link'.

    Returns:
      The newly constructed NxGraph object.

    Raises:
      ValueError: If json_graph is unsupported format.
    """
    types = { 'graph': Dict, 'json_graph': str, 'dimension': int, 'id': str }

    assert isinstance(object, Dict)
    assert all([k in object and isinstance(object[k], t) for k, t in types.items()])
    assert object['dimension'] > 0 and len(object['id']) > 0

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

    graph   = to_graph(object['graph'], object['json_graph'])
    graphid = kwargs.get('id', object['id'])
    nxgraph = NxGraph(object['dimension'], graph, id=graphid)
    G       = nxgraph.G

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
