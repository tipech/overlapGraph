#!/usr/bin/env python

"""
Base Experiment

Defines a representation of an experiment along with helper methods
for making it easier to implement experiments. Experiments are defined
by a set of controlled variables, an independent variable and a dependent
variable. A list of values for the independent variable are along with the
set of controlled variables are specified. To compare multiple algorithms or
implementations, several data series can be provided. Provides method for
outputing and generating CSV as well as visualizations, via matplotlib.

Classes:
- Experiment
"""

from csv import DictWriter
from dataclasses import dataclass
from inspect import FrameInfo, stack
from io import FileIO
from numbers import Number
from os.path import basename
from time import perf_counter, strftime
from typing import Any, Dict, Generic, List, NamedTuple, Tuple, TypeVar, Union

from matplotlib import pyplot as plt
from numpy import arange, mean

from sources.helpers.randoms import Randoms


X = TypeVar('X', int, float)
Y = TypeVar('Y', int, float, Tuple[Number, ...])


class Xseries(NamedTuple):
  x: Number
  series: str


@dataclass
class Experiment(Generic[X, Y]): # pylint: disable=E1136
  """
  A representation of an experiment along with helper methods for making it
  easier to implement experiments. Experiments are defined by a set of
  controlled variables, an independent variable and a dependent variable.
  Provides method for outputing and generating CSV as well as visualizations,
  via matplotlib.

  Generics:
    X:  The independent variable as numeric values.
    Y:  The dependent variable as numeric values or
        multiple components, as a named tuple of
        numeric values.

  Attributes:
    name:   The name of the experiment.
    series: The data series names, for multiple
            algorithms or implementations.
    x, y:   The independent and dependent variable values.
            The dependent variable could have multiple
            components, as a named tuple.
    xname:  The name of the independent variable.
    ynames: The name of the dependent variable or the names
            of each component of the dependent variable.
    rounds: The number of times the experiment should
            evaluated from the same x and series.
            The dependent variable is the average value
            over these runs.
    data:   The controlled variables values and
            additional data properties.
  """
  name:   str
  series: List[str]
  x:      List[X]
  y:      Dict[Xseries, List[Y]]
  xname:  str
  ynames: Union[str, List[str]]
  rounds: int
  data:   Dict[str, Any]

  def __init__(self, name: str, xname: str, ynames: Union[str, List[str]],
                     series: List[str], x: List[X], rounds: int = 1, **data):
    """
    Initialize this abstract experiment with the necessary data series,
    controlled variables, values for the independent variable and the data
    structure to store values for the dependent variable.

    Args:
      name:   The name of the experiment.
      series: The data series names, for multiple
              algorithms or implementations.
      x:      The independent variable values.
      xname:  The name of the independent variable.
      ynames: The name of the dependent variable or the names
              of each component of the dependent variable.
      rounds: The number of times the experiment should
              evaluated from the same x and series.
              The dependent variable is the average value
              over these runs.
      data:   The controlled variables values and
              additional data properties.
    """
    self.name   = name
    self.series = series
    self.x      = x
    self.xname  = xname
    self.ynames = ynames
    self.rounds = rounds
    self.data   = data
    self.y      = {}

  ### Methods: Getters

  def gety(self, key: Union[Xseries, Tuple], measure: str = None) -> Union[Y, Number]:
    """
    Returns the averaged, dependent variable, y, value for the given
    independent variable, x, and series pair. If a specific Y-component,
    measure, is given, returns on that component's average value.

    Args:
      key:
        The independent variable, x, and series pair.
      measure:
        The specific Y component to return.

    Returns:
      The averaged, dependent variable values or the
      averaged value of specific component in the
      dependent variable.
    """
    assert isinstance(key, (Tuple, Xseries)) and len(key) == 2

    if key not in self.y or len(self.y[key]) == 0:
      return None
    if not isinstance(key, Xseries):
      key = Xseries(*key)

    ys = self.y[key]
    yv = tuple(mean(ys, axis=0)) if all([isinstance(y, Tuple) for y in ys]) else mean(ys)

    if isinstance(self.ynames, List) and measure in self.ynames:
      return yv[self.ynames.index(measure)]

    return yv

  def getseries(self, series: str, measure: str = None) -> List[Union[Y, Number]]:
    """
    Returns an list of averaged, dependent variable, y, values for the
    given series name, ordered by the independent variable, x, values.
    If a specific Y-component, measure, is given, returns on that
    component's average value.

    Args:
      series:
        The series name for which to return averaged,
        dependent variable, y, values, ordered by the
        independent variable, x, values.
      measure:
        The specific Y component to return.

    Returns:
      A List of averaged, dependent variable, y, values
      or the averaged value of specific component in the
      dependent variable.
    """
    assert series in self.series

    kv = {}
    for x, s in self.y.keys():
      if s == series:
        kv[x] = self.gety(Xseries(x, s), measure)

    for x in self.x: assert x in kv

    return [kv[x] for x in self.x]

  def getxy(self, xvalue: X, measure: str = None) -> List[Union[Y, Number]]:
    """
    Returns an dictionary mapping series names to averaged, dependent
    variable, y, values for the given independent variable, x, value.
    If a specific Y-component, measure, is given, returns on that
    component's average value.

    Args:
      xvalue:
        The independent variables, x, value for which
        to return averaged, dependent variable, y, values,
        ordered by the independent variable, x, values.
      measure:
        The specific Y component to return.

    Returns:
      A List of averaged, dependent variable, y, values
      or the averaged value of specific component in the
      dependent variable.
    """
    assert xvalue in self.x

    kv = {}
    for x, s in self.y.keys():
      if x == xvalue:
        kv[s] = self.gety(Xseries(x, s), measure)

    for s in self.series: assert s in kv

    return [kv[s] for s in self.series]

  ### Methods: Setters

  def sety(self, key: Union[Xseries, Tuple], y: Y):
    """
    Assigns the given dependent variable, y, value to the given
    independent variable, x, and series pair.

    Args:
      key:
        The independent variable, x, and series pair.
      y:
        The dependent variable, y, value.
    """
    assert isinstance(key, (Tuple, Xseries)) and len(key) == 2

    if not isinstance(key, Xseries):
      key = Xseries(*key)
    if key not in self.y:
      self.y[key] = []

    self.y[key].append(y)

  ### Methods: Outputs

  def output_csv(self, output: FileIO, measure: str = None, orientation = True):
    """
    Outputs this experiment's results to the given output file
    as a comma-separate values (CSV) file.

    Args:
      output:
        The CSV output file.
      measure:
        The specific Y component to return.
      orientation:
        Boolean flag for orientation of the values.
        True for series as rows, x values as columns.
        False for x values as rows, series as rows.
    """
    def xy(k, measure):
      r = {}
      for i, v in enumerate(kv(k, measure)):
        r[columns[i]] = v
      return r

    if orientation:
      rows = self.series
      columns = self.x
      kv = self.getseries
    else:
      rows = self.x
      columns = self.series
      kv = self.getxy

    writer = DictWriter(output, fieldnames=[self.xname, *columns])
    writer.writeheader()

    for r in rows:
      writer.writerow({self.xname: r, **xy(r, measure)})

  def output_lineplot(self, output: FileIO, measure: str = None, 
                            title: str = None, xscale: str = 'linear',
                            yscale: str = 'linear', **kwargs):
    """
    Outputs this experiment's results to the given output file
    as a plotted line chart.

    Args:
      output:   The output image file.
      measure:  The specific Y component to return.
      title:    The title for the line plot.
      xscale:   The x-axis scale type to apply.
      yscale:   The y-axis scale type to apply.
      kwargs:   Additonal arguments.
    """
    dfs = {
      'subplots': {'subplot_kw': {'aspect': 'auto'}},
      'suptitle': {'fontsize': 16},
      'legend':   {'loc': 'upper left', 'bbox_to_anchor': (1.05, 1), 'borderaxespad': 0.},
      'savefig':  {'bbox_inches': 'tight'}
    }

    rng  = Randoms.uniform()
    plot = lambda s: {'color': rng(3), 'label': s}
    kw   = lambda k, df: {**df, **kwargs[k]} if k in kwargs else df
    kwd  = lambda k: kw(k, dfs[k] if k in dfs else {})

    if isinstance(self.ynames, List):
      assert measure in self.ynames
    if isinstance(self.ynames, str):
      measure = self.ynames
    if not isinstance(title, str) or len(title) == 0:
      title = self.name

    fig, ax = plt.subplots(**kwd('subplots'))
    fig.suptitle(title, **kwd('suptitle'))

    for s in self.series:
      ax.plot(self.x, self.getseries(s, measure), **kw('plot', plot(s)))

    ax.set_xlabel(self.xname, **kwd('xlabel'))
    ax.set_xscale(xscale,     **kwd('xscale'))
    ax.set_ylabel(measure,    **kwd('ylabel'))
    ax.set_yscale(yscale,     **kwd('yscale'))
    ax.legend(**kwd('legend'))

    fig.savefig(output, **kwd('savefig'))
    plt.close(fig)

  def output_barchart(self, output: FileIO, measure: str = None,
                            title: str = None, yscale: str = 'linear',
                            width: float = 0.2, **kwargs):
    """
    Outputs this experiment's results to the given output file
    as a plotted bar chart.

    Args:
      output:   The output image file.
      measure:  The specific Y component to return.
      title:    The title for the bar chart.
      yscale:   The y-axis scale type to apply.
      width:    The width of each bar in the chart.
      kwargs:   Additonal arguments.
    """
    dfs = {
      'subplots': {'subplot_kw': {'aspect': 'auto'}},
      'suptitle': {'fontsize': 16},
      'legend':   {'loc': 'upper left', 'bbox_to_anchor': (1.05, 1), 'borderaxespad': 0.},
      'savefig':  {'bbox_inches': 'tight'}
    }

    rng  = Randoms.uniform()
    plot = lambda s: {'color': rng(3), 'label': s}
    bar  = lambda ind, w, i: ind - w*len(self.series)/2 + w*(i + 1/2)
    kw   = lambda k, df: {**df, **kwargs[k]} if k in kwargs else df
    kwd  = lambda k: kw(k, dfs[k] if k in dfs else {})

    if isinstance(self.ynames, List):
      assert measure in self.ynames
    if isinstance(self.ynames, str):
      measure = self.ynames
    if not isinstance(title, str) or len(title) == 0:
      title = self.name

    fig, ax = plt.subplots(**kwd('subplots'))
    fig.suptitle(title, **kwd('suptitle'))

    idx = arange(len(self.x))

    for i, s in enumerate(self.series):
      ax.bar(bar(idx, width, i), self.getseries(s, measure), width, **kw('plot', plot(s)))

    ax.set_xlabel(self.xname,  **kwd('xlabel'))
    ax.set_xticks(idx,         **kwd('xticks'))
    ax.set_xticklabels(self.x, **kwd('xticklabels'))
    ax.set_ylabel(measure,     **kwd('ylabel'))
    ax.set_yscale(yscale,      **kwd('yscale'))
    ax.legend(**kwd('legend'))

    fig.savefig(output, **kwd('savefig'))
    plt.close(fig)

  def output_log(self, output: FileIO, message: Union[str, Dict] = None,
                       msgprefix: str = '[{time}][{function}@{filename}:{lineno}][{name}]',
                       timestamp: str = '%Y-%m-%d %H:%M:%S %z',
                       caller: int = 1, **kwargs):
    """
    Outputs log entry during this experiment to the given output file.

    Args:
      output:     The output log file.
      message:    The output message as log entry. If None or
                  Dict, construct message from data property.
      msgprefix:  The string to prefix to output message.
      timestamp:  The string to format time stamps.
      caller:     The number of stack frames to associate
                  with log entry, to prepend function name
                  to log entry.
      kwargs:     The data properties to insert within
                  the given message string.
    """
    def msg(message) -> str:
      if message is None:
        return ' '.join([f'{k}={v}' for k, v in kwargs.items()])
      elif isinstance(message, Dict):
        return ' '.join([f'{k}={v}' for k, v in {**message, **kwargs}.items()])
      elif isinstance(message, NamedTuple):
        return ' '.join([f'{k}={v}' for k, v in {**message._asdict(), **kwargs}.items()])
      else:
        return message

    time, frame = strftime(timestamp), stack()[caller]._asdict()
    frame['filename'] = basename(frame['filename'])
    msgprefix = msgprefix.format(**{'time': time, 'name': self.name, **frame})
    message = message.format(**kwargs) if isinstance(message, str) else msg(message)

    output.write(f'{msgprefix}: {message}\n')
