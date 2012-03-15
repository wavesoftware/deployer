'''
Created on 27-01-2012

@author: ksuszynski
'''
import argparse
from configobj import ConfigObj
from util import SystemException
import subprocess
import sys
import config
import json
from os import path
from os import chdir

alias   = 'co'

description = 'Fetches tag for project and setups it'

parser = argparse.ArgumentParser(description=description, usage='%(prog)s checkout [options]')
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
    parsed = parser.parse_args(args)
    project_name = parsed.project[0]
    tag = parsed.tag[0]
    v = parsed.verbose
    
    projects_filename = path.join(config.dirs.root, 'projects.dat')
    try:
        projects_file = file(projects_filename)
        projects = json.loads(projects_file.read())
        projects_file.close()
    except:
        projects = {}
        
    try:
        project_dir = projects[project_name]
    except:
        print >> sys.stderr, 'Project is not being setuped! Use `%s init [dir]` first' % sys.argv[0]
        return 2
    
    ini = ConfigObj(path.join(project_dir, 'project.ini'))
    general = ini['general']
    
    scm = general['scm']
    uri = general['uri']
    tool = general['tool']
    if scm not in 'svn,git,hg'.split(','):
        raise SystemException('Invalid SCM type: %s in  config file: %s' % (scm, ini.filename))
    
    print 'Checkout of tag: %s' % tag
    
    tag_dir = path.join(project_dir, 'tags', tag)
    
    if not path.exists(tag_dir):
        
        if scm == 'svn':
            params = (uri, tag, tag_dir, general['username'], general['password'])
            __run('svn co --non-interactive --trust-server-cert %s/tags/%s %s --username=\'%s\' --password=\'%s\'' % params, v)
        if scm == 'git':
            params = (uri, tag_dir)
            __run('git clone %s %s' % params, v)
            chdir(tag_dir)
            __run('git checkout %s' % tag, v)
        if scm == 'hg':
            params = (uri, tag_dir)
            __run('hg clone %s %s' % params, v)
            chdir(tag_dir)
            __run('hg checkout %s' % tag, v)
    
    else:
        print 'Tag %s has already been checked out' % tag
    
    chdir(tag_dir)
    
    common_paths_file = path.join(tag_dir, 'config', 'sharedfiles.conf')
    if not path.exists(common_paths_file):
        common_paths_file = path.join(tag_dir, '.sharedfiles')
    if path.exists(common_paths_file):
        print 'Deleting shared directories and linking...'
        
        f = file(common_paths_file)
        common_paths = f.readlines()
        f.close()
        for pathd in common_paths:
            pathd = pathd.strip()
            if pathd == '':
                continue
            target = '%s/data/%s' % (project_dir, pathd)
            tag_path = '%s/%s' % (tag_dir, pathd)
            if not path.exists(target):
                if path.isfile(tag_path):
                    __run('mkdir -p %s' % path.dirname(target), v)
                    __run('cp %s %s' % (tag_path, target), v)
                else:
                    __run('mkdir -p %s' % target, v)
            __run('rm -Rf %s' % tag_path, v)
            if path.isfile(target):
                __run('ln %s %s' % (target, tag_path), v)
            else:
                __run('ln -s %s %s' % (target, tag_path), v)
    
    subprojects_file = path.join(tag_dir, '.subprojects')
    if not path.exists(subprojects_file):
        subprojects = ['.']
    else:
        f = file(subprojects_file)
        subprojects = f.readlines()
        f.close()
        
    for project_path in subprojects:
        project_path = project_path.strip()
        if project_path == '':
            continue
        subproject_dir = path.join(tag_dir, project_path)
        chdir(subproject_dir)
        if tool != 'none':
            print 'Setting up application: %s...' % project_path
            try:
                if tool == 'phing':
                    __run('phing setup -logger phing.listener.DefaultLogger', v)
                
                if tool == 'ant':
                    __run('ant setup', v)
            except:
                pass
        
    
    print "Done. Switch to this tag using command `%s switch --project %s --tag %s`" % (sys.argv[0], project_name, tag)
    
    return 0

def __run(cmd, verbose = False):
    if verbose:
        print '>>> ' + cmd
    subprocess.check_call(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)

def help():
    parser.print_help()

