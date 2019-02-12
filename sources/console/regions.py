#!/usr/bin/env python

"""
Regions Console Command-line Interface

Based on CommonConsole, with modifications and customization
for the RegionsConsole.

Group:
- RegionsConsole

Commands:
- generate
- convert
- enumerate
- visualize
- visualenum
"""

from .common import CommonConsole
from .console import Command, Group, Option


RegionsConsole = Group(help='Regions commands.')


for name, command in CommonConsole.commands.items():
  RegionsConsole.add_command(command)
  for i, param in enumerate(command.params):
    # Set the 'kind' and 'srckind' to 'regions', convert to option.
    if param.name in ['kind', 'srckind']:
      opt = Option(('--' + param.name,), default='regions', hidden=True)
      command.params[i] = opt
    # Update 'source' help documentation.
    if param.name == 'source':
      param.help = 'The input source file to load the set of Regions from.'

  if name == 'generate':
    # Update 'generate' command help documentation.
    command.help = 'Randomly generate a new collection of Regions.'
    for param in command.params:
      # Update 'output' + 'id' help documentations.
      if param.name == 'output':
        param.help = 'The file to save newly generated set of Regions.'
      if param.name == 'id':
        param.help = 'The unique identifier for the RegionSet.'

  if name == 'convert':
    for param in command.params:
      # Set default 'outkind' for 'convert' command to 'rigraph'.
      if param.name == 'outkind':
        param.default = 'rigraph'
        param.required = False
