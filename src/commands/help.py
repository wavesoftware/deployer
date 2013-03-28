'''
Created on 27-01-2012

@author: ksuszynski
'''

import config
import sys
from util import BussinessLogicException
import deployer

description = 'Prints this help, use `help command` for detailed help of command'

error = None

def run(args):
    try:
        helpcommand = args[0]
    except:
        helpcommand = None
    
    prog = deployer.deployer()
    
    if error != None:
        if isinstance(error, BussinessLogicException):
            print >> sys.stderr, error
        else:
            print >> sys.stderr, repr(error)

    print >> sys.stderr, config.program.description
    print >> sys.stderr, ''
    
    if not prog.has_command(helpcommand):
            
        print >> sys.stderr, 'Available commands:'
        for module in config.program.commands:
            name = '.'.join(module.__name__.split('.')[1:])
            try:
                desc = module.description
            except:
                desc = ''
            printed = name
            try:
                alias = module.alias
                printed += ', ' + alias
            except:
                alias = ''
            print >> sys.stderr, '    %s %s' % (printed.ljust(25), desc)
            
        print >> sys.stderr, ''
    
    else:
        print >> sys.stderr, prog.cmdmap[helpcommand].phelp()
    
    
    return 1