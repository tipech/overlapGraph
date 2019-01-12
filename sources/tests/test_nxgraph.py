#!/usr/bin/env python

"""
Unit tests for Regional Intersection Graph -- NetworkX

- test_nxgraph_create
- test_nxgraph_sweepctor
- test_nxgraph_sweepctor_graph
"""

from io import StringIO
from typing import List, Tuple
from unittest import TestCase

from sources.algorithms.sweepln.regionsweepdebug import RegionSweepDebug
from sources.algorithms.rigctor.nxgsweepctor import NxGraphSweepCtor
from sources.algorithms.sweepln.regionsweep import RegionSweep
from sources.datastructs.datasets.regionset import RegionSet
from sources.datastructs.rigraphs.nxgraph import NxGraph
from sources.datastructs.shapes.region import Region, RegionPair


class TestNxGraph(TestCase):

  test_regions: List[Region]

  def setUp(self):
    self.test_regions = []
    self.test_regions.append(Region([0, 0], [5, 5]))
    self.test_regions.append(Region([2, 2], [5, 10]))
    self.test_regions.append(Region([1, 5], [3, 7]))
    self.test_regions.append(Region([-5, 5], [1, 7]))
    self.test_regions.append(Region([-5, 5], [2, 7]))

  def _reset_output(self, output: StringIO) -> StringIO:
    output.seek(0)
    return output

  def _nxgraphctor(self, regions: RegionSet) -> NxGraph:
    subscribers = [] #[RegionSweepDebug()]
    return NxGraphSweepCtor.evaluate(regions, *subscribers)()

  def naive_ctor(self, nxgraph: NxGraph):
    for region in self.test_regions:
      nxgraph.put_region(region)

    for region in self.test_regions:
      for that in self.test_regions:
        if region is that:
          continue
        if region.overlaps(that):
          nxgraph.put_overlap((region, that))

  def check_nxgraph(self, a: NxGraph, b: NxGraph):
    self.assertEqual(a.dimension, b.dimension)
    for anode, aregion in a.G.nodes(data='region'):
      self.assertTrue(anode in b.G.node)
      self.assertTrue(isinstance(aregion, Region))
      self.assertTrue(isinstance(b.G.node[anode]['region'], Region))
      self.assertEqual(aregion, b.G.node[anode]['region'])

    for (u, v, aregion) in a.G.edges(data='intersect'):
      self.assertTrue((u, v) in b.G.edges)
      bregion = b.G.edges[u, v]['intersect']
      #print(f'A: {aregion}: {aregion["intersect"]}')
      #print(f'B: {bregion}: {bregion["intersect"]}')
      self.assertTrue(isinstance(aregion, Region))
      self.assertTrue(isinstance(bregion, Region))
      self.assertEqual(aregion, bregion)
      if 'intersect' in aregion:
        self.assertTrue('intersect' in bregion)
        self.assertTrue(all([isinstance(r, Region) for r in aregion['intersect']]))
        self.assertTrue(all([isinstance(r, Region) for r in bregion['intersect']]))
        self.assertTrue(all([r in bregion['intersect'] for r in aregion['intersect']]))

  def test_nxgraph_create(self):
    dimension = self.test_regions[0].dimension
    nxgraph = NxGraph(dimension=dimension)
    self.naive_ctor(nxgraph)

    with StringIO() as output:
      for json_graph in ['node_link', 'adjacency']:
        options = { 'json_graph': json_graph, 'compact': True }
        output.truncate(0)
        nxgraph.to_output(self._reset_output(output), options=options)
        #json_output = output.getvalue()
        #print(f'{json_graph}:')
        #print(f'{json_output}')
        newgraph = NxGraph.from_source(self._reset_output(output))
        self.check_nxgraph(nxgraph, newgraph)

  def test_nxgraph_sweepctor(self):
    dimension = self.test_regions[0].dimension
    regionset = RegionSet(dimension=dimension)
    regionset.streamadd(self.test_regions)
    nxgraph = self._nxgraphctor(regionset)

    with StringIO() as output:
      for json_graph in ['node_link', 'adjacency']:
        options = { 'json_graph': json_graph, 'compact': True }
        output.truncate(0)
        nxgraph.to_output(self._reset_output(output), options=options)
        #json_output = output.getvalue()
        #print(f'{json_graph}:')
        #print(f'{json_output}')
        newgraph = NxGraph.from_source(self._reset_output(output))
        self.check_nxgraph(nxgraph, newgraph)

  def test_nxgraph_sweepctor_graph(self):
    dimension = self.test_regions[0].dimension
    nxgraph = NxGraph(dimension=dimension)
    self.naive_ctor(nxgraph)

    regionset = RegionSet(dimension=dimension)
    regionset.streamadd(self.test_regions)
    nxgraphsweepln = self._nxgraphctor(regionset)

    G = nxgraph.G
    S = nxgraphsweepln.G

    self.assertEqual(nxgraph.dimension, nxgraphsweepln.dimension)
    for node, region in G.nodes(data='region'):
      self.assertTrue(node in S.node)
      self.assertEqual(region, S.node[node]['region'])

    for (u, v, aregion) in G.edges(data='intersect'):
      self.assertTrue((u, v) in S.edges)
      bregion = S.edges[u, v]['intersect']
      self.assertEqual(aregion, bregion)
      self.assertTrue('intersect' in aregion)
      self.assertTrue('intersect' in bregion)
      aintersect = aregion['intersect']
      bintersect = bregion['intersect']
      self.assertTrue(all([r in bintersect for r in aintersect]))
