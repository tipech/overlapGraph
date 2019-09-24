#!/usr/bin/env python

"""
Sweep Line using Intersection Graph

Implements the SLIG (Sweep Line using Intersection Graph) algorithm. This
algorithm builds an undirected, labelled graph of all the pair-wise
intersections or overlapping regions between a collection of regions
with the same dimensionality.

Classes:
- SLIG
"""
from pprint import pprint
from networkx import networkx as nx
from slig.datastructs import Region, RegionSet, RIGraph

LOWER = False
UPPER = True

class SLIG():
  """
  Implementation of regional intersection graph construction based on a one-
    pass sweep-line algorithm. This algorithm builds an undirected, weighted
    graph of all the pair-wise intersections or overlapping regions within a
    set of Region objects.

    Attributes:
      G:
        The NetworkX graph representation of
        intersecting Regions.
      regions:
        The RegionSet to construct the Region
        intersection graph from.
  """
  def __init__(self, regionset: RegionSet):
    
    self.iterator = None
    self.regionset = regionset

    self.graph = RIGraph(dimension=regionset.dimension)
    for r in regionset:
      self.graph.put_region(r)


  def prepare(self):
    """Prepare dataset for SLIG by sorting region ends in each dimension"""

    self.iterator = []

    for d in range(self.regionset.dimension):
      
      self.iterator.append([])
      for region in self.regionset:
        self.iterator[d].append((region.factors[d].lower, LOWER, region.id))
        self.iterator[d].append((region.factors[d].upper, UPPER, region.id))

      self.iterator[d].sort(key=lambda x: (x[0], x[1]))


  def sweep(self):
    """Execute the sweep line and construct the intersection graph"""

    if self.iterator is None:
      self.prepare()

    actives = []
    intersections = {}

    for dimension in self.iterator:
      for point in dimension:
        if point[1] == UPPER:
          actives.remove(point[2])
        else:
          for active in actives:
            pair = (active, point[2])
            if pair not in intersections:
              intersections[pair] = 1
            else:
              intersections[pair] += 1
          actives.append(point[2])

    for pair, value in intersections.items():
      if value == self.regionset.dimension:
        self.graph.put_intersection(pair[0],pair[1])

    return self.graph


  def stream_enumerate(self):
    """Iteratively enumerate all multiple intersections in the graph."""

    for clique in nx.enumerate_all_cliques(self.graph.G):
      if len(clique) > 1:
        intersect = [self.graph.get_region(r) for r in clique]
        region    = Region.from_intersection(intersect)

        assert isinstance(region, Region)
        yield region


  def enumerate_all(self, combine=False):
    """Return the full enumeration of multiple intersections in the graph"""

    if combine:
      regionset = self.regionset
    else:
      regionset = RegionSet(dimension=self.regionset.dimension)

    for region in self.stream_enumerate():
      regionset.add(region)   

    return regionset