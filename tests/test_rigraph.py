#!/usr/bin/env python

"""
Unit tests for Regional Intersection Graph -- NetworkX

- test_nxgraph_create
- test_nxgraph_sweepctor
- test_nxgraph_mdsweepctor
- test_nxgraph_sweepctor_graph
- test_nxgraph_sweepctor_random
"""

from io import StringIO
from typing import List, Tuple
from unittest import TestCase
from pprint import pprint

from networkx import networkx as nx
from slig.datastructs.rigraph import RIGraph
from slig.datastructs.region import Region


class TestRIGraph(TestCase):

  test_regions: List[Region]

  def setUp(self):
    self.test_regions = []
    self.test_regions.append(Region([0, 0], [5, 5]))
    self.test_regions.append(Region([2, 2], [5, 10]))
    self.test_regions.append(Region([1, 5], [3, 7]))
    self.test_regions.append(Region([-5, 5], [1, 7]))
    self.test_regions.append(Region([-5, 5], [2, 7]))

  def test_nxgraph_create(self):
    
    graph = RIGraph(dimension=1)

    self.assertTrue(graph.G is not None)
    self.assertTrue(isinstance(graph.G, nx.Graph))


  def test_nxgraph_contains(self):
    
    dimension = self.test_regions[0].dimension
    graph = RIGraph(dimension=dimension)

    for region in self.test_regions[0:3]:
      graph.put_region(region)

    self.assertTrue(self.test_regions[0].id in graph)


  def test_nxgraph_put_region(self):
    
    dimension = self.test_regions[0].dimension
    graph = RIGraph(dimension=dimension)

    for region in self.test_regions:
      graph.put_region(region)

    self.assertEqual(self.test_regions, list(graph.regions))
      

  def test_nxgraph_put_intersect(self):
    
    dimension = self.test_regions[0].dimension
    graph = RIGraph(dimension=dimension)

    graph.put_region(self.test_regions[0])
    graph.put_region(self.test_regions[1])
    graph.put_intersection(self.test_regions[0], self.test_regions[1])

    intersection = self.test_regions[0].get_intersection(self.test_regions[1])
    self.assertEqual(intersection, list(graph.intersections)[0])
      

  def test_nxgraph_to_dict(self):
    
    dimension = self.test_regions[0].dimension
    graph = RIGraph(dimension=dimension)

    graph.put_region(self.test_regions[0])
    graph.put_region(self.test_regions[1])
    graph.put_intersection(self.test_regions[0], self.test_regions[1])
    intersection = self.test_regions[0].get_intersection(self.test_regions[1])

    graphdict = {'id':graph.id,'dimension':dimension,'json_graph':'node_link',
      'graph':{
        'directed': False, 'multigraph': False, 'graph':{},
        'nodes':[{'id':r.id, 'region':r} for r in graph.regions],
        'links':[{'source': self.test_regions[0].id,
                  'target': self.test_regions[1].id,
                  'region': intersection}]
      }}

    self.assertEqual(graphdict, graph.to_dict())


  def test_nxgraph_from_dict(self):

    dimension = self.test_regions[0].dimension
    graph = RIGraph(dimension=dimension)

    graph.put_region(self.test_regions[0])
    graph.put_region(self.test_regions[1])
    graph.put_intersection(self.test_regions[0], self.test_regions[1])

    self.assertEqual(graph.to_dict(),
      RIGraph.from_dict(graph.to_dict()).to_dict())