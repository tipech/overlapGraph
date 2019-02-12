#!/usr/bin/env python

"""
Experiments for Region Intersection Query Performance

Experiments to analyze the performance of queries over Region sets and Region
intersection graphs. Analyzes the performance of the baseline Region cycle
sweep-line algorithm, Region intersection graph construction + clique
enumeration, and pre-constructed Region intersection graph clique enumeration
algorithms for enumerating all Region intersections, Region intersections with
a given subset, and a specific Region + its neighbors.

Fixed:  - bounds:     0, 1000
        - dimension:  2
Series: - method:     'base', 'rigctor', 'rigmdctor', 'rigprector'
X:      - nregions:   10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000
        - qsizepc:    0.01, 0.02, 0.05, 0.1, 0.2, 0.5
        - sizepc:     0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1
Y:      - elapsed:    The average elapsed time to evaluate each query.

Implements the Experiments:
- enumerate:  series(method), x(nregions) -> y, fixed(rounds=10, sizepc=0.01)
              series(method), x(sizepc)   -> y, fixed(rounds=10, nregions=1000)
- mrqenum:    series(method), x(nregions) -> y, fixed(rounds=100, qsizepc=0.1)
              series(method), x(qsizepc)  -> y, fixed(rounds=100, sizepc=0.01)
              series(method), x(sizepc)   -> y, fixed(rounds=100, nregions=1000)
- srqenum:    series(method), x(nregions) -> y, fixed(rounds=100, sizepc=0.01)
              series(method), x(sizepc)   -> y, fixed(rounds=100, nregions=1000)

Classes:
- ExperimentsOnRIQPerf
"""

from io import FileIO
from numbers import Number
from math import floor
from time import perf_counter
from typing import Callable, Dict, Iterator, List, Tuple

from sources.abstract import Experiment
from sources.algorithms.queries import Enumerate, MRQEnum, RegionIntersect, SRQEnum
from sources.algorithms.rigctor import NxGraphMdSweepCtor, NxGraphSweepCtor
from sources.core import NxGraph, Region, RegionSet
from sources.helpers import Randoms

from .onregions import ExperimentsOnRegions


RegionDataset   = Tuple[RegionSet, NxGraph]
RQEnum     = List[Region]
RegionDSCtor    = Callable[[Experiment, Number], RegionDataset]
RegionQueryRnd  = Callable[[Experiment, RegionSet, Number], RQEnum]
Algorithm       = Callable[[Experiment, RegionSet, NxGraph, RQEnum], Iterator[RegionIntersect]]


class ExperimentsOnRIQPerf(ExperimentsOnRegions):
  """
  Experiments to analyze the performance of queries over Region sets and
  Region intersection graphs. Analyzes the performance of the algorithms for
  each query type.

  Extends:
    ExperimentsOnRegions
  """

  def __init__(self, logger: FileIO, istest: bool = True):
    """
    Initialize the experiments to analyze the performance of queries over
    Region sets and Region intersection graphs. Analyzes the performance of
    the algorithms for each query type.

    Args:
      logger: The logging output file.
      istest: Boolean flag for whether or not include all
              X or series values (full experiment). True for
              test mode with reduced X or series values;
              False for full experiment.
    """
    ExperimentsOnRegions.__init__(self, logger, istest)

    self.xmap['nregions']    = [10, 50, 100, 500, 1000] + self._addtests([5000, 10000, 50000, 100000])
    self.xmap['sizepc']      = [0.001, 0.002, 0.005, 0.01] + self._addtests([0.02, 0.05, 0.1])
    self.xmap['qsizepc']     = [0.01, 0.02, 0.05, 0.1]  + self._addtests([0.2, 0.5])
    self.seriesmap['method'] = ['base', 'rigctor', 'rigmdctor', 'rigprector']
    self.measures['elapsed'] = getattr(self, 'measure_performance')

  ### Methods: Helpers

  def choose_query_subset(self, regions: RegionSet, qsizepc: float) -> RQEnum:
    """
    Randomly selects and generates a subset of Regions with the given
    query (subset) size as a percentage of the bounding Region.

    Args:
      regions:  The collection of Regions.
      qsizepc:  The query (subset) size as a percent
                of the bounding Region.

    Returns:
      The list of Regions to include with the
      subset of Regions.
    """
    size   = round(qsizepc * len(regions))
    subset = [r for i, r in enumerate(regions.shuffle()) if i < size]

    return subset

  def choose_query_region(self, regions: RegionSet) -> Region:
    """
    Randomly selects a Region from the given collection of Regions.

    Args:
      regions:  The collection of Regions.

    Returns:
      The Randomly selects a Region.
    """
    random = Randoms.uniform()
    index  = floor(random(upper=len(regions)))

    return regions[index]

  def measure_performance(self, exp: Experiment,
                                params: Tuple[str, Number, Number],
                                regions: RegionSet, graph: NxGraph,
                                query: RQEnum, alg: Algorithm) -> float:
    """
    Measure the performance of the given enumeration algorithm

    Args:
      exp:      The current experiment being performed.
      params:   The experiment parameters. A tuple
                of: series, x-value, and round number.
      regions:  The collection of Regions
      graph:    The Regions associated Region
                intersection graph, preconstructed.
      query:    The list of Regions to include in query.
      alg:      The method for generating the Iterators
                for this query method.

    Returns:
      The elapsed time for the enumeration of
      the query with the given evaluation method.
    """
    level = 0
    counter = {'length': 0}
    startclk = perf_counter()

    for _, (_, intersect) in enumerate(alg(regions, graph, query)):
      if level < len(intersect):
        level = len(intersect)
        counter[level] = 0

      counter[level] += 1
      counter['length'] += 1

    stopclk  = perf_counter()
    elapsed  = stopclk - startclk

    self.output_log(exp, {
      'params':   params,
      'start':    startclk,
      'stop':     stopclk,
      'elapsed':  elapsed,
      'count':    counter
    })

    return elapsed

  ### Methods: Common Experiments

  def common_experiment(self, exp: Experiment, ctor: RegionDSCtor, 
                              query: RegionQueryRnd,
                              algs: Dict[str, Algorithm]):
    """
    Evaluate the given experiment.

    Args:
      exp:    The experiment to be evaluated.
      ctor:   The method to construct the randomly
              generated Regions + associated Region
              intersection graph.
      query:  The method for randomly generating list
              of Regions to include in query.
      algs:   The methods for generating the Iterators
              for each query method.
    """
    for x in exp.x:
      self.output_log(exp, {'x': x})
      R, G = ctor(exp, x)
      for n in range(0, exp.rounds):
        self.output_log(exp, {'x': x, 'n': n})
        Q = query(exp, R, x)
        for s in exp.series:
          y = self.measures[exp.ynames](exp, (s, x, n), R, G, Q, algs[s])
          self.output_log(exp, {'x': x, 'n': n, 'series': s, 'y': y})
          exp.sety((x, s), y)

    with open(f'data/{exp.name}.csv', 'w', newline='') as f:
      exp.output_csv(f)
    with open(f'data/{exp.name}_lineplot.png', 'wb') as f:
      exp.output_lineplot(f, title=exp.name)
    with open(f'data/{exp.name}_barchart.png', 'wb') as f:
      exp.output_barchart(f, title=exp.name)

  def common_experiment_enumerate(self, exp: Experiment, ctor: RegionDSCtor):
    """
    Evaluate the given experiment for enumeration queries.

    Args:
      exp:    The experiment to be evaluated.
      ctor:   The method to construct the randomly
              generated Regions + associated Region
              intersection graph.
    """
    query = lambda exp, r, x: []

    self.common_experiment(exp, ctor, query, {
      'base':       lambda r, g, q: Enumerate.get('naive', r)(),
      'rigctor':    lambda r, g, q: Enumerate.get('slig', r)(),
      'rigmdctor':  lambda r, g, q: Enumerate.get('slig', r, ctor=NxGraphMdSweepCtor)(),
      'rigprector': lambda r, g, q: Enumerate.get('slig', g)()
    })

  def common_experiment_mrqenum(self, exp: Experiment, ctor: RegionDSCtor, query: RegionQueryRnd):
    """
    Evaluate the given experiment for subsetted enumeration queries.

    Args:
      exp:    The experiment to be evaluated.
      ctor:   The method to construct the randomly
              generated Regions + associated Region
              intersection graph.
      query:  The method for randomly generating list
              of Regions to include in query.
    """
    self.common_experiment(exp, ctor, query, {
      'base':       lambda r, g, q: MRQEnum.get('naive', r, q)(),
      'rigctor':    lambda r, g, q: MRQEnum.get('slig', r, q)(),
      'rigmdctor':  lambda r, g, q: MRQEnum.get('slig', r, q, ctor=NxGraphMdSweepCtor)(),
      'rigprector': lambda r, g, q: MRQEnum.get('slig', g, q)()
    })

  def common_experiment_srqenum(self, exp: Experiment, ctor: RegionDSCtor, query: RegionQueryRnd):
    """
    Evaluate the given experiment for neighbored enumeration queries.

    Args:
      exp:    The experiment to be evaluated.
      ctor:   The method to construct the randomly
              generated Regions + associated Region
              intersection graph.
      query:  The method for randomly generating list
              of Regions to include in query.
    """
    self.common_experiment(exp, ctor, query, {
      'base':       lambda r, g, q: SRQEnum.get('naive', r, q)(),
      'rigctor':    lambda r, g, q: SRQEnum.get('slig', r, q)(),
      'rigmdctor':  lambda r, g, q: SRQEnum.get('slig', r, q, ctor=NxGraphMdSweepCtor)(),
      'rigprector': lambda r, g, q: SRQEnum.get('slig', g, q)()
    })

  ### Methods: Experiments

  def experiment_enumerate_nregions(self):
    self.common_experiment_enumerate(
      self.construct_experiment(('method', 'nregions'), rounds=10),
      lambda exp, x: self.construct_graph(exp, x, 0.01, 2)
    )

  def experiment_enumerate_sizepc(self):
    self.common_experiment_enumerate(
      self.construct_experiment(('method', 'sizepc'), rounds=10),
      lambda exp, x: self.construct_graph(exp, 1000, x, 2)
    )

  def experiment_mrqenum_nregions(self):
    self.common_experiment_mrqenum(
      self.construct_experiment(('method', 'nregions'), rounds=100),
      lambda exp, x: self.construct_graph(exp, x, 0.01, 2),
      lambda exp, r, x: self.choose_query_subset(r, 0.1)
    )

  def experiment_mrqenum_sizepc(self):
    self.common_experiment_mrqenum(
      self.construct_experiment(('method', 'sizepc'), rounds=100),
      lambda exp, x: self.construct_graph(exp, 1000, x, 2),
      lambda exp, r, x: self.choose_query_subset(r, 0.1)
    )

  def experiment_mrqenum_qsizepc(self):
    self.common_experiment_mrqenum(
      self.construct_experiment(('method', 'qsizepc'), rounds=100),
      lambda exp, x: self.construct_graph(exp, 1000, 0.01, 2),
      lambda exp, r, x: self.choose_query_subset(r, x)
    )

  def experiment_srqenum_nregions(self):
    self.common_experiment_srqenum(
      self.construct_experiment(('method', 'nregions'), rounds=100),
      lambda exp, x: self.construct_graph(exp, x, 0.01, 2),
      lambda exp, r, x: self.choose_query_region(r)
    )

  def experiment_srqenum_sizepc(self):
    self.common_experiment_srqenum(
      self.construct_experiment(('method', 'sizepc'), rounds=100),
      lambda exp, x: self.construct_graph(exp, 1000, x, 2),
      lambda exp, r, x: self.choose_query_region(r)
    )
