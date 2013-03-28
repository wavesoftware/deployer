'''
Created on 27-01-2012

@author: ksuszynski
'''
import argparse
import deployers

description = 'Print project version'

parser = argparse.ArgumentParser(description=description, usage='%(prog)s version [options]')
parser.add_argument('-p', '--project', 
    nargs=1, 
    required=True, 
    help="Project defined name"
)

def run(args):
    parsed = parser.parse_args(args)
    project_name = parsed.project[0]
    
    deployer = deployers.create(project_name)
    return deployer.version(project_name)

def phelp():
    parser.print_help()