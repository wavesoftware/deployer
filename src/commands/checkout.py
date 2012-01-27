'''
Created on 27-01-2012

@author: ksuszynski
'''
import argparse
import os
from configobj import ConfigObj
from util import BussinessLogicException

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
    
    scm = config['scm']
    uri = config['uri']
    if scm not in 'svn,git,hg'.split(','):
        raise BussinessLogicException('Invalid SCM type: %s in  config file: %s' % (scm, config.filename))
    
    commands = []
    if scm == 'svn':
        params = (uri, tag, config['username'], config['password'])
        commands.append('svn co %s/tags/%s --username=\'%s\' --password=\'%s\'' % params)
    if scm == 'git':
        params = (uri, dir, tag)
        commands.append('git clone %s %s/tags/%s' % params)
    if scm == 'hg':
        params = (uri, dir, tag)
        commands.append('hg clone %s %s/tags/%s' % params)
    
    params = (dir, tag)
    commands.append('cd %s/tags/%s' % params)
    commands.append('phing setup')
    return 0

def help():
    parser.print_help()

