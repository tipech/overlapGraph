#!/usr/bin/env python

"""
Region Intersection Graph Console Command-line
Implements the console command-line for the 'rigraph' command.

Methods:
- main

Commands:
- visualize
- regions
- vregions
- rqenum
- vrqenum
"""

import typing as t

from io import FileIO
from numbers import Real
from sys import stdout
from time import perf_counter

from matplotlib import pyplot
from matplotlib.cm import ScalarMappable, get_cmap
from matplotlib.colors import Normalize, to_rgb
from networkx import networkx as nx

from sources.abstract import IOable
from sources.algorithms import Enumerate, MRQEnum, NxGraphSweepCtor, SRQEnum
from sources.core import NxGraph, Region, RegionSet
from sources.helpers import Randoms
from sources.visualize import draw_regions, draw_rigraph

from .console import Choice, File, argument, group, option


def colorize(regions: RegionSet, graph: NxGraph = None):
  assert isinstance(regions, RegionSet) or isinstance(graph, NxGraph)

  if graph is None:
    graph = NxGraphSweepCtor.prepare(regions)()

  if regions is None:
    regions = RegionSet(dimension=graph.dimension, id=graph.id)
    regions.streamadd([region for n, region, _ in graph.regions])

  random     = Randoms.uniform()
  components = nx.connected_components(graph.G)

  for component in sorted(components, key=len, reverse=True):
    if len(component) > 1:
      color = tuple(random(3))
      for rid in component:
        regions[rid].initdata('color', color)


@group(help='RIGraph commands.')
def main():
  pass


@main.command('visualize')
@argument('source', type=File('r'))
@argument('output', type=File('wb'))
@option('--forced', is_flag=True)
@option('--colored', is_flag=True)
def visualize(source: FileIO, output: FileIO, forced: bool, colored: bool):
  """
  Generate and output a visualization of the Region intersection graph
  Deserializes the given source file of a Region intersection graph, and
  then generates the visualization of the graph with NetworkX.
  Saves the visualization to the given destination image file. \f

  Args:
    source:
      The input source file to load the
      Region intersection graph from.
    output:
      The destination image file to save the
      generated intersection graph visualization.
    forced:
      Boolean flag whether or not to force apart
      the unconnected clusters (nodes and edges)
      within the graph.
    colored:
      Boolean flag for whether or not to color
      code the connected Regions.
  """
  assert source.readable()
  assert output.writable()

  graph = NxGraph.from_source(source)

  if colored:
    colorize(None, graph)

  figure, ax = pyplot.subplots(subplot_kw={'aspect': 'equal'}, figsize=(20, 10))
  draw_rigraph(graph, ax, colored=colored, forced=forced)
  figure.savefig(output, bbox_inches='tight')
  pyplot.close(figure)


@main.command('regions')
@argument('source', type=File('r'))
@argument('output', type=File('w'))
@option('--colored', is_flag=True)
def toregions(source: FileIO, output: FileIO, colored: bool):
  """
  Converts the given source file of a Region intersection graph
  to its representation as a collections of Regions. Serializes and writes the
  output data structure to the given destination file. \f

  Args:
    source:
      The input source file to load the
      Region intersection graph from.
    output:
      The destination file to save the
      generated collection of Regions.
    colored:
      Boolean flag for whether or not to color code
      the connected Regions and save the associated
      colors in each Region's data properties.
  """
  assert source.readable()
  assert output.writable()

  graph   = NxGraph.from_source(source)
  regions = RegionSet(dimension=graph.dimension, id=graph.id)
  regions.streamadd([region for n, region, _ in graph.regions])

  if colored:
    colorize(regions, graph)

  RegionSet.to_output(regions, output, options={'compact': True})


@main.command('vregions')
@argument('source', type=File('r'))
@argument('output', type=File('wb'))
@option('--colored', is_flag=True)
def vregions(source: FileIO, output: FileIO, colored: bool):
  """
  Visualizes the given source file of a Region intersection graph as a
  collections of intersecting Regions. Saves the visualization to the given
  destination image file. \f

  Args:
    source:
      The input source file to load the
      Region intersection graph from.
    output:
      The destination image file for the
      generated visualization to be saved.
    colored:
      Boolean flag for whether or not to color
      code the connected Regions.
  """
  assert source.readable()
  assert output.writable()

  graph   = NxGraph.from_source(source)
  regions = RegionSet(dimension=graph.dimension, id=graph.id)
  regions.streamadd([region for n, region, _ in graph.regions])

  if colored:
    colorize(regions, graph)

  figure, ax = pyplot.subplots(subplot_kw={'aspect': 'equal'}, figsize=(20, 10))
  draw_regions(regions, ax, colored=colored)
  figure.savefig(output, bbox_inches='tight')
  pyplot.close(figure)


@main.command('rqenum')
@argument('source', type=File('r'))
@argument('output', type=File('w'))
@argument('queries', type=str, nargs=-1)
def rqenum(source: FileIO, output: FileIO, queries = []):
  """
  Enumerate over the Region intersection graph in the given input source file.
  Outputs the results to as a JSON with performance data and the results
  as a RegionSet of intersecting Regions.

  If no Regions given in the query, enumerate all intersecting Regions.
  If a single Region is given in the query, enumerate all intersecting Regions
  that includes that Region. If multiple Regions given in the query, enumerate
  all intersecting Regions amongst the subset of Regions.
  \f

  Args:
    source:
      The input source file to load the
      Region intersection graph from.
    output:
      The output file to save the resulting collection
      of intersecting Regions and collected the
      statistics during the evaluation.
    queries:
      The Regions to be queried.
  """
  assert source.readable()
  assert output.writable()

  alg        = 'slig'
  graph      = NxGraph.from_source(source)
  intersects = RegionSet(dimension=graph.dimension)
  counts     = {}

  def get_enumerator():
    if len(queries) == 0:
      return Enumerate.get(alg, graph)
    elif len(queries) == 1:
      return SRQEnum.get(alg, graph, queries[0])
    else:
      return MRQEnum.get(alg, graph, list(queries))

  start = perf_counter()
  enumerator = get_enumerator()

  for region, intersect in enumerator():
    k = len(intersect)
    if k not in counts:
      counts[k] = 0
    counts[k] += 1
    intersects.add(region)

  elapse_query = perf_counter() - start
  data = {
    'header': {
      'rigraph':      graph.id,
      'dimension':    graph.dimension,
      'length':       len(graph),
      'query':        queries,
      'elapse_query': elapse_query,
      'count':        counts
    },
    'results': intersects
  }

  IOable.to_output(data, output, options={'compact': True})


@main.command('vrqenum')
@argument('source', type=File('r'))
@argument('output', type=File('wb'))
@argument('queries', type=str, nargs=-1)
@option('--regions', is_flag=True)
@option('--forced', is_flag=True)
@option('--colormap', type=str, default='jet')
def vrqenum(source: FileIO, output: FileIO,
            regions: bool, forced: bool, colormap: str,
            queries = []):
  """
  Enumerate over the Region intersection graph in the given input source file.
  Outputs the results an visualization of intersecting Regions color
  coded by the number of Regions involved in each intersection.

  If no Regions given in the query, enumerate all intersecting Regions.
  If a single Region is given in the query, enumerate all intersecting Regions
  that includes that Region. If multiple Regions given in the query, enumerate
  all intersecting Regions amongst the subset of Regions.
  \f

  Args:
    source:
      The input source file to load the
      Region intersection graph from.
    output:
      The output file to save the resulting
      visualization of intersecting Regions.
    regions:
      Boolean flag for whether or not to output a
      visualization for the region intersection graph
      or the intersecting Regions.
    forced:
      Boolean flag whether or not to force apart
      the unconnected clusters (nodes and edges)
      within the graph. Only applicable when --graph.
    colormap:
      The name of a built-in matplotlib colormap.
    queries:
      The Regions to be queried.
  """
  assert source.readable()
  assert output.writable()

  alg        = 'slig'
  graph      = NxGraph.from_source(source)
  regionset  = RegionSet(dimension=graph.dimension, id=graph.id)
  intersects = RegionSet(dimension=graph.dimension)
  count      = 2

  regionset.streamadd([region for n, region, _ in graph.regions])

  def get_enumerator():
    if len(queries) == 0:
      return Enumerate.get(alg, graph)
    elif len(queries) == 1:
      return SRQEnum.get(alg, graph, queries[0])
    else:
      return MRQEnum.get(alg, graph, list(queries))

  enumerator = get_enumerator()

  for region, intersect in enumerator():
    k = len(intersect)
    if count < k:
      count = k
    intersects.add(region)

  cnorm  = Normalize(vmin=1, vmax=count)
  colors = ScalarMappable(norm=cnorm, cmap=get_cmap(colormap))

  for region in regionset:
    region['color'] = tuple([0.5]*3)
  for rid in queries:
    region = regionset[rid]
    color = tuple(colors.to_rgba(1)[0:3])
    region['color'] = color
  for region in intersects:
    color = tuple(colors.to_rgba(len(region['intersect']))[0:3])
    region['color'] = color
    if not regions:
      for i, a in enumerate(region['intersect']):
        a['color'] = color
        for b in region['intersect'][i+1:]:
          intersect = graph.region((a, b))
          intersect['color'] = color

  figure, ax = pyplot.subplots(subplot_kw={'aspect': 'equal'}, figsize=(20, 10))

  if regions:
    draw_regions(regionset.merge([intersects]), ax, colored=True)
  else:
    draw_rigraph(graph, ax, colored=True, forced=forced)

  figure.savefig(output, bbox_inches='tight')
  pyplot.close(figure)
