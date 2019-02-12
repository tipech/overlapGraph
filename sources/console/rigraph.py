#!/usr/bin/env python

"""
RIGraph Console Command-line Interface

Based on CommonConsole, with modifications and customization
for the RIGraphConsole.

Group:
- RIGraphConsole

Commands:
- generate
- convert
- enumerate
- visualize
- visualenum
"""

from .common import CommonConsole
from .console import Command, Group, Option


RIGraphConsole = Group(help='RIGraph (Region Intersection Graph) commands.')


for name, command in CommonConsole.commands.items():
  RIGraphConsole.add_command(command)
  for i, param in enumerate(command.params):
    # Set the 'kind' and 'srckind' to 'rigraph', convert to option.
    if param.name in ['kind', 'srckind']:
      opt = Option(('--' + param.name,), default='rigraph', hidden=True)
      command.params[i] = opt
    # Update 'source' help documentation.
    if param.name == 'source':
      param.help = 'The input source file to load graph of Regions from.'

  if name == 'generate':
    # Update 'generate' command help documentation.
    command.help = 'Randomly generate a new Region intersection graph.'
    for param in command.params:
      # Update 'output' + 'id' help documentations.
      if param.name == 'output':
        param.help = 'The file to save newly generated graph of Regions.'
      if param.name == 'id':
        param.help = 'The unique identifier for the RIGraph.'

  if name == 'convert':
    for param in command.params:
      # Set default 'outkind' for 'convert' command to 'regions'.
      if param.name == 'outkind':
        param.default = 'regions'
        param.required = False
