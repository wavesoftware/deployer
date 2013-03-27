#!/usr/bin/env python
'''
Created on 27-01-2012

@author: ksuszynski
'''
import sys
import argparse
import config
from util import BussinessLogicException
import binascii

class CommandNotFound(BussinessLogicException):
    def __str__(self):
        if self.message != None:
            return 'Command not found: %s' % self.message
        else:
            return 'Command not found'

class deployproj:
    
    def __init__(self):
        self.cmdlist = []
        self.cmdmap = {}
        for module in config.program.commands:
            name = '.'.join(module.__name__.split('.')[1:])
            self.cmdlist.append(name)
            self.cmdmap[name] = module
            try:
                self.cmdlist.append(module.alias)
                self.cmdmap[module.alias] = module
            except:
                pass
        
    def get_module(self, command):
        return self.cmdmap[command]
    
    def has_command(self, command):
        return command in self.cmdlist
    
    def run_command(self, command, cmdargs):
        if not self.has_command(command):
            raise CommandNotFound(command)
        return self.cmdmap[command].run(cmdargs)

if __name__ == '__main__':
    prog = deployproj()
    args = []
    try:
        try:
            conf = sys.argv[1]
            command = sys.argv[2]
        except:
            raise CommandNotFound(None)
        try:
            args = sys.argv[3:]
        except:
            pass
        if command != 'help':
            print config.program.description
            print ''
        code = prog.run_command(command, args)
    except IOError, e:
        code = binascii.crc32(str(e)) % 256
        print >> sys.stderr, str(e)
    except KeyboardInterrupt:
        code = 9
    except EOFError:
        code = 10
    except Exception, e:
        prog.get_module('help').error = e
        code = prog.run_command('help', args)
        
    if code == None:
        code = 0
    print "\n"
    sys.exit(code)
