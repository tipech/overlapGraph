#!/usr/bin/env python

"""
Base Definition for IOable class

This script implements an base class for (de)serialization of certain objects
to/from various serialized data formats: JSON and Python Literal (parseable by
ast.literal_eval). Provides base implements for to_output, from_text and
from_source methods. Requires the concrete classes to implement the to_object
and from_object method.

Methods:
- json_encoder_default_factory

Classes:
- IOable
"""

from ast import literal_eval as PythonParse
from io import TextIOBase
from json import JSONEncoder
from json import load as JSONLoader
from json import loads as JSONParse
from typing import Any, Callable, Dict


def json_encoder_default_factory(
        withself: bool = False,
        default = JSONEncoder.default, **kwargs) -> Callable:
  """
  Returns a function that extends JSONEncoder to recognize other objects, by
  implementing a default() method with another method that returns a
  serializable object if possible, otherwise it should call the default
  implementation (to raise TypeError).

  Args:
    withself:
      Whether or not the function has self as the
      first argument, so that it can be attached
      to a class.
    default:
      The unmodified JSONEncoder.default method or
      base implementation that the new default()
      method falls back on.
    kwargs:
      Additional arguments used to customize and
      tweak the object generation process.

  kwargs:
    object_types:
      Outputs __type__ attribute to object output if True.
      The '__type__' attribute will hold the class
      name of the object type. Sometimes necessary for
      deserializing the output back in its in-memory
      object represectation.

  Factory for:
    json_encoder_default(self, value), if withself is True
    json_encoder_default(value), otherwise

    Args:
      self:
        JSONEncoder class
      value:
        The value to be converted to an object
        (dict, list, tuple).

    Returns:
      The object (dict, list, tuple) that
      represents the given value.

    Raises:
      TypeError: If object type is unrecognized.

  Returns:
    A function that extends JSONEncoder to
    recognize other objects.
  """
  def json_encoder_default(self, value):
    if isinstance(value, IOable):
      json_value = value.__class__.to_object(value, **kwargs)
      if 'object_types' in kwargs and kwargs['object_types'] \
                                  and isinstance(json_value, Dict):
        json_value['__type__'] = value.__class__.__name__

      return json_value
    if hasattr(value, 'to_json'):
      json_value = getattr(value, 'to_json', default)(value, **kwargs)
      if 'object_types' in kwargs and kwargs['object_types'] \
                                  and isinstance(json_value, Dict):
        json_value['__type__'] = value.__class__.__name__

      return json_value
    else:
      raise TypeError(f'{value}')

  def json_encoder_default_noself(value):
    return json_encoder_default(None, value)

  def json_encoder_default_setdefault(default):
    JSONEncoder.default = default

  json_encoder_default.default        = default
  json_encoder_default_noself.default = default
  json_encoder_default.setdefault     = \
      lambda: json_encoder_default_setdefault(json_encoder_default)
  json_encoder_default.resetdefault   = \
      lambda: json_encoder_default_setdefault(json_encoder_default.default)

  return json_encoder_default if withself else \
         json_encoder_default_noself


class IOable:
  """
  Abstract base class for (de)serialization of objects that implement
  this class (subclasses) to/from various serialized data formats: JSON and
  Python Literal (parseable by ast.literal_eval). Provides base implements
  for to_output, from_text and from_source methods. Requires the concrete
  classes to implement the to_object and from_object method.

  Method:
    Instance:       to_output
    Class Methods:  from_text, from_source
      Abstract:     to_object, from_object
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

    default = json_encoder_default_factory(**options)

    if format == 'json':
      if 'indent' not in kwargs:
        kwargs['indent'] = 2
      encoder = JSONEncoder(default=default, **kwargs)
      for chunk in encoder.iterencode(self):
        output.write(chunk)
    else:
      raise ValueError(f'Unsupported "{format}" output format')

  ### Class Methods: Serialization

  @classmethod
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
