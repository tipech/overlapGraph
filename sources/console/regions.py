#!/usr/bin/env python

"""
Regions Console Command-line
Implements the console command-line for the 'regions' command.

Methods:
- main

Commands:
- generate
- visualize
- vgraph
- graph
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
  if graph is None:
    graph = NxGraphSweepCtor.prepare(regions)()

  random = Randoms.uniform()
  components = nx.connected_components(graph.G)
  for component in sorted(components, key=len, reverse=True):
    if len(component) > 1:
      color = tuple(random(3))
      for rid in component:
        regions[rid].initdata('color', color)


@group(help='Regions commands.')
def main():
  pass


@main.command('generate')
@argument('output', type=File('w'))
@argument('nregions', type=int, default=1000)
@argument('dimension', type=int, default=2)
@option('--id', type=str, default='')
@option('--bounds', type=(float, float), default=(0, 1000), show_default=True)
@option('--sizepc', type=(float, float), default=(0, 0.05), show_default=True)
@option('--precision', type=int, default=5, show_default=True)
@option('--colored', is_flag=True)
def generate(id: str, nregions: int, dimension: int,
             bounds: t.Tuple[float, float], sizepc: t.Tuple[float, float],
             precision: int, colored: bool,
             output: FileIO = stdout):
  """
  Randomly generate a new collection of Regions. \f

  Args:
    id:         The unique identifier for the RegionSet.
    nregions:   The number of Regions to be generated.
    dimension:  The number of dimensions for each Region.
    output:
      The output file to save the newly generated
      collection of Regions.
    bounds:
      The minimum and maximum bounding value for each
      dimension that all Region must be enclosed within.
    sizepc:
      The minimum and maximum size of each Region as a
      percent of the bounding Region that all Region
      must be enclosed within.
    precision:
      The number of digits after the decimal point
      in each Region's lower and upper values.
    colored:
      Boolean flag for whether or not to color code
      the connected Regions and save the associated
      colors in each Region's data properties.
  """
  assert output.writable()

  regions = RegionSet.from_random(nregions, **{'id': id,
    'bounds': Region.from_object((dimension, bounds)),
    'sizepc': Region.from_object((dimension, sizepc)),
    'precision': precision
  })

  if colored:
    colorize(regions)

  RegionSet.to_output(regions, output, options={'compact': True})


@main.command('visualize')
@argument('source', type=File('r'))
@argument('output', type=File('wb'))
@option('--colored', is_flag=True)
def visualize(source: FileIO, output: FileIO, colored: bool):
  """
  Generate and output a visualization for intersecting Regions for
  the given input source file to load the collection of Regions from.
  Saves the visualization to the given destination image file. \f

  Args:
    source:
      The input source file to load the
      collection of Regions from.
    output:
      The destination image file for the
      generated visualization to be saved.
    colored:
      Boolean flag for whether or not to color
      code the connected Regions.
  """
  assert source.readable()
  assert output.writable()

  regions = RegionSet.from_source(source)
  figure, ax = pyplot.subplots(subplot_kw={'aspect': 'equal'}, figsize=(20, 10))

  if colored:
    colorize(regions)

  draw_regions(regions, ax, colored=colored)

  figure.savefig(output, bbox_inches='tight')
  pyplot.close(figure)

@main.command('graph')
@argument('source', type=File('r'))
@argument('output', type=File('w'))
@option('--colored', is_flag=True)
def tograph(source: FileIO, output: FileIO, colored: bool):
  """
  Converts the given source file of Regions to its graph representation.
  Evaluates the sweep-line Region intersection graph construction
  algorithm, and then serializes and writes the output data structure
  to the given destination file. \f

  Args:
    source:
      The input source file to load the
      collection of Regions from.
    output:
      The destination file to save the
      generated intersection graph data.
    colored:
      Boolean flag for whether or not to color code
      the connected Regions and save the associated
      colors in each Region's data properties.
  """
  assert source.readable()
  assert output.writable()

  regions = RegionSet.from_source(source)
  graph   = NxGraphSweepCtor.prepare(regions)()

  if colored:
    colorize(regions, graph)

  NxGraph.to_output(graph, output, options={'compact': True})


@main.command('vgraph')
@argument('source', type=File('r'))
@argument('output', type=File('wb'))
@option('--forced', is_flag=True)
@option('--colored', is_flag=True)
def vgraph(source: FileIO, output: FileIO, forced: bool, colored: bool):
  """
  Generate and output a visualization of the Region intersection graph
  Converts the given source file of Regions to its graph representation.
  Evaluates the sweep-line Region intersection graph construction
  algorithm, and then generates the visualization of the graph with NetworkX.
  Saves the visualization to the given destination image file. \f

  Args:
    source:
      The input source file to load the
      collection of Regions from.
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

  regions = RegionSet.from_source(source, 'json')
  graph = NxGraphSweepCtor.prepare(regions)()

  if colored:
    colorize(regions, graph)

  figure, ax = pyplot.subplots(subplot_kw={'aspect': 'equal'}, figsize=(20, 10))
  draw_rigraph(graph, ax, colored=colored, forced=forced)
  figure.savefig(output, bbox_inches='tight')
  pyplot.close(figure)


@main.command('rqenum')
@argument('source', type=File('r'))
@argument('output', type=File('w'))
@argument('queries', type=str, nargs=-1)
@option('--naive', is_flag=True)
def rqenum(source: FileIO, output: FileIO, naive: bool, queries = []):
  """
  Enumerate over the Regions in the given input source file.
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
      collection of Regions from.
    output:
      The output file to save the resulting collection
      of intersecting Regions and collected the
      statistics during the evaluation.
    naive:
      Boolean flag for whether or not to use the naive
      sweep-line algorithm instead of querying via the
      region intersection graph.
    queries:
      The Regions to be queried.
  """
  assert source.readable()
  assert output.writable()

  regions = RegionSet.from_source(source)
  intersects = RegionSet(dimension=regions.dimension)
  counts = {}

  def get_enumerator():
    if len(queries) == 0:
      return Enumerate.get(alg, context)
    elif len(queries) == 1:
      return SRQEnum.get(alg, context, queries[0])
    else:
      return MRQEnum.get(alg, context, list(queries))

  start = perf_counter()

  if naive:
    alg = 'naive'
    context = regions
    elapse_ctor = 0
  else:
    alg = 'slig'
    context = NxGraphSweepCtor.prepare(regions)()
    elapse_ctor = perf_counter() - start

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
      'regionset':    regions.id,
      'dimension':    regions.dimension,
      'length':       regions.length,
      'query':        queries,
      'elapse_ctor':  elapse_ctor,
      'elapse_query': elapse_query - elapse_ctor,
      'count':        counts
    },
    'results': intersects
  }

  IOable.to_output(data, output, options={'compact': True})


@main.command('vrqenum')
@argument('source', type=File('r'))
@argument('output', type=File('wb'))
@argument('queries', type=str, nargs=-1)
@option('--graph', is_flag=True)
@option('--forced', is_flag=True)
@option('--colormap', type=str, default='jet')
def vrqenum(source: FileIO, output: FileIO,
            graph: bool, forced: bool, colormap: str,
            queries = []):
  """
  Enumerate over the Regions in the given input source file.
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
      collection of Regions from.
    output:
      The output file to save the resulting
      visualization of intersecting Regions.
    graph:
      Boolean flag for whether or not to output a
      visualization for the intersecting Regions or
      the region intersection graph.
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

  regions = RegionSet.from_source(source)
  intersects = RegionSet(dimension=regions.dimension)
  count = 2

  def get_enumerator():
    if len(queries) == 0:
      return Enumerate.get(alg, context)
    elif len(queries) == 1:
      return SRQEnum.get(alg, context, queries[0])
    else:
      return MRQEnum.get(alg, context, list(queries))

  alg = 'slig'
  context = NxGraphSweepCtor.prepare(regions)()
  enumerator = get_enumerator()

  for region, intersect in enumerator():
    k = len(intersect)
    if count < k:
      count = k
    intersects.add(region)

  cnorm  = Normalize(vmin=1, vmax=count)
  colors = ScalarMappable(norm=cnorm, cmap=get_cmap(colormap))

  for region in regions:
    region['color'] = tuple([0.5]*3)
  for rid in queries:
    region = regions[rid]
    color = tuple(colors.to_rgba(1)[0:3])
    region['color'] = color
  for region in intersects:
    color = tuple(colors.to_rgba(len(region['intersect']))[0:3])
    region['color'] = color
    if graph:
      for i, a in enumerate(region['intersect']):
        a['color'] = color
        for b in region['intersect'][i+1:]:
          intersect, _ = context[a, b]
          intersect['color'] = color

  figure, ax = pyplot.subplots(subplot_kw={'aspect': 'equal'}, figsize=(20, 10))

  if graph:
    draw_rigraph(context, ax, colored=True, forced=forced)
  else:
    draw_regions(regions.merge([intersects]), ax, colored=True)

  figure.savefig(output, bbox_inches='tight')
  pyplot.close(figure)
