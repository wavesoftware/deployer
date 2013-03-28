'''
Created on 27-01-2012

@author: ksuszynski
'''
import argparse
import deployers


description = 'Completely remove project directory. Use with caution!'
parser = argparse.ArgumentParser(description=description)
parser.add_argument('-p', '--project', 
    nargs=1, 
    required=True, 
    help="Project defined name"
)
parser.add_argument('-v','--verbose',
    default=False,
    action='store_const', 
    const=True,
    help="Show all messages"
)
parser.add_argument('-y','--yes',
    default=False,
    action='store_const', 
    const=True,
    help="Confirms all safety questions"
)

def run(args):
    parsed = parser.parse_args(args)
    project_name = parsed.project[0]
    v = parsed.verbose
    yes = parsed.yes
    
    deployer = deployers.create(project_name)
    return deployer.purge(project_name, yes, v)

def phelp():
    parser.print_help()

