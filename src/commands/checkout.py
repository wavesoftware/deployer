'''
Created on 27-01-2012

@author: ksuszynski
'''
import argparse
from configobj import ConfigObj
from util import SystemException
import sys
import config
import json
import shutil
from os import path
from os import chdir
import binascii
import deployers
import time

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
    
    start_time = time.time()
    
    projects_filename = path.join(config.dirs.root, 'projects.dat')
    try:
        projects_file = file(projects_filename)
        projects = json.loads(projects_file.read())
        projects_file.close()
    except:
        projects = {}
        
    try:
        project_dir = projects[project_name]
        deployer = deployers.create(project_name)
    except:
        print >> sys.stderr, 'Project is not being setuped! Use `%s init [dir]` first' % config.program.name
        return 2
    
    try:
        ret = None
        ini = ConfigObj(path.join(project_dir, 'project.ini'))
        general = ini['general']
        
        scm = general['scm']
        if scm == 'none':
            print >> sys.stderr, '''
SCM repo is not set. Can't fetch a tag. 
Change it by `init` or use `register` command'''
            return 11
        uri = general['uri']
        if scm not in 'svn,git,hg,none'.split(','):
            raise SystemException('Invalid SCM type: %s in config file: %s' % (scm, ini.filename))
        
        print 'Checkout of tag: %s' % tag
        
        tag_dir = path.join(project_dir, 'tags', tag)
        
        if not path.exists(tag_dir):
            
            if scm == 'svn':
                params = (uri, tag, tag_dir, general['username'], general['password'])
                deployer.run('svn co --non-interactive --trust-server-cert %s/tags/%s %s --username=\'%s\' --password=\'%s\'' % params, v)
            if scm == 'git':
                params = (uri, tag_dir)
                deployer.run('git clone %s %s' % params, v)
                chdir(tag_dir)
                deployer.run('git checkout %s' % tag, v)
            if scm == 'hg':
                params = (uri, tag_dir)
                deployer.run('hg clone %s %s' % params, v)
                chdir(tag_dir)
                deployer.run('hg checkout %s' % tag, v)
        
        else:
            print >> sys.stderr, 'Tag %s has already been checked out' % tag
    except BaseException, e:
        ret = (binascii.crc32(repr(e)) % 255) + 1
        print >> sys.stderr, "There was errors during checkout!!!: %s" % repr(e)
        shutil.rmtree(tag_dir)
        return ret
    try:
        deployer.after_fetch(tag_dir, project_name, v)
        print ''
        print "Done. Switch to this tag using command `deployer switch --project %s --tag %s`" % (project_name, tag)
        print 'Completed in %.2f sec.' % (time.time() - start_time)
    except BaseException, e:
        ret = (binascii.crc32(repr(e)) % 255) + 1
        print >> sys.stderr, "There was errors during setup after checkout!!!: %s" % repr(e)
    
    return ret

def phelp():
    parser.print_help()

