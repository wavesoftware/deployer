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
from configobj import ConfigObj

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
    except:
        print >> sys.stderr, 'Project is not being setuped! Use `%s init [dir]` first' % sys.argv[0]
        return 2
    
    try:
        ini = ConfigObj(os.path.join(project_dir, 'project.ini'))
        general = ini['general']
        tool = general['tool']
    except:
        print >> sys.stderr, "Unknown manage tool"
        return 3
    
    tag_dir = os.path.join(project_dir, 'tags', tag)
    
    print "Switching version to tag: %s" % tag
    if not os.path.exists(tag_dir):
        print >> sys.stderr, "Tag %s has not been checked out. Use checkout first!" % tag
        return 1
    
    __run('rm -Rf %s/src' % project_dir, v)
    __run('ln -s %s %s/src' % (tag_dir, project_dir), v)
    
    subprojects_file = os.path.join(tag_dir, '.subprojects')
    if not os.path.exists(subprojects_file):
        subprojects = ['.']
    else:
        f = file(subprojects_file)
        subprojects = f.readlines()
        f.close()
        
    for project_path in subprojects:
        project_path = project_path.strip()
        if project_path == '':
            continue
        subproject_dir = os.path.join(tag_dir, project_path)
        os.chdir(subproject_dir)
        if tool != 'none':
            print "Running DB migrate: %s" % project_path
            try:
                if tool == 'phing':
                    __run('phing migrate -logger phing.listener.DefaultLogger', v)
                
                if tool == 'ant':
                    __run('ant migrate', v)
            except:
                pass    

    print 'Done. Successfully switched to tag: %s for "%s"' % (tag, project_name)
    

def __run(cmd, verbose = False):
    if verbose:
        print '>>> ' + cmd
    subprocess.check_call(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)

def help():
    parser.print_help()