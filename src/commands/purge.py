'''
Created on 27-01-2012

@author: ksuszynski
'''
import argparse
import config
import os
import json
import sys
import subprocess

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

def run(args):
    parsed = parser.parse_args(args)
    project_name = parsed.project[0]
    v = parsed.verbose
    
    projects_filename = os.path.join(config.dirs.root, 'projects.dat')
    try:
        projects_file = file(projects_filename)
        projects = json.loads(projects_file.read())
        projects_file.close()
    except:
        projects = {}
        
    try:
        project_dir = projects[project_name]
    except:
        print >> sys.stderr, 'Project is not being managed! Mispelled?'
        return 2
    
    print 'Project: %s (%s)' % (project_name, project_dir)
    while(True):
        ans = raw_input('Do you relly want to delete whole project with all common data? [yes, NO]: ')
        if ans.lower() not in 'yes,no,'.split(','):
            pass
        else:
            break
    if ans.lower() == 'no' or ans == '':
        return 5
    
    del projects[project_name]
    
    try:
        projects_file = file(projects_filename, 'w')
        projects_file.write(json.dumps(projects))
    finally:
        projects_file.close()
    __run('rm -Rf %s' % project_dir, v)
    return 0

def __run(cmd, verbose = False):
    if verbose:
        print '>>> ' + cmd
    subprocess.check_call(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)

def phelp():
    parser.print_help()

