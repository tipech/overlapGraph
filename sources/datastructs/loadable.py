#!/usr/bin/env python

#
# datastructs/loadable.py - Base Definition for Loadable class
#
# This script implements an base class for deserialization of
# certain objects from various serialized data formats: JSON and
# Python Literal (parseable by ast.literal_eval). Provides base
# implements for from_text and from_source methods. Requires the
# concrete classes to implement the from_object method.
#

from ast import literal_eval as PythonParse
from io import TextIOBase
from json import load as JSONLoader
from json import loads as JsonParse
from typing import Any


class Loadable:
  """
  Abstract base class for deserialization of objects that implement
  this class (subclasses) from various serialized data formats: JSON and
  Python Literal (parseable by ast.literal_eval). Provides base implements
  for from_text and from_source methods. Requires the concrete classes to
  implement the from_object method.

  Class Methods:            from_text, from_source
  Abstract Class Methods:   from_object
  """

  @classmethod
  def from_object(cls, object: Any, **kvargs) -> 'Loadable':
    """
    Construct a new Loadable object from the conversion of
    the given object. Additional arguments passed via kvargs.
    Returns the new Loadable object.

    :param object:
    :param kvargs:
    """
    raise NotImplementedError

  @classmethod
  def from_text(cls, text: str, format: str = 'json', **kvargs) -> 'Loadable':
    """
    Construct a new Loadable object from the conversion of the given
    input text. The given input text can be either JSON or Python literal
    (parseable by ast.literal_eval). The parsed text is that passed to
    from_object to be converted into a Loadable object; thus, must
    have the necessary data structure and fields to be converted. Allowed
    formats are: 'json' and 'literal'. Unknown formats will raise ValueError.
    Returns the new Loadable object.

    :param text:
    :param format:
    :param kvargs:
    """
    if format == 'json':
      return cls.from_object(JsonParse(text), **kvargs)
    elif format == 'literal':
      return cls.from_object(PythonParse(text), **kvargs)
    else:
      raise ValueError(f'Unrecognized {cls.__name__} representation')

  @classmethod
  def from_source(cls, source: TextIOBase, format: str = 'json', **kvargs) -> 'Loadable':
    """
    Construct a new Loadable object from the conversion of the text from the given
    text input source. The given input source text can be either JSON or Python literal
    (parseable by ast.literal_eval). The parsed text is that passed to from_object to be
    converted into a Loadable object; thus, must have the necessary data structure
    and fields to be converted. Allowed formats are: 'json' and 'literal'. Unknown formats
    will raise ValueError. Returns the newly constructed Loadable object.

    :param source:
    :param format:
    :param kvargs:
    """
    assert source.readable()
    if format == 'json':
      return cls.from_object(JSONLoader(source), **kvargs)
    elif format == 'literal':
      return cls.from_object(PythonParse(source.read()), **kvargs)
    else:
      raise ValueError(f'Unrecognized {cls.__name__} representation')
