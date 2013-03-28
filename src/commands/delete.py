'''
Created on 27-01-2012

@author: ksuszynski
'''
import argparse
import deployers

alias   = 'del'

description = 'Deletes projects version'

parser = argparse.ArgumentParser(description=description, usage='%(prog)s delete [options]')
parser.add_argument('-p', '--project', 
    nargs=1, 
    required=True, 
    help="Project defined name"
)
parser.add_argument('-t', '--tag', 
    nargs=1, 
    required=True, 
    help="SCM Tag name ex.: 1.0.1"
)
parser.add_argument('-v','--verbose',
    default=False,
    action='store_const', 
    const=True,
    help="Show all messages"
)

def run(args):
    '''
    '''
    parsed = parser.parse_args(args)
    project_name = parsed.project[0]
    tag = parsed.tag[0]
    v = parsed.verbose
    
    deployer = deployers.create(project_name)
    return deployer.delete(project_name, tag, v)

def phelp():
    parser.print_help()