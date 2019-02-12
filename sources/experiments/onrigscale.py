#!/usr/bin/env python

"""
Experiments for Region Intersection Sensitivity + Scale

Experiments to analyze relationship between the number of Regions and
the number of Region overlaps, as well as relationship with between Regions
and overlaps when the density and size of Regions is changed.

Fixed:  - bounds:     0, 1000
        - rounds:     10
Series: - nregions:   10, 100, 1000, 10000
        - sizepc:     0.001, 0.01, 0.1
        - dimensions: 1, 2, 3
X:      - nregions:   10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000
        - sizepc:     0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1
Y:      - edges:      The number of overlapping Regions
        - isolated:   The percentage of unoverlapped Regions
        - degrees:    The average number of overlaps per Regions

Implements the Experiments:
- series(nregions),  x(sizepc)   -> y, fixed(dimension=2)
- series(sizepc),    x(nregions) -> y, fixed(dimension=2)
- series(dimension), x(sizepc)   -> y, fixed(nregions=1000)
- series(dimension), x(nregions) -> y, fixed(sizepc=0.01)

Classes:
- ExperimentsOnRIGScale
"""

from inspect import stack
from io import FileIO
from numbers import Number
from sys import stdout
from typing import Any, Callable, Dict, List, Union

from networkx import networkx as nx
from numpy import mean

from sources.abstract import Experiment
from sources.algorithms import NxGraphSweepCtor
from sources.core import Region, RegionSet

from .onregions import ExperimentsOnRegions


GraphCtor = Callable[[Experiment, str, Number], nx.Graph]


class ExperimentsOnRIGScale(ExperimentsOnRegions):
  """
  Experiments to analyze relationship between the number of Regions and
  the number of Region overlaps, as well as relationship with between Regions
  and overlaps when the density and size of Regions is changed.

  Extends:
    ExperimentsOnRegions
  """

  def __init__(self, logger: FileIO, istest: bool = True):
    """
    Initialize the experiments to analyze relationship between the number 
    of Regions and the number of Region overlaps, as well as relationship 
    with between Regions and overlaps when the density and size of Regions
    is changed.

    Args:
      logger: The logging output file.
      istest: Boolean flag for whether or not include all
              X or series values (full experiment). True for
              test mode with reduced X or series values;
              False for full experiment.
    """
    ExperimentsOnRegions.__init__(self, logger, istest)

    self.data['rounds']         = 10
    self.xmap['nregions']       = [10, 50, 100, 500, 1000] + self._addtests([5000, 10000, 50000, 100000])
    self.xmap['sizepc']         = [0.001, 0.002, 0.005, 0.01] + self._addtests([0.02, 0.05, 0.1])
    self.seriesmap['nregions']  = [10, 100, 1000, 10000]
    self.seriesmap['sizepc']    = [0.001, 0.01, 0.1]
    self.seriesmap['dimension'] = [1, 2, 3]
    self.measures['edges']      = lambda G: nx.number_of_edges(G)
    self.measures['isolated']   = lambda G: nx.number_of_isolates(G)/nx.number_of_nodes(G)
    self.measures['degrees']    = lambda G: mean([n[1] for n in nx.degree(G)])
    self.measures['cluster']    = lambda G: nx.average_clustering(G)

  ### Methods: Experiments

  def common_experiment(self, exp: Experiment, ctor: GraphCtor):
    """
    Evaluate the given experiment.

    Args:
      exp:
        The experiment to be evaluated.
      ctor:
        The constructor of Region intersection graph.
    """
    for x in exp.x:
      self.output_log(exp, {'x': x})
      for n in range(0, exp.rounds):
        self.output_log(exp, {'x': x, 'n': n})
        for s in exp.series:
          G = ctor(exp, s, x)
          y = [v(G) for _, v in self.measures.items()]
          self.output_log(exp, {'x': x, 'n': n, 'series': s, 'y': y})
          exp.sety((x, s), tuple(y))

    for measure in self.measures.keys():
      name  = f'{exp.name}_{measure}'
      scale = 'linear' if measure == 'isolated' else 'log'
      with open(f'data/{name}.csv', 'w', newline='') as f:
        exp.output_csv(f, measure)
      with open(f'data/{name}_lineplot.png', 'wb') as f:
        exp.output_lineplot(f, measure, title=name, xscale=scale, yscale=scale)
      with open(f'data/{name}_barchart.png', 'wb') as f:
        exp.output_barchart(f, measure, title=name, yscale=scale)

  ### Methods: Experiments

  def experiment_nregions_sizepc(self):
    exp  = self.construct_experiment()
    ctor = lambda exp, s, x: self.construct_graph(exp, s, x, 2)[1].G
    self.common_experiment(exp, ctor)

  def experiment_sizepc_nregions(self):
    exp  = self.construct_experiment()
    ctor = lambda exp, s, x: self.construct_graph(exp, x, s, 2)[1].G
    self.common_experiment(exp, ctor)

  def experiment_dimension_sizepc(self):
    exp  = self.construct_experiment()
    ctor = lambda exp, s, x: self.construct_graph(exp, 1000, x, s)[1].G
    self.common_experiment(exp, ctor)

  def experiment_dimension_nregions(self):
    exp  = self.construct_experiment()
    ctor = lambda exp, s, x: self.construct_graph(exp, x, 0.01, s)[1].G
    self.common_experiment(exp, ctor)
