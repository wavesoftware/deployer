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

description = 'Initiate project structure'

parser = argparse.ArgumentParser(description=description, usage='%(prog)s init [options]')
parser.add_argument('-d', '--dir', 
    default=os.getcwd(), 
    required=False, 
    help="Directory of project"
)

def run(args):
    parsed = parser.parse_args(args)
    dir = parsed.dir
    
    try:
        deploy_dir = os.environ['DEPLOY_TARGET_DIR']
    except:
        deploy_dir = '/var/www'
    if dir[0] != '/':
        dir = os.path.join(deploy_dir, dir)
    if not os.path.isdir(dir):
        os.mkdir(dir)
    os.chdir(dir)
    
    if not os.path.isdir(os.path.join(dir, 'common')):
        os.mkdir(os.path.join(dir, 'common'))
    if not os.path.isdir(os.path.join(dir, 'tags')):
        os.mkdir(os.path.join(dir, 'tags'))
    
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
    
    filename = os.path.join(dir, 'project.ini')
    config = ConfigObj()
    config.filename = filename
    config['general'] = {}
    general = config['general']
    
    if scm == 'svn':
        username = raw_input('Enter SVN username:')
        password = getpass.getpass('Enter SVN password:')
        general['username'] = username
        general['password'] = password
    
    general['scm'] = scm
    general['uri'] = uri
    
    config.write()
    
    return 0

def help():
    parser.print_help()

