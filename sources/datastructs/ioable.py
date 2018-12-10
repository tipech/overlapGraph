#!/usr/bin/env python

"""
datastructs/ioable.py - Base Definition for IOable class

This script implements an base class for (de)serialization of
certain objects to/from various serialized data formats: JSON and
Python Literal (parseable by ast.literal_eval). Provides base
implements for to_output, from_text and from_source methods.
Requires the concrete classes to implement the to_object and
from_object method.
"""

from ast import literal_eval as PythonParse
from io import TextIOBase
from json import JSONEncoder
from json import load as JSONLoader
from json import loads as JSONParse
from typing import Any, Dict


class IOable:
  """
  Abstract base class for (de)serialization of objects that implement
  this class (subclasses) to/from various serialized data formats: JSON and
  Python Literal (parseable by ast.literal_eval). Provides base implements
  for to_output, from_text and from_source methods. Requires the concrete
  classes to implement the to_object and from_object method.

  Method:                   to_output
  Class Methods:            from_text, from_source
  Abstract Class Methods:   to_object, from_object
  """

  def to_output(self, output: TextIOBase, format: str = 'json', options: Dict = {}, **kwargs):
    """
    Outputs this object to the given output stream in the specified
    output data representation format. The output format can be: 'json'.
    Generator options 'options' are passed to IOable.to_object, used to 
    customize and tweak the object generation process. Additional arguments
    passed via kwargs are passed to the specific output format encoder.

    :param output:
    :param format:
    :param options:
    :param kwargs:
    """
    assert output.writable()

    def generator(value):
      if isinstance(value, IOable):
        return value.__class__.to_object(value, format, **options)
      else:
        raise TypeError(f'{value}')

    if format == 'json':
      if 'indent' not in kwargs:
        kwargs['indent'] = 2
      encoder = JSONEncoder(default = generator, **kwargs)
      for chunk in encoder.iterencode(self):
        output.write(chunk)
    else:
      raise ValueError(f'Unsupported "{format}" output format')

  @classmethod
  def to_object(cls, object: 'IOable', format: str = 'json', **kwargs) -> Any:
    """
    Generates an object (dict, list, or tuple) from the given IOable object that
    can be converted or serialized as the specified data format: 'json'. Additional
    arguments passed via kwargs are used to customize and tweak the object
    generation process.

    :param object:
    :param format:
    :param kwargs:
    """
    raise NotImplementedError

  @classmethod
  def from_object(cls, object: Any, **kwargs) -> 'IOable':
    """
    Construct a new IOable object from the conversion of
    the given object. Additional arguments passed via kwargs.
    Returns the new IOable object.

    :param object:
    :param kwargs:
    """
    raise NotImplementedError

  @classmethod
  def from_text(cls, text: str, format: str = 'json', **kwargs) -> 'IOable':
    """
    Construct a new IOable object from the conversion of the given
    input text. The given input text can be either JSON or Python literal
    (parseable by ast.literal_eval). The parsed text is that passed to
    from_object to be converted into a IOable object; thus, must
    have the necessary data structure and fields to be converted. Allowed
    formats are: 'json' and 'literal'. Unknown formats will raise ValueError.
    Returns the new IOable object.

    :param text:
    :param format:
    :param kwargs:
    """
    if format == 'json':
      return cls.from_object(JSONParse(text), **kwargs)
    elif format == 'literal':
      return cls.from_object(PythonParse(text), **kwargs)
    else:
      raise ValueError(f'Unsupported "{format}" input format')

  @classmethod
  def from_source(cls, source: TextIOBase, format: str = 'json', **kwargs) -> 'IOable':
    """
    Construct a new IOable object from the conversion of the text from the given
    text input source. The given input source text can be either JSON or Python literal
    (parseable by ast.literal_eval). The parsed text is that passed to from_object to be
    converted into a IOable object; thus, must have the necessary data structure
    and fields to be converted. Allowed formats are: 'json' and 'literal'. Unknown formats
    will raise ValueError. Returns the newly constructed IOable object.

    :param source:
    :param format:
    :param kwargs:
    """
    assert source.readable()
    if format == 'json':
      return cls.from_object(JSONLoader(source), **kwargs)
    elif format == 'literal':
      return cls.from_object(PythonParse(source.read()), **kwargs)
    else:
      raise ValueError(f'Unsupported "{format}" input format')
