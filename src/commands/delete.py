'''
Created on 27-01-2012

@author: ksuszynski
'''
import argparse
import subprocess
import os
import sys
import config
import json

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
    
    projects_filename = os.path.join(config.dirs.root, 'projects.dat')
    try:
        projects_file = file(projects_filename)
        projects = json.loads(projects_file.read())
        projects_file.close()
    except:
        projects = {}
    
    try:
        project_dir = projects[project_name]
        real = os.path.realpath(os.path.join(project_dir, 'src'))
        actual_tag = os.path.basename(real)
        tags_dir = os.path.join(project_dir, 'tags')
    except:
        print >> sys.stderr, 'Project is not being setuped! Use `%s init [dir]` first' % sys.argv[0]
        return 2
    
    if tag == actual_tag:
        print >> sys.stderr, 'Cant delete tag that is activly being used!'
        return 3
    
    target = os.path.join(tags_dir, tag)
    __run('rm -Rf %s' % target, v)
    
    print 'Tag: %s deleted for project: %s' % (tag, project_name)      
    

def __run(cmd, verbose = False):
    if verbose:
        print '>>> ' + cmd
    subprocess.check_call(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)

def help():
    parser.print_help()