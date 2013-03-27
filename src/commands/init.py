'''
Created on 27-01-2012

@author: ksuszynski
'''
import argparse
import os
from configobj import ConfigObj
import sys
import urlparse
import getpass
import config
from os import path
import json

description = 'Initiate project structure'

parser = argparse.ArgumentParser(description=description)
parser.add_argument('dir',
    default=os.getcwd(),  
    nargs='?',
    help="Directory of project"
)

def _input(text, conf, default_name, default_value = None):
    try:
        default_value = conf[default_name]
    except:
        pass
    if default_value != None:
        default_txt = ' (confirm: %s)' % default_value
    else: 
        default_txt = '' 
    value = raw_input(text + '%s:' % default_txt)
    if value == '':        
        value = default_value
    return value

def run(args):
    parsed = parser.parse_args(args)
    project_dir = parsed.dir
    
    currdir = os.getcwd()
    if project_dir[0] != '/':
        project_dir = path.join(currdir, project_dir)
    project_dir = path.abspath(project_dir)
    if not path.isdir(project_dir):
        os.makedirs(project_dir)
    os.chdir(project_dir)
    
    if not path.isdir(path.join(project_dir, 'common')):
        os.mkdir(path.join(project_dir, 'common'))
    if not os.path.isdir(os.path.join(project_dir, 'tags')):
        os.mkdir(path.join(project_dir, 'tags'))
    
    projects_filename = path.join(config.dirs.root, 'projects.dat')
    try:
        projects_file = file(projects_filename)
        projects = json.loads(projects_file.read())
        projects_file.close()
    except:
        projects = {}
    
    
    filename = path.join(project_dir, 'project.ini')
    if path.exists(filename):
        ini = ConfigObj(filename)
        general = ini['general']
        project_name = general['name']
        print 'Using project: %s' % project_name
    else:
        ini = ConfigObj()
        ini.filename = filename
        ini['general'] = {}
        general = ini['general']
    
        while(True):
            project_name = raw_input('Enter project name (must be unique): ')
            if project_name not in projects:
                break
    common_file = os.path.join(project_dir, '.sharedfiles')
    print '''
Shared folders and files will be read from the file "%s".
This file should contain relative paths to files and 
directories that should be shared between versions of 
applications such as "web/upload" directory
    ''' % common_file    
    
    while(True):
        try:
            default = ' (set: %s)' % general['tool']
        except:
            default = ''
        tool = raw_input('Choose project management tool [phing, ant, none]%s: ' % default)
        if tool == '' and default != '':
            tool = general['tool']
        if tool not in 'phing,ant,none'.split(','):
            print >> sys.stderr, 'Invalid tool type: %s' % tool
        else:
            break
        
    if tool != 'none':
        general['target_setup'] = _input('Enter setup target', general, 'target_setup', 'build')
        general['target_install'] = _input('Enter install target', general, 'target_install')
        general['target_uninstall'] = _input('Enter uninstall target', general, 'target_uninstall')
        
    while(True):
        try:
            default = ' (set: %s)' % general['scm']
        except:
            default = ''        
        scm = raw_input('Choose SCM type [svn, hg, git]%s: ' % default)
        if scm == '' and default != '':
            scm = general['scm']
        if scm not in 'svn,git,hg'.split(','):
            print >> sys.stderr, 'Invalid SCM type: %s' % scm
        else:
            break
        
    while(True):
        try:
            default = ' (set: %s)' % general['uri']
        except:
            default = ''        
        uri = raw_input('Enter uri for project SCM code%s: ' % default)
        if uri == '' and default != '':
            uri = general['uri']
        uriparsed = urlparse.urlparse(uri)
        if uriparsed.hostname == None:
            print >> sys.stderr, 'Invalid uri: %s' % uri
        else:
            break
        
    
    general['name'] = project_name
    general['tool'] = tool
    
    if scm == 'svn':
        try:
            default = ' (set: %s)' % general['username']
        except:
            default = '' 
        username = raw_input('Enter SVN username%s:' % default)
        if username == '' and default != '':
            username = general['username']
        password = getpass.getpass('Enter SVN password:')
        general['username'] = username
        general['password'] = password
    
    general['scm'] = scm
    general['uri'] = uri
    
    ini.write()
    
    projects[project_name] = project_dir
    
    try:
        projects_file = file(projects_filename, 'w')
        projects_file.write(json.dumps(projects))
    finally:
        projects_file.close()
    
    print ''
    print 'Project %s is now setuped. Checkout some tag using `%s checkout --project %s --tag [tag]`' % (project_name, sys.argv[0], project_name)
    print ''
    return 0

def help():
    parser.print_help()

