#!/usr/bin/env python

"""
Base Definition for IOable class

Defines an abstract class for serialization and deserialization of certain
objects to/from various serialized data formats: JSON and Python Literal
(parseable by ast.literal_eval). Provides base implements for to_output,
from_text and from_source methods. Requires the concrete classes to implement
the to_object and from_object method.

Abstract Classes:
- IOable
"""

from abc import ABCMeta, abstractmethod
from ast import literal_eval as PythonParse
from io import TextIOBase
from json import JSONEncoder
from json import load as JSONLoader
from json import loads as JSONParse
from typing import Any, Callable, Dict


class IOable(metaclass=ABCMeta):
  """
  Abstract Class.

  Serialization and deserialization of objects that implement this class
  (subclasses) to/from various serialized data formats: JSON and Python
  Literal (parseable by ast.literal_eval). Provides base implements for
  to_output, from_text and from_source methods. Requires the concrete
  classes to implement the to_object and from_object method.
  """

  ### Methods: Serialization

  def to_output(self, output: TextIOBase, format: str = 'json',
                      options: Dict = {}, **kwargs):
    """
    Outputs this object to the given output stream in the specified output
    data representation format.

    Args:
      output:   The output stream to serialize object to.
      format:   The output serialization format: 'json'.
      options:  The options to be passed to to_object
                via json_encoder_default, used to customize
                and tweak the object generation process.
      kwargs:   Additional arguments to be passed to the
                specific output format encoder.

    Raises:
      ValueError: If output format is unsupported.
    """
    assert output.writable()

    default = JSONEncoder.default

    def json_encoder(value):
      if isinstance(value, IOable):
        return value.__class__.to_object(value, **options)
      elif hasattr(value, 'to_json'):
        return getattr(value, 'to_json', default)(value, **options)
      else:
        raise TypeError(f'{value}')

    if format == 'json':
      if 'indent' not in kwargs:
        kwargs['indent'] = 2
      encoder = JSONEncoder(default=json_encoder, **kwargs)
      for chunk in encoder.iterencode(self):
        output.write(chunk)
    else:
      raise ValueError(f'Unsupported "{format}" output format')

  ### Class Methods: Serialization

  @classmethod
  @abstractmethod
  def to_object(cls, object: 'IOable', format: str = 'json', **kwargs) -> Any:
    """
    Abstract Definition.

    Generates an object (dict, list, or tuple) from the given IOable object
    that can be converted or serialized.

    Args:
      object:   The IOable object to be converted to an
                object (dict, list, or tuple).
      format:   The output serialization format: 'json'.
      kwargs:   Additional arguments to be used to
                customize and tweak the object generation
                process.

    Returns:
      The generated object (dict, list, or tuple).
    """
    raise NotImplementedError

  ### Class Methods: Deserialization

  @classmethod
  @abstractmethod
  def from_object(cls, object: Any, **kwargs) -> 'IOable':
    """
    Abstract Definition.

    Construct a new IOable object from the conversion of the given object.

    Args:
      object:   The object (dict, list, or tuple)
                to be converted into an IOable object.
      kwargs:   Additional arguments for customizing
                and tweaking the IOable object
                generation process.

    Returns:
      The newly constructed IOable object.
    """
    raise NotImplementedError

  @classmethod
  def from_text(cls, text: str, format: str = 'json', **kwargs) -> 'IOable':
    """
    Construct a new IOable object from the conversion of the given
    input text. The given input text can be either JSON or Python literal
    (parseable by ast.literal_eval). The parsed text is that passed to
    from_object to be converted into a IOable object; thus, must
    have the necessary data structure and fields to be converted.

    Args:
      text:     The str to be parsed and converted
                into an IOable object.
      format:   The serialization format: 'json' or
                'literal' (for ast.literal_eval).
      kwargs:   Additional arguments to be passed to
                from_object for customizing and
                tweaking the IOable object generation
                process.

    Returns:
      The newly constructed IOable object.

    Raises:
      ValueError: If input format is unsupported.
    """
    if format == 'json':
      return cls.from_object(JSONParse(text), **kwargs)
    elif format == 'literal':
      return cls.from_object(PythonParse(text), **kwargs)
    else:
      raise ValueError(f'Unsupported "{format}" input format')

  @classmethod
  def from_source(cls, source: TextIOBase,
                       format: str = 'json', **kwargs) -> 'IOable':
    """
    Construct a new IOable object from the conversion of the text from the
    given text input source. The given input source text can be either JSON or
    Python literal (parseable by ast.literal_eval). The parsed text is that
    passed to from_object to be converted into a IOable object; thus, must
    have the necessary data structure and fields to be converted.

    Args:
      source:   The input source whose content is
                to be converted into an IOable object.
      format:   The serialization format: 'json' or
                'literal' (for ast.literal_eval).
      kwargs:   Additional arguments to be passed to
                from_object for customizing and
                tweaking the IOable object generation
                process.

    Returns:
      The newly constructed IOable object.

    Raises:
      ValueError: If input format is unsupported.
    """
    assert source.readable()
    if format == 'json':
      return cls.from_object(JSONLoader(source), **kwargs)
    elif format == 'literal':
      return cls.from_object(PythonParse(source.read()), **kwargs)
    else:
      raise ValueError(f'Unsupported "{format}" input format')
