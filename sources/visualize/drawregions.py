#!/usr/bin/env python

"""
Visualization for Intersecting Regions

Draws the Regions on a 1D or 2D plot, to visualize the
overlapping or intersecting Regions.

Methods:
- draw_regions
- draw_regions1d
- draw_regions2d
"""

from dataclasses import astuple

from matplotlib import pyplot
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

from sources.datastructs.datasets.regionset import RegionSet
from sources.datastructs.shapes.region import Region


def draw_regions(regions: RegionSet, plot: Axes, **kwargs):
  """
  Draws the Regions on a 1D or 2D plot, to visualize the
  overlapping or intersecting Regions.

  Args:
    regions:  The set of Regions to draw.
    plot:     The matplotlib plot to draw on.
    kwargs:   Additional arguments and options.
  
  See:
  - draw_regions1d
  - draw_regions2d
  """
  if regions.dimension == 1:
    draw_regions1d(regions, plot, **kwargs)
  elif regions.dimension == 2:
    draw_regions2d(regions, plot, **kwargs)
  else:
    raise NotImplementedError


def draw_regions1d(regions: RegionSet, plot: Axes, **kwargs):
  """
  Draws the Regions on a 1D plot, to visualize the
  overlapping or intersecting Regions (or intervals).

  Args:
    regions:  The set of 1D Regions to draw.
    plot:     The matplotlib plot to draw on.
    kwargs:   Additional arguments and options.

  Keyword Args:
    colored:
      Boolean flag for colored output or greyscale.
      If True, color codes the Regions based on the
      Region's stored 'color' data property. Otherwise,
      all Regions have black edges with transparent faces.
    communities:
      Boolean flag for whether or not to show the
      connected communities (or Regions with same color).
      Requires colored to be True.
    tightbounds:
      Boolean flag for whether or not to reduce the
      bounding size to the minimum bounding Region,
      instead of the defined bounds.
  """
  assert regions.dimension == 1

  black   = (0,0,0)
  groups  = {}

  colored     = kwargs.get('colored', False)
  communities = kwargs.get('communities', False)
  tightbounds = kwargs.get('tightbounds', False)

  bbox    = regions.bbox if tightbounds else regions.minbounds
  spacing = max(bbox[0].length / len(regions), 10)

  if colored and communities:
    for region in regions:
      color = region.getdata('color')
      if color is not None:
        group = groups.setdefault(tuple(color), RegionSet(dimension=1))
        group.add(region)

    for color, group in groups.items():
      gbbox  = group.bbox[0]
      lows   = (gbbox.lower, 0)
      w, h   = (gbbox.length, spacing*(len(regions) + 2))

      rectangle = Rectangle(lows, w, h, facecolor=(*color,0.05), edgecolor='none')
      rectangle.set_clip_box(plot)
      plot.add_artist(rectangle)

  for i, region in enumerate(regions):
    color = region.getdata('color', black) if colored else black
    plot.plot(list(astuple(region[0])), [spacing*(i + 1)]*2, color=color)

  plot.set_xlim(astuple(bbox[0]))
  plot.yaxis.set_visible(False)


def draw_regions2d(regions: RegionSet, plot: Axes, **kwargs):
  """
  Draws the Regions on a 2D plot, to visualize the
  overlapping or intersecting Regions (or rectangles).

  Args:
    regions:  The set of 2D Regions to draw.
    plot:     The matplotlib plot to draw on.
    kwargs:   Additional arguments and options.

  Keyword Args:
    colored:
      Boolean flag for colored output or greyscale.
      If True, color codes the Regions based on the
      Region's stored 'color' data property. Otherwise,
      all Regions have black edges with transparent faces.
    communities:
      Boolean flag for whether or not to show the
      connected communities (or Regions with same color).
      Requires colored to be True.
    tightbounds:
      Boolean flag for whether or not to reduce the
      bounding size to the minimum bounding Region,
      instead of the defined bounds.
  """
  assert regions.dimension == 2

  black   = (0,0,0)
  groups  = {}

  colored     = kwargs.get('colored', False)
  communities = kwargs.get('communities', False)
  tightbounds = kwargs.get('tightbounds', False)

  bbox = regions.bbox if tightbounds else regions.minbounds

  def mkrectangle(region: Region):
    lower = tuple(region[d].lower  for d in range(2))
    w, h  = tuple(region[d].length for d in range(2))

    return lower, w, h

  if colored and communities:
    for region in regions:
      color = region.getdata('color')
      if color is not None:
        group = groups.setdefault(tuple(color), RegionSet(dimension=2))
        group.add(region)

    for color, group in groups.items():
      rectangle = Rectangle(*mkrectangle(group.bbox), facecolor=(*color,0.05), edgecolor='none')
      rectangle.set_clip_box(plot)
      plot.add_artist(rectangle)

  for region in regions:
    color = region.getdata('color', black) if colored else black
    rectangle = Rectangle(*mkrectangle(region), facecolor=(*color,0.1), edgecolor=color)
    rectangle.set_clip_box(plot)
    plot.add_artist(rectangle)

  plot.set_xlim(astuple(bbox[0]))
  plot.set_ylim(astuple(bbox[1]))
