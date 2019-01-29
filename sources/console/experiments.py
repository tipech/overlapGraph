#!/usr/bin/env python

from sys import argv, stdout

from sources.experiments.onrigscale import ExperimentsOnRIGScale
from sources.experiments.onriqperf import ExperimentsOnRIQPerf


if __name__ == "__main__":
  with stdout as logger:
    ExperimentsOnRIGScale.evaluate(argv[1:], logger)
    ExperimentsOnRIQPerf.evaluate(argv[1:], logger)
