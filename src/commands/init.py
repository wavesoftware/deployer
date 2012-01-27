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
import pickle
from os import path

description = 'Initiate project structure'

parser = argparse.ArgumentParser(description=description)
parser.add_argument('dir',
    default=os.getcwd(),  
    nargs='?',
    help="Directory of project"
)

def run(args):
    parsed = parser.parse_args(args)
    project_dir = parsed.dir
    
    currdir = os.getcwd()
    if project_dir[0] != '/':
        project_dir = path.join(currdir, project_dir)
    project_dir = path.abspath(project_dir)
    if not path.isdir(project_dir):
        os.mkdir(project_dir)
    os.chdir(project_dir)
    
    if not path.isdir(path.join(project_dir, 'common')):
        os.mkdir(path.join(project_dir, 'common'))
    if not os.path.isdir(os.path.join(project_dir, 'tags')):
        os.mkdir(path.join(project_dir, 'tags'))
    
    projects_filename = path.join(config.dirs.root, 'projects.pickle')
    try:
        projects_file = file(projects_filename)
        projects = pickle.loads(projects_file.read())
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
    
    while(True):
        scm = raw_input('Choose SCM type [svn, hg, git]: ')
        if scm not in 'svn,git,hg'.split(','):
            print >> sys.stderr, 'Invalid SCM type: %s' % scm
        else:
            break
        
    while(True):
        uri = raw_input('Enter uri for project SCM code: ')
        uriparsed = urlparse.urlparse(uri)
        if uriparsed.hostname == None:
            print >> sys.stderr, 'Invalid uri: %s' % uri
        else:
            break
    
    general['name'] = project_name
    
    if scm == 'svn':
        username = raw_input('Enter SVN username:')
        password = getpass.getpass('Enter SVN password:')
        general['username'] = username
        general['password'] = password
    
    general['scm'] = scm
    general['uri'] = uri
    
    ini.write()
    
    projects[project_name] = project_dir
    
    try:
        projects_file = file(projects_filename, 'w')
        projects_file.write(pickle.dumps(projects))
    finally:
        projects_file.close()
    
    return 0

def help():
    parser.print_help()

