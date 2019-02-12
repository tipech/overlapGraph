#!/usr/bin/env python

"""
Common Commands for Regions and RIGraph Console Command-line

Implements shared and common commands in the CommonConsole command group for
the RegionsConsole and RIGraphConsole command-line interfaces.

Helper Classes:
- CommonConsoleNS

Group:
- CommonConsole

Commands:
- generate
- convert
- enumerate
- visualize
- visualenum
"""

from enum import IntEnum
from io import FileIO
from time import perf_counter
from typing import Any, Callable, Dict, List, Tuple, Type, Union

from matplotlib import pyplot
from matplotlib.cm import ScalarMappable, get_cmap
from matplotlib.colors import Normalize, to_rgb
from networkx import networkx as nx

from sources.abstract import IOable
from sources.algorithms import Enumerate, MRQEnum, NxGraphSweepCtor, SRQEnum
from sources.core import NxGraph, Region, RegionId, RegionSet
from sources.helpers import Randoms
from sources.visualize import draw_regions, draw_rigraph

from .console import Choice, File, Group, argument, option, pass_context


Context   = Union[RegionSet,NxGraph]
CtxBundle = Tuple[RegionSet,NxGraph]
CtxTypes  = {
  'regions': RegionSet,
  'rigraph': NxGraph
}


class CommonConsoleNS:

  ### Class Methods: Helpers

  @classmethod
  def resolve_ctxtype(cls, kind: str) -> Tuple[str, Type]:
    """
    Resolves the given context type name.
    Returns the first type and the exact name that matches
    the given context type name or None if no match found.

    Args:
      kind: The context type.
    Returns:
      The first matching type and the exact name as a tuple
      or None if no match found.
    """
    kind = kind.lower()
    for t, clz in CtxTypes.items():
      name = t.lower()
      if kind == name or kind in name:
        return (t, clz)
    return None

  @classmethod
  def read(cls, source: FileIO, kind: str) -> Context:
    """
    Deserialize the given input JSON file as the specified object type.

    Args:
      source: The input JSON file.
      kind:   The context object type.
    Returns:
      The parsed object.
    """
    assert source.readable()
    _, clz = cls.resolve_ctxtype(kind)
    return clz.from_source(source)

  @classmethod
  def write(cls, output: FileIO, ctx: Context):
    """
    Serialize the given context object to the given output JSON file.

    Args:
      output: The destination JSON file.
      ctx:    The context object.
    """
    assert output.writable()
    assert isinstance(ctx, (IOable, Dict, List, Tuple))
    IOable.to_output(ctx, output, options={'compact': True})

  @classmethod
  def context(cls, ctx: Context) -> Context:
    """
    Given a context object (a collection of Regions or a Region
    intersection graph), converts it into the other object type.

    Args:
      ctx: The object to be converted.
    Returns:
      The converted object.
    """
    assert isinstance(ctx, (RegionSet, NxGraph))
    if isinstance(ctx, RegionSet):
      return NxGraphSweepCtor.prepare(ctx)()
    else:
      regions = RegionSet(dimension=ctx.dimension, id=ctx.id)
      regions.streamadd([region for n, region, _ in ctx.regions])
      return regions

  @classmethod
  def bundle(cls, ctx: Context) -> CtxBundle:
    """
    Returns a tuple with both the collection of Regions and the Region
    intersection graph for the given collection of Regions or Region
    intersection graph.

    Args:
      ctx: The object to be converted.
    Returns:
      Tuple of the collection of Regions and the Region
      intersection graph.
    """
    assert isinstance(ctx, (RegionSet, NxGraph))
    if isinstance(ctx, RegionSet):
      return (ctx, cls.context(ctx))
    else:
      return (cls.context(ctx), ctx)

  @classmethod
  def unbundle(cls, bundle: CtxBundle, kind: str) -> Context:
    """
    Retrieve the component in the given bundle that matches
    with the given kind of context object.

    Args:
      bundle: The bundle to extract context object from.
      kind:   The context object type. 

    Returns:
      The extracted context object or None
      if no match found.
    """
    kind, clz = cls.resolve_ctxtype(kind)
    for n in bundle:
      if isinstance(n, clz):
        return n
    return None

  @classmethod
  def enumerator(cls, alg: str, ctx: Context, qs: List[RegionId]) -> Callable:
    """
    Returns the evaluator function for evaluating the given query with the
    specified algorithm over the given context object.

    Args:
      alg:  The name of the algorithm.
      ctx:  The collection or RIGraph of Regions.
      qs:   The list of Regions to be queried.
    Returns:
      A function to evaluate the algorithm and
      compute the resulting value.
    """
    assert isinstance(ctx, (RegionSet, NxGraph))
    if len(qs) == 0:
      return Enumerate.get(alg, ctx)
    else:
      clz, qs = (SRQEnum, qs[0]) if len(qs) == 1 else (MRQEnum, qs)
      return clz.get(alg, ctx, qs)

  @classmethod
  def colorize_components(cls, ctx: Union[Context,CtxBundle]):
    """
    Assigns colors to the Regions based on the connected communities
    in the graph for which the Region resides.

    Args:
      ctx:
        Context:
          The collection or RIGraph of Regions to assign
          colors based on the connected communities.
        CtxBundle:
          Tuple of the collection of Regions and RIGraph.
    """
    random         = Randoms.uniform()
    regions, graph = ctx if isinstance(ctx, Tuple) else cls.bundle(ctx)
    components     = nx.connected_components(graph.G)

    for component in sorted(components, key=len, reverse=True):
      if len(component) > 1:
        color = tuple(random(3))
        for rid in component:
          regions[rid].initdata('color', color)

  ### Class Methods: Commands

  @classmethod
  def generate(cls, output: FileIO,
                    kind: str,
                    nregions: int,
                    dimension: int, **kwargs):
    """
    Randomly generate a new collection or intersection graph of Regions. \f

    Args:
      output:
        The file to save the newly generated set
        or intersection graph of Regions.

      kind:       The output object type.
      nregions:   The number of Regions to be generated.
      dimension:  The number of dimensions for each Region.
      kwargs:     Additional arguments.

    Keyword Args:
      id:
        The unique identifier for the output.
      bounds:
        The minimum + maximum bounding value for
        each dimension that all Region must be
        enclosed within.
      sizepc:
        The minimum + maximum size of each Region
        as a percent of the bounding Region that
        all Region must be enclosed within.
      precision:
        The number of digits after the decimal pt
        in each Region's lower + upper values.
      colored:
        Boolean flag for whether to color code the
        connected Regions and save the associated
        colors in each Region's data properties.
    """
    kwargs['bounds'] = Region.from_object((dimension, kwargs['bounds']))
    kwargs['sizepc'] = Region.from_object((dimension, kwargs['sizepc']))

    colored = kwargs.pop('colored', False)
    regions = RegionSet.from_random(nregions, **kwargs)
    bundle  = cls.bundle(regions)

    if colored:
      cls.colorize_components(bundle)

    cls.write(output, cls.unbundle(bundle, kind))

  @classmethod
  def convert(cls, source: FileIO,
                   output: FileIO,
                   srckind: str,
                   outkind: str, **kwargs):
    """
    Convert the given source data file with the specified data type to
    specified output data file in the specified data type. Writes the output
    data structure to the given destination file.

    If collection of Regions, evaluates the sweep-line Region intersection
    graph construction algorithm. If Region intersection graph, extracts the
    Regions associated with the nodes within the graph. If input and output
    types are the same, simply deserialize and re-serialize. \f

    Args:
      source:   The input source file to load.
      output:   The destination file to save generated data.
      srckind:  The input data type to convert from.
      outkind:  The output data type to convert to.
      kwargs:   Additional arguments.

    Keyword Args:
      colored:
        Boolean flag for whether to color code the
        connected Regions and save the associated
        colors in each Region's data properties.
    """
    colored = kwargs.pop('colored', False)
    context = cls.read(source, srckind)
    bundle  = cls.bundle(context)    

    if colored:
      cls.colorize_components(bundle)

    cls.write(output, cls.unbundle(bundle, outkind))

  ### Class Methods: Query Evaluation Commands

  @classmethod
  def enumerate(cls, source: FileIO,
                     output: FileIO,
                     srckind: str,
                     queries: List[str] = [], **kwargs):
    """
    Enumerate over the set or graph of Regions in the given input source file.
    Outputs the results to as a JSON with performance data and the results
    as a RegionSet of intersecting Regions.

    If no Regions given in the query, enumerate all intersecting Regions.
    If a single Region is given in the query, enumerate all intersecting
    Regions that includes that Region. If multiple Regions given in the query,
    enumerate all intersecting Regions amongst the subset of Regions. \f

    Args:
      source:   The input source file to load.
      output:   The destination file to save results.
      srckind:  The input data type.
      queries:  The Regions to be queried.
      kwargs:   Additional arguments.

    Keyword Args:
      naive:
        Boolean flag for whether to use the naive
        sweep-line algorithm instead of querying
        via the region intersection graph.
    """
    queries    = list(queries)
    context    = cls.read(source, srckind)
    intersects = RegionSet(dimension=context.dimension)
    counts     = {}

    def get_header(ctx: Context) -> Dict:
      header = {'id': ctx.id, 'type': type(ctx).__name__, 'dimension': ctx.dimension, 'length': len(ctx)}
      if elapse_ctor is None:
        header['elapse_query'] = elapse_query
      else:
        header['elapse_query'] = elapse_query - elapse_ctor
        header['elapse_ctor']  = elapse_ctor
      return header

    def get_enumerator():
      if isinstance(context, NxGraph):
        return (None, cls.enumerator('slig', context, queries))
      if kwargs.get('naive', False):
        return (0, cls.enumerator('naive', context, queries))

      graph   = NxGraphSweepCtor.prepare(context)()
      elapsed = perf_counter() - start
      return (elapsed, cls.enumerator('slig', graph, queries))

    start = perf_counter()
    elapse_ctor, enumerator = get_enumerator()

    for region, intersect in enumerator():
      k = len(intersect)
      if k not in counts:
        counts[k] = 0
      counts[k] += 1
      intersects.add(region)

    elapse_query = perf_counter() - start
    header = get_header(context)
    cls.write(output, {
      'header': {**header, 'query': queries, 'count': counts},
      'results': intersects
    })

  ### Class Methods: Visualization Commands

  @classmethod
  def visualize(cls, source: FileIO,
                     output: FileIO,
                     srckind: str,
                     outkind: str, **kwargs):
    """
    Generate and output a visualization of the collection of Regions or
    Region intersection graph, based on the specified visual to output.
    Saves the visualization to the given destination image file. \f

    Args:
      source:   The input source file to load.
      output:   The dest image file to save visualization.
      srckind:  The input data type.
      outkind:  The output visualization type.
      kwargs:   Additional arguments.

    Keyword Args:
      colored:
        Boolean flag for whether or not to color
        code the connected Regions.
      forced:
        Boolean flag whether or not to force apart
        the unconnected clusters (nodes and edges)
        within the graph.
      communities:
        Boolean flag for whether or not to show the
        connected communities (or Regions with same color).
        Requires colored to be True.
      tightbounds:
        Boolean flag for whether or not to reduce the
        bounding size to the minimum bounding Region,
        instead of the defined bounds.
    """
    figure, ax = pyplot.subplots(subplot_kw={'aspect': 'equal'}, figsize=(20, 10))
    colored = kwargs.get('colored')
    bundle  = cls.bundle(cls.read(source, srckind))

    if colored:
      cls.colorize_components(bundle)

    ctx = cls.unbundle(bundle, outkind)
    draw_plot = draw_regions if isinstance(ctx, RegionSet) else draw_rigraph

    draw_plot(ctx, ax, **kwargs)

    figure.savefig(output, bbox_inches='tight')
    pyplot.close(figure)

  @classmethod
  def visualenum(cls, source: FileIO,
                      output: FileIO,
                      srckind: str,
                      outkind: str,
                      queries: List[str] = [], **kwargs):
    """
    Enumerate over the set or graph of Regions in the given input source file.
    Generate and output a visualization of the collection of Regions or
    Region intersection graph, based on the specified visual to output, and
    color codes the results based on the number of intersecting Regions
    involved in each enumerated intersection. Saves the visualization to the
    given destination image file.

    If no Regions given in the query, enumerate all intersecting Regions.
    If a single Region is given in the query, enumerate all intersecting
    Regions that includes that Region. If multiple Regions given in the query,
    enumerate all intersecting Regions amongst the subset of Regions. \f

    Args:
      source:   The input source file to load.
      output:   The dest image file to save visualization.
      srckind:  The input data type.
      outkind:  The output visualization type.
      queries:  The Regions to be queried.
      kwargs:   Additional arguments.

    Keyword Args:
      colormap:
        The name of a built-in matplotlib colormap to
        color code the enumerated intersecting Regions
        by, based on the number of intersecting Regions
        involved in each enumerated intersection.
      forced:
        Boolean flag whether or not to force apart
        the unconnected clusters (nodes and edges)
        within the graph.
      tightbounds:
        Boolean flag for whether or not to reduce the
        bounding size to the minimum bounding Region,
        instead of the defined bounds.
    """
    figure, ax = pyplot.subplots(subplot_kw={'aspect': 'equal'}, figsize=(20, 10))
    regions, rigraph = cls.bundle(cls.read(source, srckind))
    intersects = RegionSet(dimension=regions.dimension)
    enumerator = cls.enumerator('slig', rigraph, list(queries))
    vmin, vmax = 1, 2

    for region, intersect in enumerator():
      k = len(intersect)
      if vmax < k:
        vmax = k
      intersects.add(region)

    cmap      = get_cmap(kwargs.pop('colormap'))
    cnorm     = Normalize(vmin=vmin, vmax=vmax)
    colors    = ScalarMappable(norm=cnorm, cmap=cmap)
    ctx       = cls.unbundle((regions, rigraph), outkind)
    get_color = lambda i: tuple(colors.to_rgba(i)[0:3])
    draw_plot = draw_regions if isinstance(ctx, RegionSet) else draw_rigraph

    for r in regions:
      r['color'] = tuple([0.5]*3)
    for r in [regions[q] for q in queries]:
      r['color'] = get_color(vmin)
    for r in intersects:
      intersect = r['intersect']
      r['color'] = color = get_color(len(intersect))
      if isinstance(ctx, NxGraph):
        for i, a in enumerate(intersect):
          a['color'] = color
          for b in intersect[i+1:]:
            rigraph.region((a, b))['color'] = color

    if isinstance(ctx, RegionSet):
      ctx = ctx.merge([intersects])

    draw_plot(ctx, ax, colored=True, **kwargs)

    figure.savefig(output, bbox_inches='tight')
    pyplot.close(figure)


### Commands

CommonConsole = Group()

@CommonConsole.command('generate', help=CommonConsoleNS.generate.__doc__)
@argument('output',    type=File('w'))
@argument('kind',      type=Choice(CtxTypes.keys(), case_sensitive=False))
@argument('nregions',  type=int, default=1000)
@argument('dimension', type=int, default=2)
@option('--id',        type=str, default='')
@option('--bounds',    type=(float, float), default=(0, 1000), show_default=True)
@option('--sizepc',    type=(float, float), default=(0, 0.05), show_default=True)
@option('--precision', type=int, default=5, show_default=True)
@option('--colored',   is_flag=True)
@pass_context
def cc_generate(ctx, **kwargs):
  CommonConsoleNS.generate(**kwargs)

@CommonConsole.command('convert', help=CommonConsoleNS.convert.__doc__)
@argument('source',  type=File('r'))
@argument('output',  type=File('w'))
@argument('srckind', type=Choice(CtxTypes.keys(), case_sensitive=False))
@argument('outkind', type=Choice(CtxTypes.keys(), case_sensitive=False))
@option('--colored', is_flag=True)
@pass_context
def cc_convert(ctx, **kwargs):
  CommonConsoleNS.convert(**kwargs)

@CommonConsole.command('enumerate', help=CommonConsoleNS.enumerate.__doc__)
@argument('source',  type=File('r'))
@argument('output',  type=File('w'))
@argument('srckind', type=Choice(CtxTypes.keys(), case_sensitive=False))
@argument('queries', type=str, nargs=-1)
@option('--naive',   is_flag=True)
@pass_context
def cc_enumerate(ctx, **kwargs):
  CommonConsoleNS.enumerate(**kwargs)

@CommonConsole.command('visualize', help=CommonConsoleNS.visualize.__doc__)
@argument('source',  type=File('r'))
@argument('output',  type=File('wb'))
@argument('srckind', type=Choice(CtxTypes.keys(), case_sensitive=False))
@argument('outkind', type=Choice(CtxTypes.keys(), case_sensitive=False))
@option('--colored',     is_flag=True)
@option('--communities', is_flag=True)
@option('--tightbounds', is_flag=True)
@option('--forced',      is_flag=True)
@pass_context
def cc_visualize(ctx, **kwargs):
  CommonConsoleNS.visualize(**kwargs)

@CommonConsole.command('visualenum', help=CommonConsoleNS.visualenum.__doc__)
@argument('source',   type=File('r'))
@argument('output',   type=File('wb'))
@argument('srckind',  type=Choice(CtxTypes.keys(), case_sensitive=False))
@argument('outkind',  type=Choice(CtxTypes.keys(), case_sensitive=False))
@argument('queries',  type=str, nargs=-1)
@option('--colormap', type=str, default='jet')
@option('--forced',      is_flag=True)
@option('--tightbounds', is_flag=True)
@pass_context
def cc_visualenum(ctx, **kwargs):
  CommonConsoleNS.visualenum(**kwargs)
