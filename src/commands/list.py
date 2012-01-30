'''
Created on 27-01-2012

@author: ksuszynski
'''
import config
import os
import json
import subprocess
import sys

description = 'Prints all installed projects'

def run(args):
    projects_filename = os.path.join(config.dirs.root, 'projects.dat')
    try:
        projects_file = file(projects_filename)
        projects = json.loads(projects_file.read())
        projects_file.close()
    except:
        projects = {}
        
    print 'Managed projects:'
    no = True
    for project_name, project_dir in projects.items():
        
        try:
            real = os.path.realpath(os.path.join(project_dir, 'src'))
            tag = os.path.basename(real)
            v_author = subprocess.check_output('ls -ld %s | cut -d \' \' -f 3' % real, shell=True).strip()
            v_date = subprocess.check_output('ls -ld %s | cut -d \' \' -f 6' % real, shell=True).strip()
            v_time = subprocess.check_output('ls -ld %s | cut -d \' \' -f 7' % real, shell=True).strip()
            no = False
        except:
            continue
            
        print " - %s %s %s %s %s" % (project_name.ljust(15), tag.ljust(8), v_author.ljust(15), v_date, v_time)
    if no:
        print 'There is no managed project. Initiate one using: %s init [dir]' % sys.argv[0]
    print ''

def __run(cmd, verbose = False):
    if verbose:
        print '>>> ' + cmd
    subprocess.check_call(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)

def help():
    print description