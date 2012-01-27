'''
Created on 27-01-2012

@author: ksuszynski
'''
import argparse
import os
import readline
from configobj import ConfigObj

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
    
    scm = raw_input('Choose SCM type [svn, hg, git]: ')
    uri = raw_input('Enter uri for project SCM code: ')
    
    filename = os.path.join(dir, 'project.ini')
    config = ConfigObj()
    config.filename = filename
    config['general'] = {}
    general = config['general']
    general['scm'] = scm
    general['uri'] = uri
    
    config.write()
    
    return 0

def help():
    parser.print_help()

