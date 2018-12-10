#!/usr/bin/env python

"""
helpers/base26.py - Base26 Converter

This script implements methods for converting from a
decimal integer to a Base26 number and from a Base26
number back to a decimal integer. A values in this
numeric representation are in uppercase A-Z letters.
Used for generating shorter, more readable Region or
RegionSet IDs. For instance: 
 
- A, B, C, ..., X, Y, Z, AA, AB, ...
"""

from functools import reduce
from string import ascii_uppercase as alphabet


def _divmod_base26(n):
  a, b = divmod(n, 26)
  if b == 0:
    return a - 1, b + 26
  return a, b


def to_base26(num: int) -> str:
  """
  Convert the given decimal integer to a Base26 number
  A numeric representation using only in uppercase A-Z letters.
  The integer must be greater than zero.

  :param num:
  """
  assert num > 0

  chars = []
  while num > 0:
    num, d = _divmod_base26(num)
    chars.append(alphabet[d - 1])

  return ''.join(reversed(chars))


def from_base26(chars: str) -> int:
  """
  Convert the given Base26 number back to an integer.
  The Base26 numeric representation uses only in uppercase A-Z letters.

  :param chars:
  """
  assert len(chars) > 0

  return reduce(lambda r, x: r * 26 + x + 1, \
                map(alphabet.index, chars), 0)
