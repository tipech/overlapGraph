#!/usr/bin/env python

"""
Visualization for Region Intersection Graph

Draws the Region intersection graph, to visualize how Regions the
overlapping or intersecting Regions, and how the Regions form
a network of intersecting Regions.

Methods:
- draw_rigraph
"""

from matplotlib.axes import Axes
from networkx import networkx as nx
from pandas import DataFrame

from sources.core import NxGraph, Region


def draw_rigraph(graph: NxGraph, plot: Axes, **kwargs):
  """
  Draws the Region intersection graph, to visualize how Regions the
  overlapping or intersecting Regions, and how the Regions form
  a network of intersecting Regions.

  Args:
    nxgraph:  The Region intersecting graph to draw.
    plot:     The matplotlib plot to draw on.
    kwargs:   Additional arguments and options.

  Keyword Args:
    forced:
      Boolean flag whether or not to force apart
      the unconnected clusters (nodes and edges)
      within the graph.
    colored:
      Boolean flag for colored output or greyscale.

      If True:
        Color codes the nodes based on the Region's
        stored 'color' data property. And color codes the
        edges based on the 2 node Region's stored 'color'
        data property. If the colors in the node Region's
        differ, the edge is black.
      If False:
        All nodes and edges are colored black.
  """
  G = graph.G
  black = (0,0,0)

  forced  = kwargs.get('forced', False)
  colored = kwargs.get('colored', False)

  def force(G: nx.Graph):
    df = DataFrame(index=G.nodes(), columns=G.nodes())
    for row, data in nx.shortest_path_length(G):
      for col, dist in data.items():
        df.loc[row,col] = dist
    df = df.fillna(df.max().max())
    return df.to_dict()

  def get_pos(G: nx.Graph):
    return nx.kamada_kawai_layout(G, **({'dist': force(G)} if forced else {}))

  def get_edge_color(a: Region, b: Region):
    a_color = a.getdata('color')
    b_color = b.getdata('color')
    return a_color if a_color == b_color else black

  if colored:
    node_color = [region.getdata('color', black) for r, region in graph.regions]
    edge_color = [get_edge_color(*region['intersect']) for u, v, region in graph.overlaps]
  else:
    node_color = [black]*len(G)
    edge_color = [black]*nx.number_of_edges(G)

  plot.set_axis_off()
  nx.draw_networkx(G, ax=plot, **{
    'pos': get_pos(G),
    'with_labels': False,
    'node_color': node_color,
    'node_size': 1,
    'edge_color': edge_color,
    'width': 1
  })
