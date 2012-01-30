'''
Created on 27-01-2012

@author: ksuszynski
'''
import subprocess
import sys
import argparse
import config
import os
import json

description = 'Print project version'

parser = argparse.ArgumentParser(description=description, usage='%(prog)s version [options]')
parser.add_argument('-p', '--project', 
    nargs=1, 
    required=True, 
    help="Project defined name"
)

def run(args):
    parsed = parser.parse_args(args)
    project_name = parsed.project[0]
    
    projects_filename = os.path.join(config.dirs.root, 'projects.dat')
    try:
        projects_file = file(projects_filename)
        projects = json.loads(projects_file.read())
        projects_file.close()
    except:
        projects = {}
        
    try:
        project_dir = projects[project_name]
    
        real = os.path.realpath(os.path.join(project_dir, 'src'))
        tag = os.path.basename(real)
    except:
        tag = None
        project_dir = 'Not available'
        
    print "Project: %s (%s)" % (project_name, project_dir)
    if tag:        
        print ''
        print 'Installed project versions:'
        
        try: 
            tags_dir = os.path.join(project_dir, 'tags')
            for version in os.listdir(tags_dir):
                version = str(version)
                if version[0] == '.':
                    continue
                v_author = subprocess.check_output('ls -ld %s/%s | cut -d \' \' -f 3' % (tags_dir, version), shell=True).strip()
                v_date = subprocess.check_output('ls -ld %s/%s | cut -d \' \' -f 6' % (tags_dir, version), shell=True).strip()
                v_time = subprocess.check_output('ls -ld %s/%s | cut -d \' \' -f 7' % (tags_dir, version), shell=True).strip()
                
                if version == tag:
                    line = ' * '
                else:
                    line = '   '
                line += "%s    %s   %s %s" % (version, v_author, v_date, v_time)
                print line
        except:
            print '>> None <<'
        print ''        
        print "Actual varsion: %s" % tag        
    print ''        


def __run(cmd, verbose = False):
    if verbose:
        print '>>> ' + cmd
    subprocess.check_call(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)

def help():
    parser.print_help()