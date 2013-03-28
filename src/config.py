'''
Created on 30-11-2011

@author: ksuszyns
'''

from util import D
from os import path
import commands.checkout
import commands.help
import commands.version
import commands.switch
import commands.list
import commands.delete
import commands.purge
import commands.init

program = D(
    description='deployer - Project deployment system',
    name='deployer',
    commands = (
        commands.checkout,
        commands.switch,
        commands.version, 
        commands.init, 
        commands.list, 
        commands.delete, 
        commands.purge, 
        commands.help
    ),
)
root = path.dirname(path.dirname(path.realpath(__file__)))

dirs = D(
    root = root,
    src = path.join(root, 'src'),
    bin = path.join(root, 'bin'),
    etc = path.join(root, 'etc')
)

program['installed'] = (dirs.root == '/usr/local/lib/%s' % program.name)
