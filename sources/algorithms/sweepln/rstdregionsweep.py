#!/usr/bin/env python

"""
Restricted One-Pass Sweep-line Algorithm for RegionSet

Implements an one-pass sweep-line algorithm over a set of Regions, within a
restricting Region (all Begin and End events must have context Regions that
intersect with the specified restricting Region) and within a specified subset
of Regions.

Implements RestrictedRegionSweep class that executes the specific details and
actions of the sweep-line algorithm, when encountering: Init, Begin, End or
Done events.

Classes:
- RestrictedRegionSweep
"""

from typing import Dict, List, Union

from sources.abstract import Event
from sources.core import Region, RegionEvent, RegionId, RegionSet

from .regionsweep import RegionSweep, RegionSweepEvtKind


class RestrictedRegionSweep(RegionSweep):
  """
  An one-pass sweep-line algorithm over a set of Regions with restricting
  Region and subset of Regions. Subscribes to and is evaluated by the
  one-pass sweep-line algorithm along a dimension on the set of Regions.

  Extends:
    RegionSweep

  Attributes:
    region: The Region that restricts the Begin and
            End events to Regions that intersect it.
    subset: The subset of Regions to include within
            the Intersect events.
  """
  region: Region
  subset: List[Region]

  def __init__(self, *args, **kwargs):
    """
    Initialize the one-pass sweep-line algorithm over a
    restricted set of Regions.

    Args:
      args, kwargs:
        Arguments for self.initialize().
    """
    self.initialize(*args, **kwargs)

    RegionSweep.__init__(self, self.regions)

  def initialize(self, regions: RegionSet, region: RegionId = None,
                       subset: List[RegionId] = []):
    """
    Initialize the one-pass sweep-line algorithm over a
    restricted set of Regions.

    Args:
      regions:  The set of Regions to evaluate
                sweep-line algorithm over.
      region:   The Region that restricts the Begin and
                End events to Regions that intersect it.
      subset:   The subset of Regions to include within
                the Intersect events.
    """
    assert isinstance(subset, List)
    assert all([isinstance(r, (Region, str)) for r in subset])
    assert region is None or isinstance(region, (Region, str))

    if isinstance(region, str) and region in regions:
      region = regions[region]
    if region is not None:
      assert region in regions and (len(subset) == 0 or region in subset)
      assert region.dimension == regions.dimension

    for i, r in enumerate(subset):
      if isinstance(r, str) and r in regions:
        subset[i] = regions[r]

    assert all([r in regions for r in subset])

    self.regions = regions.subset(subset) if len(subset) > 0 else regions
    self.subset = subset
    self.region = region

  ### Methods: Helpers

  def _should_process(self, event: RegionEvent) -> bool:
    """
    Determine if the Begin or End Region event should be process.
    More concretely, does the context Region intersect with the
    restricting Region (if specified)?

    Args:
      event:  The Region beginning or ending Event.

    Returns:
      True:   If the context Region intersects with the
              restricting Region or no restricting Region.
      False:  Otherwise.
    """
    assert self.is_active
    assert event.kind == RegionSweepEvtKind.Begin or \
           event.kind == RegionSweepEvtKind.End

    region, d = event.context, self.dimension

    return self.region is None or self.region[d].overlaps(region[d])

  ### Methods: Event Handlers

  def on_begin(self, event: RegionEvent):
    """
    Handle Event when sweep-line algorithm encounters
    the beginning of a Region.

    Overrides:
      RegionSweep.on_begin

    Args:
      event:  The Region beginning Event.
    """
    if self._should_process(event):
      RegionSweep.on_begin(self, event)

  def on_end(self, event: RegionEvent):
    """
    Handle Event when sweep-line algorithm encounters
    the ending of a Region.

    Overrides:
      RegionSweep.on_end

    Args:
      event:  The Region ending Event.
    """
    if self._should_process(event):
      RegionSweep.on_end(self, event)
