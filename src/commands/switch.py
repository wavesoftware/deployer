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

alias   = 'sw'

description = 'Switches project to tag and runs db migrate'

parser = argparse.ArgumentParser(description=description, usage='%(prog)s switch [options]')
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
    dir = parsed.dir[0]
    tag = parsed.tag[0]
    
    v = parsed.verbose
    
    try:
        deploy_dir = os.environ['DEPLOY_TARGET_DIR']
    except:
        deploy_dir = '/var/www'
    if dir[0] != '/':
        dir = os.path.join(deploy_dir, dir)
    
    tag_dir = os.path.join(dir, 'tags', tag)
    
    print "Switching version to tag: %s" % tag
    if not os.path.exists(tag_dir):
        print >> sys.stderr, "Tag %s has not been checked out. Use checkout first!" % tag
        return 1
    
    __run('rm -Rf %s/src' % dir, v)
    __run('ln -s %s %s/src' % (tag_dir, dir), v)

    print 'Done.'
    

def __run(cmd, verbose):
    if verbose:
        print '>>> ' + cmd
    subprocess.check_call(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)

def help():
    parser.print_help()