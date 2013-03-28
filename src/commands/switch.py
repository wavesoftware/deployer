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
import binascii

alias   = 'sw'

description = 'Switches project to target version and runs appopriate uninstall/install jobs'

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
        print >> sys.stderr, 'Project is not being setup! Use `deployproj init [dir]` first'
        return 2
    
    try:
        ini = ConfigObj(os.path.join(project_dir, 'project.ini'))
        general = ini['general']
        general['tool']
    except:
        print >> sys.stderr, "Unknown manage tool"
        return 3
    
    try:
        latest_dir = os.path.join(project_dir, 'src')
        tag_dir = os.path.join(project_dir, 'tags', tag)
        if not os.path.exists(tag_dir):
            print >> sys.stderr, "Tag %s has not been installed. Use checkout or register first!" % tag
            return 1
        
        subprojects_file = os.path.join(tag_dir, '.subprojects')
        if not os.path.exists(subprojects_file):
            subprojects = ['.']
        else:
            f = file(subprojects_file)
            subprojects = f.readlines()
            f.close()    
        
        if os.path.exists(latest_dir):
            __uninstall(subprojects, latest_dir, general, v)
        
        print "Switching version to tag: %s" % tag
        
        if os.path.exists(latest_dir):
            __run('rm -Rf %s/src' % project_dir, v)
        __run('ln -s %s %s/src' % (tag_dir, project_dir), v)
        
        __install(subprojects, tag_dir, general, v)
    
        print 'Done. Successfully switched to tag: %s for "%s"' % (tag, project_name)
        return 0
    except Exception, e:
        print >> sys.stderr, 'There was errors. Failed to switch to tag: %s for "%s"' % (tag, project_name)
        return (binascii.crc32(str(e)) % 255) + 1
        

def __install(subprojects, tag_dir, general, v):
    for project_path in subprojects:
        project_path = project_path.strip()
        if project_path == '':
            continue
        subproject_dir = os.path.join(tag_dir, project_path)
        os.chdir(subproject_dir)
        tool = general['tool']
        target = general['target_install']
        if tool != 'none' and target != 'None':
            
            print "Installing: %s" % project_path
            if tool == 'phing':
                __run('phing %s -logger phing.listener.DefaultLogger' % target, v)
            
            if tool == 'ant':
                __run('ant %s' % target, v)

def __uninstall(subprojects, latest_dir, general, verbose):
    for project_path in subprojects:
        project_path = project_path.strip()
        if project_path == '':
            continue
        subproject_dir = os.path.join(latest_dir, project_path)
        os.chdir(subproject_dir)
        tool = general['tool']
        target = general['target_uninstall']
        if tool != 'none' and target != 'None':
            print "Uninstalling previous version: %s" % project_path
            if tool == 'phing':
                __run('phing %s -logger phing.listener.DefaultLogger' % target, verbose)
            
            if tool == 'ant':
                __run('ant %s' % target, verbose)

def __run(cmd, verbose = False):
    if verbose:
        print '>>> ' + cmd
    ret = subprocess.check_call(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)
    if ret != 0:
        raise RuntimeError("Errors in command execution", ret)

def phelp():
    parser.print_help()