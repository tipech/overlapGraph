#!/usr/bin/env python

"""
Multi-Pass Sweep-line Algorithm for RegionSet

This script implements an multi-pass sweep-line algorithm over a set of Regions.
Implements RegionMSweep class that executes the specific details and actions
of the multi-pass sweep-line algorithm, when encountering a Begin or End event.

Note:
  Within this script, we make the distinction between
  two similar terms: 'overlap' and 'intersect'.

  overlap:
    The intersection between exactly two Regions.
  intersect:
    The intersection between two or more Regions
    It is more general. An overlap is an intersect,
    but an intersect is not an overlap.

Classes:
- RegionMSweep
"""

from typing import Any, Dict, Iterator, List, Tuple

from sortedcontainers import SortedSet

from sources.algorithms.sweepln.msweepln import MSweepln, MSweepRunner
from sources.algorithms.sweepln.sweepln import Sweepln, SweepRunner
from sources.algorithms.sweepln.regionsweep import RegionSweep
from sources.datastructs.abstract.timeline import Timeline
from sources.datastructs.datasets.regionset import RegionSet
from sources.datastructs.datasets.regiontime import RegionEvent, RegionEvtKind
from sources.datastructs.shapes.region import Region, RegionIntxn


RegionIDs = Tuple[str, ...]

def toregionids(rintxns: RegionIntxn) -> RegionIDs:
  return tuple(sorted(map(lambda r: r.id, rintxns)))

def toregions(rids: RegionIDs, regions: RegionSet) -> RegionIntxn:
  return list(map(lambda r: regions[r], sorted(rids)))


class RegionMSweep(RegionSweep, MSweepRunner[Region, Iterator[RegionIDs]]):
  """
  Class for implementing an multi-pass sweep-line algorithm over a set of
  Regions. Binds to and is evaluated by the multi-pass sweep-line algorithm
  along a dimension on the set of Regions.

  Attributes:
    members:      Temporary set of tuples of intersecting
                  Regions all with k-length.

  Properties:
    intersects:   Resulting intersection Regions.
                  Alias for: self.overlaps

  Methods:
    Instance:     findintersects (alias: findoverlaps),
                  addintersect   (alias: addoverlap),
                  addintersects

  Inherited from RegionSweep:

    Attributes:
      id:         Unique identifier for this SweepRunner.
      events:     Mapping of Event kinds to callbacks.
      sweepln:    Sweepln algorithm for which its binded.
      timeline:   Timeline to evaluate sweep-line over.
      running:    Boolean flag for whether or not the
                  algorithm is currently running.
      dimension:  Dimension to evaluate sweep-line over.
      actives:    Active Regions during sweep-line.
      overlaps:   Resulting intersection Regions.

    Properties:
      binded:
        Whether or not this SweepRunner is binded to a
        Sweepln algorithm. True if it is binded, False 
        otherwise.
      initialized:
        Whether or not this SweepRunner has been
        initialized for evaluation. True if it is
        initialized, False otherwise.
      regions:
        The RegionSet to evaluate sweep-line over.

    Methods:
      Special:  __init__
      Instance: bind, unbind, results, hasevent,
                findoverlaps, addoverlap, onevent,
                oninit, onbegin, onend, onfinal

    Overridden Attributes:
      overlaps: Resulting intersecting Regions.

    Overridden Methods:
      Instance: results, findoverlaps, addoverlap,
                onbegin, onfinal

  Inherited from MSweepRunner:

    Attributes:
      nexttimeln:
        Timeline for the next pass of the MSweepln
        sweep-line algorithm.

    Properties:
      ismaster:
        Boolean flag. Whether or not this MSweepRunner
        is assigned as the master SweepRunner in MSweepln
        that generates the subsequent sweep-line passes.

    Methods:
      Instance: onsweep

    Overridden Methods:
      Instance: onsweep
  """
  overlaps: List[RegionIntxn]
  members: SortedSet

  ### Properties

  @property
  def intersects(self) -> List[RegionIntxn]:
    """
    The resulting intersecting Regions.
    Alias for: self.overlaps

    Returns:
      The resulting intersecting Regions.
    """
    return self.overlaps
  
  @intersects.setter
  def intersects(self, intersects: List[RegionIntxn]):
    """
    Assign the given intersects as the resulting intersecting Regions.
    Alias for: self.overlaps = intersects

    Args:
      intersects:
        The resulting intersecting Regions.
    """
    self.overlaps = intersects

  ### Methods: Overlaps

  def findoverlaps(self, region: Region) -> Iterator[RegionIntxn]:
    """
    Return an iterator over all the pairs of intersects between the
    given intersecting Region and the currently active intersecting Regions,
    as RegionIntxns. Alias for: self.findintersects(region)

    Args:
      region: The intersecting Region to find pairs of
              intersects with currently active 
              intersecting Regions, as RegionIntxns.

    Returns:
      An iterator over all the intersections between
      the intersecting Region and currently active
      intersecting Regions.
    """
    return self.findoverlaps(region)

  def addoverlap(self, regionintxn: RegionIntxn):
    """
    Add the given intersecting Regions to the list of intersects.
    This method should be overridden in subclasses to implement.
    Alias for: self.addintersect(regionintxn)

    Args:
      regionintxn:
        The intersecting Regions to add as intersects.
    """
    self.addoverlap(regionintxn)

  ### Methods: Intersects (Aliases for: Overlaps)

  def findintersects(self, region: Region) -> Iterator[RegionIntxn]:
    """
    Return an iterator over all the pairs of intersects between the
    given intersecting Region and the currently active intersecting Regions,
    as RegionIntxns.

    Args:
      region: The intersecting Region to find pairs of
              intersects with currently active 
              intersecting Regions, as RegionIntxns.

    Returns:
      An iterator over all the intersections between
      the intersecting Region and currently active
      intersecting Regions.
    """

    def match_elements(a: RegionIntxn, b: RegionIntxn) -> Tuple[RegionIntxn, RegionIntxn, RegionIntxn]:
      ab = []
      for region in reversed(a):
        if region in b:
          ab.append(region)
          a.remove(region)
          b.remove(region)
      return a, b, ab

    for _, active in self.actives.items():
      if region.overlaps(active):
        aintxn = region['intersect'] if 'intersect' in region.data else [region]
        bintxn = active['intersect'] if 'intersect' in active.data else [active]
        assert len(aintxn) == len(bintxn)

        a, b, ab = match_elements(aintxn.copy(), bintxn.copy())
        if len(a) == len(b) == 1 and len(ab) == len(aintxn) - 1:
          yield ab + a + b

  def addintersect(self, regionintxn: RegionIntxn):
    """
    Add the given intersecting Regions to the list of intersects.
    This method should be overridden in subclasses to implement.

    Args:
      regionintxn:
        The intersecting Regions to add as intersects.
    """
    self.members.add(toregionids(regionintxn))

  def addintersects(self):
    """
    Add the temporary intersecting Region members to the list of intersects.
    Clear SortedSet of temporary intersecting Region members.
    """
    for member in self.members:
      self.intersects.append(toregions(member, self.regions))

    self.members.clear()

  ### Methods: Results

  def results(self) -> Iterator[RegionIDs]:
    """
    Returns the iterator of intersecting Regions found in the RegionSet
    using the multi-pass sweep-line algorithm.

    Returns:
      The iterator of intersecting Regions.
    """
    return iter(self.intersects)

  ### Methods: Event Callbacks

  def onsweep(self, npass: int, **kwargs):
    """
    Initialize the runner for the next sweep/pass in the MSweepln algorithm.
    This method should be overridden in subclasses.

    Args:
      kwargs:   The additional arguments.
      npass:    The number of passes/sweeps already
                evaluated over the data.
    """
    if npass > 0:
      self.addintersects()
    else:
      self.members = SortedSet()

    MSweepRunner.onsweep(self, npass=npass, **kwargs)

  def onbegin(self, event: RegionEvent, npass: int, **kwargs):
    """
    When a Begin event is encountered in the RegionMSweep evaluation, 
    this method is invoked with that RegionEvent. Invokes findintersects and
    addintersect methods from here. Adds the newly active intersecting Region
    to the set of active intersecting Regions. Generate the Timeline Events
    for the next sweep-line pass.

    Args:
      event:
        The beginning event when encountered
        in the RegionMSweep evaluation.
      npass:
        The sweep count; number of the
        previous passes.
      kwargs:
        Additional arguments (unused)
    """
    assert isinstance(event, RegionEvent)
    assert self.binded and self.initialized

    region = event.context
    assert region.id not in self.actives

    for regionintxn in self.findintersects(region):
      self.addintersect(regionintxn)
      if self.ismaster:
        d = self.dimension
        rintxn = Region.from_intersect(regionintxn, True)
        assert isinstance(rintxn, Region)

        self.nexttimeln.put(RegionEvent(RegionEvtKind.Begin, rintxn[d].lower, rintxn, d))
        self.nexttimeln.put(RegionEvent(RegionEvtKind.End,   rintxn[d].upper, rintxn, d))

    self.actives[region.id] = region

  def onfinal(self, **kwargs):
    """
    Finalize the RegionMSweep for the MSweepln algorithm.
    When the MSweepln evaluation is complete, the sweep is complete,
    this method is invoked. Uninitialized this RegionMSweep.
    Sets the result value with the computed overlapping Regions.

    Args:
      kwargs:   The additional arguments.    
    """
    self.addintersects()

    RegionSweep.onfinal(self, **kwargs)
