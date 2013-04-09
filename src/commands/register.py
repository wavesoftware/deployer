'''
Created on 28-03-2013

@author: ksuszyns
'''
import argparse
import re
from util import SystemException
import os
from deployers import get_project_dir
import sys
import deployers
import binascii
import shutil
from deployer import retcode

alias   = 'reg'

description = 'Registers file as a project tag and setups it'

parser = argparse.ArgumentParser(description=description, usage='%(prog)s register [options]')
parser.add_argument('-p', '--project', 
    nargs=1, 
    required=True, 
    help="Project defined name"
)
parser.add_argument('-f', '--file', 
    nargs=1, 
    required=True, 
    help='artifact file or directory name to install. You can pass absolute file path, scp path or http/ftp path. Examples, file: "/tmp/artifact.war", scp: "sourcehost.org:/tmp/artifact.war", http/ftp: "http://sourcehost.org/artifact.war"'
)
parser.add_argument('-t', '--tag', 
    nargs=1, 
    required=True, 
    help="Tag name ex.: r1.0.1"
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
    address = parsed.file[0]
    tag = parsed.tag[0]
    v = parsed.verbose
    
    ret = 0
    try:
        project_dir = get_project_dir(project_name)
        deployer = deployers.create(project_name)
        
        
        tag_dir = os.path.join(project_dir, 'tags', tag)
            
        if os.path.exists(tag_dir):
            print >> sys.stderr, 'Tag %s has already been checked out' % tag
        else:
            atype = __get_type(address)
            basename = os.path.basename(address)
            tmpnam = os.path.join('/tmp', basename)
            if atype == 'http':
                deployer.output('wget -O %s %s' % (tmpnam, address), v)
                if not os.path.isdir(tmpnam):
                    deployer.output('mkdir -p %s' % tag_dir, v)
                deployer.output('mv %s %s' % (tmpnam, tag_dir), v)
            if atype == 'scp':
                deployer.output('scp -r %s %s' % (address, tmpnam), v)
                if not os.path.isdir(tmpnam):
                    deployer.output('mkdir -p %s' % tag_dir, v)
                deployer.output('mv %s %s' % (tmpnam, tag_dir), v)
            if atype == 'local':
                if not os.path.isdir(address):
                    deployer.output('mkdir -p %s' % tag_dir, v)
                deployer.output('cp -R %s %s' % (address, tag_dir), v)
    except BaseException, e:
        ret = retcode(e)
        print >> sys.stderr, "There was errors during registering!!!: %s" % repr(e)
        if os.path.isdir(tag_dir):
            shutil.rmtree(tag_dir)
        else:
            os.unlink(tag_dir)
        return ret
    try:
        deployer.after_fetch(tag_dir, project_name, v)
        print ''
        print "Done. Switch to this tag using command `deployer switch --project %s --tag %s`" % (project_name, tag)
    except BaseException, e:
        ret = retcode(e)
        print >> sys.stderr, "There was errors during setup after registering!!!: %s" % repr(e)
    return ret

def __get_type(filename):
    http = re.compile('^(?:http|ftp)s?://[^/]{2,}/[^ ]+$', re.IGNORECASE)
    scp = re.compile('^(?:[a-z0-9_-]+@)?(?:[a-z0-9_-]+\.){1,}(?:[a-z0-9_-]{2,4}):"?[^ ]+"?$', re.IGNORECASE)
    local = re.compile('^/(?:[^/]+/)*.+$', re.IGNORECASE)
    if http.match(filename) != None:
        return 'http'
    if scp.match(filename) != None:
        return 'scp'
    if local.match(filename) != None:
        return 'local'
    raise SystemException('Invalid format of --file arg, Pass absolute file path, scp path or http/ftp path.')
def phelp():
    parser.print_help()