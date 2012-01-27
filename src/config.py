'''
Created on 30-11-2011

@author: ksuszyns
'''

from util import D
import os.path
from ConfigParser import ConfigParser
import commands.checkout
import commands.help

program = D(
    description='Project deployment system - Mediovski 2012',
    name='deployproj',
    commands = (
        commands.checkout, 
        commands.help
    ),
    context = D(
        src_dir = os.path.dirname(os.path.realpath(__file__))
    )        
)
program.context['root_dir'] = os.path.dirname(program.context.src_dir)

installation = D(
    installed = False,
    properties = ConfigParser()
)
installation.properties.read([program.context.root_dir])

program['installed'] = (program.context.src_dir == '/usr/local/lib/deployproj/src')