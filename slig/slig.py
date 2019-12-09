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
from collections import deque
from itertools import chain, combinations, islice, combinations
from pprint import pprint
from networkx import networkx as nx
from .datastructs import Region, RegionSet, RIGraph
from typing import Any, Callable, Dict, List, Tuple, Union

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


  def prepare_sweep(self):
    """Prepare dataset for SLIG by sorting region ends in each dimension"""

    self.iterator = []

    for d in range(self.regionset.dimension):
      
      self.iterator.append([])
      for region in self.regionset:
        self.iterator[d].append((region.factors[d].lower, LOWER, region.id))
        self.iterator[d].append((region.factors[d].upper, UPPER, region.id))

      self.iterator[d].sort(key=lambda x: (x[0], x[1]))


  def prepare_scan(self):
    """Prepare dataset for SLIG by sorting region starts in each dimension"""

    self.iterator = []

    for d in range(self.regionset.dimension):
      
      self.iterator.append([])
      for region in self.regionset:
        self.iterator[d].append((region.factors[d].lower, region.id))

      self.iterator[d].sort(key=lambda x: x[0])


  def sweep(self):
    """Execute the sweep line and construct the intersection graph"""

    if self.iterator is None:
      self.prepare_sweep()

    actives = []
    intersections = {}

    for dimension in self.iterator:
      for point in dimension:
        if point[1] == UPPER:
          actives.remove(point[2])
        else:
          for active in actives:
            pair = tuple(sorted([active, point[2]]))

            if pair not in intersections:
              intersections[pair] = 1
            else:
              intersections[pair] += 1
          actives.append(point[2])

    for pair, value in intersections.items():
      if value == self.regionset.dimension:
        self.graph.put_intersection(pair[0],pair[1])

    return self.graph


  def scan_line(self):
    """Execute the scan line and construct the intersection graph"""

    if self.iterator is None:
      self.prepare_scan()

    intersections = {}
    for d, regions in enumerate(self.iterator):
      for i, (point,region) in enumerate(regions):
        for j in range(i+1,len(regions)):
          other_point, other_region = regions[j]
          if other_point > self.regionset[region][d].upper:
            break

          pair = tuple(sorted([region, other_region]))
          if pair not in intersections:
            intersections[pair] = 1
          else:
            intersections[pair] += 1
    

    for i, (pair, value) in enumerate(intersections.items()):
      if value == self.regionset.dimension:
        self.graph.put_intersection(pair[0],pair[1])

    return self.graph


  def enumerate_all(self):
    """Return the full enumeration of multiple intersections in the graph"""

    regionset = RegionSet(dimension=self.regionset.dimension)

    for clique in nx.enumerate_all_cliques(self.graph.G):

      if len(clique) > 1:
        intersect = [self.graph.get_region(r) for r in clique]
        region    = Region.from_intersection(intersect)

        assert isinstance(region, Region)
        regionset.add(region)   

    return regionset



  def enumerate_visible(self):
    """Return the highest-k visible multiple intersections, in-memory."""

    regionset = RegionSet(dimension=self.regionset.dimension)

    G = self.graph.G

    index = {}
    nbrs = {}
    for u in G:
      index[u] = len(index)
      # Neighbors of u that appear after u in the iteration order of G.
      nbrs[u] = {v for v in G[u] if v not in index}

    queue = deque(([u], self.graph.get_region(u),
      sorted(nbrs[u], key=index.__getitem__)) for u in G)

    # Loop invariants:
    # 1. len(base) is nondecreasing.
    # 2. (base + cnbrs) is sorted with respect to the iteration order of G.
    # 3. cnbrs is a set of common neighbors of nodes in base.
    while queue:
      base, base_region, cnbrs = queue.popleft()
      cnbrs = list(cnbrs)
      visible = True

      for i, u in enumerate(cnbrs):

        # construct larger qlique and corresponding region
        super_clique = base + [u]
        if len(super_clique) > 1:
          intersect = [self.graph.get_region(r) for r in super_clique]
          super_region = Region.from_intersection(intersect)

          # if larger clique's region covers base, mark base not visible
          if super_region.size == base_region.size:
            visible = False
        else:
          super_region = self.graph.get_region(super_clique[0])

        queue.append((super_clique, super_region,
          filter(nbrs[u].__contains__, islice(cnbrs, i + 1, None))))

      if visible and len(base) > 1:
        regionset.add(base_region)

    return regionset
