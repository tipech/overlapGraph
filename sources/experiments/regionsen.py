#!/usr/bin/env python

"""
Experiments for Region Intersection (Edge) Sensitivity

Fixed:
- bounds:     [0, 1000]
- rounds:     10

Series:
- nregions:   [10, 100, 1000, 10000]
- sizepc:     [0.001, 0.01, 0.1]
- dimensions: [1, 2, 3]

X:
- nregions:   [10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000]
- sizepc:     [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1]

Y:
- edges:      The number of overlapping Regions
- isolated:   The percentage of unoverlapped Regions
- degrees:    The average number of overlaps per Regions

Implements the Experiments:
- series(nregions),  x(sizepc)   -> y, fixed(dimension=2)
- series(sizepc),    x(nregions) -> y, fixed(dimension=2)
- series(dimension), x(sizepc)   -> y, fixed(nregions=1000)
- series(dimension), x(nregions) -> y, fixed(sizepc=0.01)
"""

from csv import DictWriter
from inspect import stack
from typing import Callable, Dict, List, Union

from matplotlib import pyplot as plt
from networkx import networkx as nx
from numpy import mean

from sources.algorithms.rigctor.nxgsweepctor import NxGraphSweepCtor
from sources.datastructs.datasets.regionset import RegionSet
from sources.datastructs.rigraphs.nxgraph import NxGraph
from sources.datastructs.shapes.region import Region
from sources.helpers.randoms import Randoms


Number   = Union[int, float]
XYseries = Dict[Number, Dict[Number, Number]]


class RegionSensitivityExperiment:

  bounds: int
  rounds: int

  x_nregions:   List[int]
  x_sizepc:     List[float]
  s_nregions:   List[int]
  s_sizepc:     List[float]
  s_dimension:  List[int]

  y:      Dict[str, XYseries]
  calcs:  Dict[str, Callable]

  def __init__(self):
    self.bounds      = 1000
    self.rounds      = 10
    self.x_nregions  = [10, 50, 100, 500, 1000, 5000, 10000] #, 50000, 100000]
    self.x_sizepc    = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1]
    self.s_nregions  = [10, 100, 1000, 10000]
    self.s_sizepc    = [0.001, 0.01, 0.1]
    self.s_dimension = [1, 2, 3]

    self.y = {}
    self.calcs = {
      'edges':    lambda G: nx.number_of_edges(G),
      'isolated': lambda G: nx.number_of_isolates(G)/nx.number_of_nodes(G),
      'degrees':  lambda G: mean([n[1] for n in nx.degree(G)])
    }

  ### Methods: Helpers

  def log(self, message):
    print(f'{stack()[1][3]}: {message}')

  def construct_graph(self, nregions: int, sizepc: float, dimension: int) -> nx.Graph:
    bounds  = Region([0]*dimension, [self.bounds]*dimension)
    sizepr  = Region([0]*dimension, [sizepc]*dimension)
    regions = RegionSet.from_random(nregions, bounds=bounds, sizepc_range=sizepr)
    graph   = NxGraphSweepCtor.evaluate(regions)()

    self.log({
      'nregions': nregions,
      'sizepc': sizepc,
      'dimension': dimension
    })

    return graph.G

  def write_csv(self, name: str, series: List[Number], xs: List[Number], xys: XYseries):
    csv_filename = f'data/{name}.csv'

    with open(csv_filename, 'w', newline='') as output:
      self.log(csv_filename)

      csv = DictWriter(output, fieldnames=['series', *xs])
      csv.writeheader()

      for s, y in xys.items():
        csv.writerow({'series': s, **y})

  def draw_plot(self, name: str, series: List[Number], xs: List[Number], xys: XYseries, logscale = False):
    rng = Randoms.uniform()
    png_filename = f'data/{name}.png'

    with open(png_filename, 'wb') as output:
      self.log(png_filename)

      fig, ax = plt.subplots(subplot_kw={'aspect': 'auto'})
      fig.suptitle(name, fontsize=16)

      for s in series:
        ax.plot(xs, [xys[s][x] for x in xs], color=rng(3), label=s)

      if logscale:
        ax.set_yscale('log')

      ax.legend(loc='upper right', borderaxespad=0.)
      fig.savefig(output, bbox_inches='tight')

  def common_experiment(self, experiment, series, xvalues, ctor):
    key = lambda name: f'{experiment}_{name}'

    for name in self.calcs.keys():
      self.y[key(name)] = {}

    for s in series:
      self.log({'experiment': experiment, 'series': s})

      for name in self.calcs.keys():
        self.y[key(name)][s] = {}

      for x in xvalues: # x
        self.log({'experiment': experiment, 'x': x})

        for name in self.calcs.keys():
          self.y[key(name)][s][x] = 0

        for n in range(0, self.rounds):
          self.log({'experiment': experiment, 'round': n})
          G = ctor(s, x)

          for name, fn in self.calcs.items():
            self.y[key(name)][s][x] += fn(G)

        for name in self.calcs.keys():
          self.y[key(name)][s][x] /= self.rounds

    for name in self.calcs.keys():
      args = [key(name), series, xvalues, self.y[key(name)]]
      self.write_csv(*args)
      self.draw_plot(*args, name != 'isolated')

  ### Methods: Experiments

  def experiment_nregions_sizepc(self):
    ctor = lambda s, x: self.construct_graph(s, x, 2)
    self.common_experiment('nregions_sizepc', self.s_nregions, self.x_sizepc, ctor)

  def experiment_sizepc_nregions(self):
    ctor = lambda s, x: self.construct_graph(x, s, 2)
    self.common_experiment('sizepc_nregions', self.s_sizepc, self.x_nregions, ctor)

  def experiment_dimension_sizepc(self):
    ctor = lambda s, x: self.construct_graph(1000, x, s)
    self.common_experiment('dimension_sizepc', self.s_dimension, self.x_sizepc, ctor)

  def experiment_dimension_nregions(self):
    ctor = lambda s, x: self.construct_graph(x, 0.01, s)
    self.common_experiment('dimension_nregions', self.s_dimension, self.x_nregions, ctor)

  ### Class Methods: Run Experiments

  @classmethod
  def run_experiments(cls, experiments: List[str] = []):
    ex = cls()
    if len(experiments) == 0:
      for name in dir(ex):
        if callable(getattr(ex, name)) and name.startswith('experiment_'):
          getattr(ex, name)()
    else:
      for experiment in experiments:
        method = f'experiment_{experiment}'
        if hasattr(ex, method) and callable(getattr(ex, method)):
          getattr(ex, method)()
