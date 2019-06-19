#!/usr/bin/env python

"""
Base Definition for IOable class

Defines an abstract class for serialization and deserialization of certain
objects to/from JSON. Provides base implementations for to_JSON, and
from_JSON methods, as well as a direct properties-to-dict method. Requires
the concrete classes to implement the to_dict and from_dict methods.

Abstract Classes:
- IOable
"""

from abc import ABCMeta, abstractmethod
from io import TextIOBase
from json import JSONEncoder
from json import load as JSONLoader
from json import loads as JSONParse
from typing import Union, Dict


class IOable(metaclass=ABCMeta):
  """
  Abstract Class.

  Serialization and deserialization of objects that implement this class
  (subclasses) to/from JSON. Provides base implementations for to_JSON, and
  from_JSON methods, as well as a direct properties-to-dict method. Requires
  the concrete classes to implement the to_dict and from_dict methods.
  """


  ### Methods: (De)serialization

  def to_output(self, output: TextIOBase, **kwargs):
    """
    Outputs the given object to the given output stream in
    the JSON data representation format.

    Args:
      output:   The output stream to serialize object to.
      kwargs:   Additional arguments to be passed to the
                JSON encoder.

    """
    assert output.writable()

    default = JSONEncoder.default

    def json_encoder(value):
      if isinstance(value, IOable):
        return value.to_dict()
      elif hasattr(value, 'to_json'):
        return value.to_json()
      else:
        raise TypeError(f'{value}')

    if 'indent' not in kwargs:
      kwargs['indent'] = 2
    
    encoder = JSONEncoder(default=json_encoder, **kwargs)
    for chunk in encoder.iterencode(self):
      output.write(chunk)



  @classmethod
  def from_JSON(cls, source: Union[str, TextIOBase], **kwargs) -> 'IOable':
    """
    Construct a new IOable object from an input text or stream in JSON format.
    The parsed text is passed to from_dict and converted into a IOable object;
    thus, it must have the necessary data structure and fields to be converted

    Args:
      source:    The str or stream to be parsed and
                converted into an IOable object.
      kwargs:   Additional arguments to be passed to
                from_dict for customizing/tweaking the
                IOable object generation process.

    Returns:
      The newly constructed IOable object.

    """
    if isinstance(source, str):
      return cls.from_dict(JSONParse(source), **kwargs)
    elif source.readable():
      return cls.from_dict(JSONLoader(source), **kwargs)
    else:
      raise ValueError(f'Unsupported "{format}" input format')


  ### Methods: Object conversion

  @abstractmethod
  def to_dict(self) -> Dict:
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


  @classmethod
  @abstractmethod
  def from_dict(cls, object: Dict, **kwargs) -> 'IOable':
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
