#!/usr/bin/env python

"""
Base26 Converter

Implements methods for converting from a decimal integer to a Base26 number
and from a Base26 number back to a decimal integer. A values in this numeric
representation are in uppercase A-Z letters. Used for generating shorter, more
readable Region or RegionSet IDs.

Example:
  A, B, C, ..., X, Y, Z, AA, AB, ...

Methods:
- to_base26
- from_base26
"""

from functools import reduce
from string import ascii_uppercase as alphabet


def to_base26(num: int) -> str:
  """
  Convert the given decimal integer to a Base26 number
  A numeric representation using only in uppercase A-Z letters.
  The integer must be greater than zero.

  Args:
    num:
      The decimal integer to be converted
      to a Base26 number.

  Returns:
    The str representation of a Base26 number.
  """
  assert num > 0

  def divmod_base26(n):
    a, b = divmod(n, 26)
    if b == 0:
      return a - 1, b + 26
    return a, b

  chars = []
  while num > 0:
    num, d = divmod_base26(num)
    chars.append(alphabet[d - 1])

  return ''.join(reversed(chars))


def from_base26(chars: str) -> int:
  """
  Convert the given Base26 number back to an integer.
  The Base26 numeric representation uses only in uppercase A-Z letters.

  Args:
    chars:
      The str representation of a Base26 number
      to be converted to an int.

  Returns:
    The numeric representation as an int.
  """
  assert len(chars) > 0

  return reduce(lambda r, x: r * 26 + x + 1, \
                map(alphabet.index, chars), 0)
