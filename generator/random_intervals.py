
# randomly generate intervals, and
# randomly choose values within an interval.

from sources.helpers import NDArray, RandomFn, Randoms





  def random_values(self, nvalues: int = 1, randomng: RandomFn = Randoms.uniform()) -> NDArray:
    """
    Randomly draw N samples from a given distribution or random number
    generation function. Samples are drawn over the interval [lower, upper)
    specified by this Interval. The given size N specifies the number of
    values to output. The default nvalues is 1; a single value is returned.
    Otherwise, a list with the specified number of samples are drawn.

    The default behavior is that samples are uniformly distributed. In other
    words, any value within the given interval is equally likely to be drawn
    by uniform. Other distribution or random number generation functions
    can be substituted via the `randomng` parameter.

    Args:
      nvalues:  The number of values to generate
      randomng: The random number generator that dictates
                the distribution of the values generated.

    Returns:
      List of randomly, sampled values drawn
      over this Interval.
    """
    assert isinstance(nvalues, int) and nvalues > 0
    assert isinstance(randomng, Callable)

    return randomng(nvalues, self.lower, self.upper)

  def random_intervals(self, nintervals: int = 1, sizepc: 'Interval' = None,
                             posnrng: RandomFn = Randoms.uniform(),
                             sizerng: RandomFn = Randoms.uniform(),
                             precision: int = None) -> List['Interval']:
    """
    Randomly generate N Intervals within this Interval, each with a random size
    as a percentage of the total Interval length, bounded by the given size
    percentage Interval (enclosed by Interval(0, 1)). The default distributions
    for choosing the position of the Interval and its size percentage are
    uniform distributions, but can be substituted for other distribution or
    random number generation functions via the `posnrng` and `sizerng`
    parameter. If precision is given, return the randomly generated Intervals
    where the lower and upper bounding values are rounded/truncated to the
    specified precision (number of digits after the decimal point).
    If precision is None, the lower and upper bounding values are of
    arbitrary precision.

    Args:
      nintervals: The number of Intervals to be generated.
      sizepc:     The size range as a percentage of the
                  total Interval length.
      posnrng:    The random number generator for choosing
                  the position of the Interval.
      sizerng:    The random number generator for choosing
                  the size of the Interval.
      precision:  The number of digits after the decimal
                  point for the lower and upper bounding
                  values, or None for arbitrary precision.

    Returns:
      List of randonly generated Intervals
      within this Interval.
    """
    if sizepc == None:
      sizepc = Interval(0, 1)
    if precision != None:
      assert isinstance(precision, int)

    assert isinstance(sizepc, Interval) and Interval(0, 1).encloses(sizepc)
    assert isinstance(posnrng, Callable) and isinstance(sizerng, Callable)

    intervals = []
    positions = self.random_values(nintervals, posnrng)
    lengths   = [s * self.length for s in sizepc.random_values(nintervals, sizerng)]

    for i in range(nintervals):
      length = lengths[i]
      position = positions[i]
      lower = position if position <= self.midpoint else max(position - length, self.lower)
      upper = min(lower + length, self.upper)
      if precision != None:
        lower = round(lower, precision)
        upper = round(upper, precision)
      intervals.append(Interval(lower, upper))

    return intervals