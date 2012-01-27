'''
Created on 27-01-2012

@author: ksuszynski
'''
import argparse

alias   = 'co'

description = 'Fetches tag for project and setups it'

parser = argparse.ArgumentParser(description=description, usage='%(prog)s checkout [options]')
parser.add_argument('-d', '--dir', 
    nargs=1, 
    required=True, 
    help="Relative directory of project in ex.: 000/livespace"
)
parser.add_argument('-t', '--tag', 
    nargs=1, 
    required=True, 
    help="SCM Tag name ex.: 1.0.1"
)

def run(args):
    parsed = parser.parse_args(args)
    dir = parsed.dir[0]
    tag = parsed.tag[0]
    
    return 0

def help():
    parser.print_help()

