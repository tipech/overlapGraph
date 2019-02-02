#!/usr/bin/env python

"""
Restricted Cyclic Multi-Pass Sweep-line Algorithm for RegionSet

Implements an cyclic multi-pass sweep-line algorithm over a set of Regions, 
within a restricting Region (all Begin and End events must have context Regions
that intersect with the specified restricting Region) and within a specified
subset of Regions.

Implements RestrictedRegionCycleSweep class that executes the specific details
and actions of the sweep-line algorithm, when encountering: Init, Begin, End or
Done events.

Classes:
- RestrictedRegionCycleSweep
"""

from typing import List

from sources.algorithms.sweepln.regioncyclesweep import RegionCycleSweep
from sources.algorithms.sweepln.rstdregionsweep import RestrictedRegionSweep
from sources.datastructs.datasets.regiontime import RegionEvent


class RestrictedRegionCycleSweep(RestrictedRegionSweep, RegionCycleSweep):
  """
  A cyclic multi-pass sweep-line algorithm over a set of Regions with
  restricting Region and subset of Regions. Subscribes to and is evaluated by
  the cyclic multi-pass sweep-line algorithm along a dimension on the set of
  Regions.

  Extends:
    RestrictedRegionSweep
    RegionCycleSweep
  """

  def __init__(self, *args, **kwargs):
    """
    Initialize the cyclic multi-pass sweep-line algorithm over a
    restricted set of Regions.

    Args:
      args, kwargs:
        Arguments for RestrictedRegionSweep.initialize().
    """
    RestrictedRegionSweep.initialize(self, *args, **kwargs)
    RegionCycleSweep.__init__(self, self.regions)

  ### Methods: Event Handlers

  def on_begin(self, event: RegionEvent):
    """
    Handle Event when cyclic multi-pass sweep-line algorithm
    encounters the beginning of a Region.

    Overrides:
      RestrictedRegionSweep.on_begin
      RegionSweep.on_begin

    Args:
      event:  The Region beginning Event.
    """
    if self._should_process(event):
      RegionCycleSweep.on_begin(self, event)

  def on_end(self, event: RegionEvent):
    """
    Handle Event when cyclic multi-pass sweep-line algorithm
    encounters the ending of a Region.

    Overrides:
      RestrictedRegionSweep.on_end
      RegionSweep.on_end

    Args:
      event:  The Region ending Event.
    """
    if self._should_process(event):
      RegionCycleSweep.on_end(self, event)
