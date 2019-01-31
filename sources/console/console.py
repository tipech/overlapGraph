#!/usr/bin/env python

"""
Console Commandline Handler

Implements the feature request https://github.com/pallets/click/issues/587
(with a few other related customizations), and acts as a drop-in replacement
module for import click. Based on: #issuecomment-410097642

Classes:
- Command   (ConsoleCommand)
- Group     (ConsoleGroup)
- Argument  (ConsoleArgument)

Decorators:
- command   (console_command)
- group     (console_group)
- argument  (console_argument)
"""

from typing import Callable, Dict, List, Tuple as PyTuple

import click

from click import * # pylint: disable=unused-wildcard-import
from docutils.frontend import OptionParser as DocOptParser
from docutils.nodes import document as Document, Element
from docutils.parsers.rst import Parser as RSTParser
from docutils.utils import new_document
from sphinxcontrib.napoleon import Config
from sphinxcontrib.napoleon.docstring import GoogleDocstring


def _deindent(text: str) -> List[str]:
  """
  Remove text indentation from the given text string.

  Args:
    text: The text to be processed.

  Returns:
    The list of unindented text.
  """
  lines, indent = text.split('\n'), -1

  for i, line in enumerate(lines):
    if len(line) == 0 or len(line.lstrip()) == 0:
      lines[i] = ''
    elif indent >= 0:
      lines[i] = line[indent:]
    else:
      noind  = line.lstrip()
      indent = len(line) - len(noind)
      lines[i] = noind

  return lines


def _parse_rst(text: List[str]) -> Document:
  """
  Parse the given list of text lines in the reStructuredText format.

  Args:
    text: The list of text lines parsed in the
          reStructuredText format.

  Returns:
    The Docutils document root.
  """
  parser   = RSTParser()
  settings = DocOptParser(components=(RSTParser,)).get_default_values()
  document = new_document('<rst-doc>', settings=settings)
  parser.parse('\n'.join(text), document)

  return document


class ConsoleCommand(click.Command):
  """
  Extends click.Command to support Arguments with help strings and
  automatically, generates help documentation from Google-styled docstrings.

  Commands are the basic building block of command line interfaces in
  Click. A basic command handles command line parsing and might dispatch
  more parsing to commands nested below it.

  Extends:
    click.Command

  Attributes:
    paramdocs:
      The mapping of the parameter name to
      the documentation text.
    sections:
      The list of sections in the order that they are to
      be displayed in the help output. All sections must
      correspond to a method on this Command with the
      name: 'format_{section}'. Enables custom sections
      to be added and sections to be reordered.
  
  Class Attributes:
    default_sections:
      The default list of sections in the order that they
      are to be displayed in the help output.
  """
  default_sections = ['usage', 'help_text', 'arguments', 'options', 'epilog']
  paramdocs: Dict[str, str]
  sections: List[str]

  def __init__(self, *args, sections = None, **kwargs):
    """
    Initialize extended click.Command to support Arguments with help strings
    and automatically, generate help documentation from Google-styled
    docstrings.

    Args:
      sections:
        The list of sections in the order that they are to
        be displayed in the help output.
      args, kwargs:
        Additional arguments to be passed to click.Command.
    """
    if 'help' in kwargs:
      help = kwargs['help']

    super().__init__(*args, **kwargs)
    self.paramdocs = self._getparams(help)
    self.sections  = sections or self.default_sections.copy()

  ### Method: Private Helpers

  def _getparams(self, docstring: str) -> Dict[str, str]:
    """
    Parse the given documentation string and extract the Args parameters.
    Returns a dictionary mapping the parameter name to the parameter text.

    Args:
      docstring:  The given documentation string to
                  extract the Args parameters from.

    Returns:
      The dictionary mapping the parameter name to
      the parameter text.
    """
    def elementByTagName(tagname: str):
      return lambda n: isinstance(n, Element) and n.tagname == tagname
    def getvalue(node, tagname: str) -> str:
      return node.traverse(elementByTagName(tagname))[0].astext()
    def param(node):
      return (getvalue(node, 'field_name'), getvalue(node, 'field_body'))

    params   = {}
    config   = Config(napoleon_use_param=True, napoleon_use_rtype=True)
    document = _parse_rst(GoogleDocstring(_deindent(docstring), config).lines())

    for node in document.traverse(elementByTagName('field')):
      name, value = param(node)
      if name.startswith('param '):
        name = name[len('param'):].lstrip()
        params[name] = value.replace('\n', ' ')

    return params

  ### Method: Sections

  def register_section(self, section: str, before: str = '<end>'):
    """
    Register the an existing section with the given section name
    in this Command and insert the section before the given section.
    If before is '<end>', appends the section at the end.
    If None or unknown section, does not insert section.
    If previously registered, first unregisters and then re-registers
    section; reordering sections.

    Args:
      section:  The section name.
      before:   The section to insert this new
                section before, or <end> to append
                this new section at the end.
    """
    method = f'format_{section}'

    assert section != before
    assert hasattr(self, method)

    if section in self.sections:
      self.sections.remove(section)

    if before == '<end>':
      self.sections.append(section)
    elif before in self.sections:
      index = self.sections.index(before)
      self.sections.insert(index, section)

  def add_section(self, section: str, before: str = '<end>') -> Callable:
    """
    Decorator that attaches the given function as a section of this Command,
    with the given section name and insert the section before the given
    section. If before is '<end>', appends the section at the end.
    If None or unknown section, does not insert section.

    Args:
      section:  The section name.
      before:   The section to insert this new
                section before, or <end> to append
                this new section at the end.
    
    Returns:
      The decorator.
    """
    def decorator(f: Callable) -> Callable:
      method = f'format_{section}'
      assert not hasattr(self, method)
      setattr(self, method, f)
      self.register_section(section, before)
      return f
    return decorator

  def update_section(self, section: str) -> Callable:
    """
    Decorator that updates an existing section with the given section name
    in this Command with the given function.

    Args:
      section:  The section name.
    
    Returns:
      The decorator.
    """
    def decorator(f: Callable) -> Callable:
      method = f'format_{section}'
      assert hasattr(self, method)
      setattr(self, method, f)
      return f
    return decorator

  ### Method: Formatting

  def format_help(self, ctx, formatter):
    """
    Writes the help into the formatter if it exists.

    Overrides:
      click.Command.format_help

    Args:
      ctx:
        The context object.
      formatter:
        The formatter object.
    """
    for section in self.sections:
      format_section = getattr(self, f'format_{section}')
      if callable(format_section):
        format_section(ctx, formatter)

  def format_options(self, ctx, formatter):
    """
    Writes all the options into the formatter if they exist.

    Overrides:
      click.Command.format_options

    Args:
      ctx:
        The context object.
      formatter:
        The formatter object.
    """
    opts = []
    for param in self.get_params(ctx):
      if not param.help and param.name in self.paramdocs:
        param.help = self.paramdocs[param.name]

      rv = param.get_help_record(ctx)
      if rv is not None and isinstance(param, click.Option):
        opts.append(rv)

    if opts:
      with formatter.section('Options'):
        formatter.write_dl(opts)

  def format_arguments(self, ctx, formatter):
    """
    Writes all the arguments into the formatter if they exist.

    Args:
      ctx:
        The context object.
      formatter:
        The formatter object.
    """
    args = []
    for param in self.get_params(ctx):
      if not param.help and param.name in self.paramdocs:
        param.help = self.paramdocs[param.name]
        param.hidden = False

      rv = param.get_help_record(ctx)
      if rv is not None and isinstance(param, click.Argument):
        args.append(rv)

    if args:
      with formatter.section('Arguments'):
        formatter.write_dl(args)


class ConsoleGroup(click.Group):
  """
  Extends click.Group to propagate support for Arguments
  with help strings.

  A group allows a command to have subcommands attached. This is the
  most common way to implement nesting in Click.

  Extends:
    click.Group
  """

  def command(self, *args, **kwargs):
    """
    A shortcut decorator for declaring and attaching a command to
    the group. This takes the same arguments as :func:`command` but
    immediately registers the created command with this instance by
    calling into :meth:`add_command`.

    Overrides:
      click.Group.command
    
    Args:
      args, kwargs:
        Arguments for click.Group.command.
    """
    cls = kwargs.pop('cls', ConsoleCommand) or ConsoleCommand

    return super().command(*args, cls=cls, **kwargs)

  def group(self, *args, **kwargs):
    """
    A shortcut decorator for declaring and attaching a group to
    the group. This takes the same arguments as :func:`group` but
    immediately registers the created command with this instance by
    calling into :meth:`add_command`.

    Overrides:
      click.Group.group
    
    Args:
      args, kwargs:
        Arguments for click.Group.group.
    """
    cls = kwargs.pop('cls', ConsoleGroup) or ConsoleGroup    

    return super().group(*args, cls=cls, **kwargs)


class ConsoleArgument(click.Argument):
  """
  Extends click.Argument to support help strings.

  Arguments are positional parameters to a command. They generally
  provide fewer features than options but can have infinite ``nargs``
  and are required by default.
  
  Extends:
    click.Argument

  Attributes:
    help:   The help documentation string.
    hidden: Hide this option from help outputs.
            Default is True, unless help is given.
  """
  help:   str
  hidden: bool

  def __init__(self, param_decls, help = None, hidden = None, **attrs):
    """
    Initialize extended click.Argument to support help strings.

    Args:
      help:
        The help documentation string.
      hidden:
        Hide this option from help outputs.
        Default is True, unless help is given.
      param_decls, required, attrs:
        Arguments to be passed to click.Argument.
    """
    super().__init__(param_decls, **attrs)

    self.help = help
    self.hidden = hidden if hidden is not None else not help

  def get_help_record(self, ctx) -> PyTuple[str, str]:
    """
    Returns a help record (argument, help documentation) that represent
    this ConsoleArgument.

    Args:
      ctx:  The context object.

    Return:
      The help record for this ConsoleArgument.
    """
    if self.hidden:
      return

    help = self.help or ''
    extra = []

    if self.default is not None:
      if isinstance(self.default, (list, tuple)):
        default_string = ', '.join('%s' % d for d in self.default)
      elif callable(self.default):
        default_string = "(dynamic)"
      else:
        default_string = self.default
      extra.append('default: {}'.format(default_string))

    if self.required:
      extra.append('required')
    if extra:
      help = '%s[%s]' % (help and help + '  ' or '', '; '.join(extra))

    return (f'{self.human_readable_name}:', help)


### Decorators

def console_command(name = None, cls = None, **attrs):
  return click.command(name=name, cls=cls or ConsoleCommand, **attrs)

def console_group(name = None, cls = None, **attrs):
  return click.group(name=name, cls=cls or ConsoleGroup, **attrs)

def console_argument(*param_decls, cls = None, **attrs):
  return click.argument(*param_decls, cls=cls or ConsoleArgument, **attrs)

### Polyfill Click

Command   = ConsoleCommand
Group     = ConsoleGroup
Argument  = ConsoleArgument

command   = console_command
group     = console_group
argument  = console_argument
