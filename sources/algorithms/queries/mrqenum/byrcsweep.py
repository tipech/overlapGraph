#!/usr/bin/env python

"""
Enumeration Query of Multiple Intersecting Regions with Cyclic
Multi-pass Sweep-line Algorithm

Implements the MRQEnumByRCSweep class that performs the enumeration of
subsetted intersecting Regions within a RegionSet via a subscription to
RegionCycleSweep.

The enumeration outputs an Iterator of the restricted intersecting Regions as
tuple of Region intersection and RegionIntns in order of the number of
intersecting Regions and the position of the last intersecting Region's
Begin Event.

Classes:
- MRQEnumByRCSweep
"""

from typing import Any, Callable, Iterable, Iterator, List, Union

from sources.abstract import Subscriber
from sources.algorithms import RestrictedRegionCycleSweep, SweepTaskRunner
from sources.core import Region, RegionGrp, RegionSet

from ..enumerate import EnumerateByRCSweep, RegionIntersect


class MRQEnumByRCSweep(EnumerateByRCSweep):
  """
  Enumeration Query of Multiple intersecting Regions by Cyclic Multi-pass
  Sweep-line Algorithm. Computes an Iterator of subsetted intersecting Regions
  using the cyclic multi-pass sweep-line algorithm, through a subscription to
  RestrictedRegionCycleSweep.

  Extends:
    EnumerateByRCSweep
  """

  ### Class Methods: Evaluation

  @classmethod
  def evaluate(cls, regions: RegionSet,
                    subset: List[Union[Region, str]],
                    *subscribers: Iterable[Subscriber[RegionGrp]]) \
                    -> Callable[[Any], Iterator[RegionIntersect]]:
    """
    Factory function for computing an Iterator of subsetted intersecting
    Regions via the restricted cyclic multi-pass sweep-line algorithm.

    Overrides:
      EnumerateByRCSweep.evaluate

    Args:
      regions, subset:
        Arguments for RestrictedRegionCycleSweep
      subscribers:
        The other Subscribers to observe the
        cyclic multi-pass sweep-line algorithm.

    Returns:
      A function to evaluate the cyclic multi-pass
      sweep-line algorithm to compute the Iterator of
      subsetted intersecting Regions.

      Args:
        args, kwargs: Arguments for alg.evaluate()

      Returns:
        The resulting Iterator of subsetted
        intersecting Regions.
    """
    assert isinstance(regions, RegionSet)
    return SweepTaskRunner.evaluate(cls, RestrictedRegionCycleSweep, **{
      'subscribers': subscribers,
      'alg_args': [regions],
      'alg_kw': {'subset': subset}
    })
