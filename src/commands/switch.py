'''
Created on 27-01-2012

@author: ksuszynski
'''
import argparse
import subprocess
from util import BussinessLogicException
from configobj import ConfigObj
import os
import sys
import config
import json

alias   = 'sw'

description = 'Switches project to tag and runs db migrate'

parser = argparse.ArgumentParser(description=description, usage='%(prog)s switch [options]')
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
    echo "Switching version to tag: $TAG"
    if [[ ! -d $PROJECT_DIR/tags/$TAG ]]; then
        log_failure_msg "Tag $TAG has not been checked out. Use checkout first!"
        exit 4
    fi
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
        
    project_dir = projects[project_name]
    
    tag_dir = os.path.join(project_dir, 'tags', tag)
    
    print "Switching version to tag: %s" % tag
    if not os.path.exists(tag_dir):
        print >> sys.stderr, "Tag %s has not been checked out. Use checkout first!" % tag
        return 1
    
    __run('rm -Rf %s/src' % project_dir, v)
    __run('ln -s %s %s/src' % (tag_dir, project_dir), v)
    
    print "Running DB migrate"
    os.chdir(tag_dir)
    __run('phing migrate -logger phing.listener.DefaultLogger', v)

    print 'Done. Successfully switched to tag: %s for "%s"' % (tag, project_name)
    

def __run(cmd, verbose = False):
    if verbose:
        print '>>> ' + cmd
    subprocess.check_call(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)

def help():
    parser.print_help()