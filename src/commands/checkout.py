'''
Created on 27-01-2012

@author: ksuszynski
'''
import argparse
import os
from configobj import ConfigObj
from util import BussinessLogicException
import subprocess
import sys

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
    
    try:
        deploy_dir = os.environ['DEPLOY_TARGET_DIR']
    except:
        deploy_dir = '/var/www'
    if dir[0] != '/':
        dir = os.path.join(deploy_dir, dir)
    
    config = ConfigObj(os.path.join(dir, 'project.ini'))
    general = config['general']
    
    scm = general['scm']
    uri = general['uri']
    if scm not in 'svn,git,hg'.split(','):
        raise BussinessLogicException('Invalid SCM type: %s in  config file: %s' % (scm, config.filename))
    
    print 'Checkout of tag: %s' % tag
    
    tagDir = os.path.join(dir, 'tags', tag)
    
    if not os.path.exists(tagDir):
        
        if scm == 'svn':
            params = (uri, tag, tagDir, general['username'], general['password'])
            __run('svn co %s/tags/%s %s --username=\'%s\' --password=\'%s\'' % params)
        if scm == 'git':
            params = (uri, tagDir)
            __run('git clone %s %s' % params)
            __run('git checkout %s' % tag)
        if scm == 'hg':
            params = (uri, tagDir)
            __run('hg clone %s %s' % params)
            __run('hg checkout %s' % tag)
    
    else:
        print 'Tag %s has already been checked out' % tag
    
    os.chdir(tagDir)
    
    common_paths_file = os.path.join(tagDir, 'config', 'common-paths.conf')
    if os.path.exists(common_paths_file):
        print 'Deleting common directories and linking...'
        
        f = file(common_paths_file)
        common_paths = f.readlines()
        f.close()
        for path in common_paths:
            path = path.strip()
            target = '%s/data/%s' % (dir, path)
            tag_path = '%s/%s' % (tagDir, path)
            if not os.path.exists(target):
                if os.path.isfile(tag_path):
                    __run('mkdir -p %s' % os.path.dirname(target))
                    __run('cp %s %s' % (tag_path, target))
                else:
                    __run('mkdir -p %s' % target)
            __run('rm -Rf %s' % tag_path)
            __run('ln -s %s %s' % (target, tag_path))
        
    print 'Setting up application...'
    __run('phing setup -logger phing.listener.DefaultLogger')
    
    return 0

def __run(cmd):
    print '>>> ' + cmd
    subprocess.check_call(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)

def help():
    parser.print_help()

