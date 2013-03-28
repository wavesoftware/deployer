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
import deployers
import select
import validate
from util import SystemException

description = 'Initiate project structure. Use linux pipes to run in batch mode (pass a correct "project.ini" contents in STDIN).'

parser = argparse.ArgumentParser(description=description)
parser.add_argument('dir',
    default=os.getcwd(),  
    nargs='?',
    help="Directory of project (if not passed cwd is used instead)"
)

projects = None

def _input(text, conf, default_name, default_value = None):
    try:
        default_value = conf[default_name]
        if default_value == "None":
            default_value = None
    except:
        pass
    if default_value != None:
        default_txt = ' (confirm: %s)' % default_value
    else: 
        default_txt = '' 
    value = raw_input(text + '%s: ' % default_txt)
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
    
    open_projects()
    ini = init_project_ini(project_dir)
    general = ini['general']
    
    if select.select([sys.stdin,],[],[],0.0)[0]:
        (project_name, scm) = batch_setup(general, project_dir)
    else:
        (project_name, scm) = interactive_setup(general, project_dir)
    
    save_changes(ini)
    
    print ''
    print 'Project %s is now ready.' % project_name
    if scm != 'none':
        print 'Checkout some tag using `%s checkout --project %s --tag [tag]`' % (config.program.name, project_name)
    else:
        print 'Register an artifact as a tag using `%s register --project %s --file [artifact] --tag [tag]`' % (config.program.name, project_name)
    print ''
    return 0

def del_setting(general, key):
    try:
        del general[key]
    except:
        pass

def batch_setup(general, project_dir):
    try:
        stdinput = sys.stdin.readlines()
    except:
        pass
    vtor = validate.Validator()
    spec = os.path.join(config.root, 'src', 'configspec.ini')
    stdinput = ConfigObj(stdinput, configspec = spec)
    result = stdinput.validate(vtor, True)
    if result != True:
        raise SystemException("Passed input configuration has errors: " + str(result))
    for key in 'name,type,tool,scm,uri,username,password'.split(','):
        if stdinput['general'][key] != None:
            general[key] = stdinput['general'][key]
        else:
            del_setting(general, key)
    project_name = general['name']
    scm = general['scm']
    projects[project_name] = project_dir
    return (project_name, scm)

def interactive_setup(general, project_dir):
    project_name = set_project_name(general, project_dir)
    project_type = set_project_type(general, project_dir)
    tool = set_tool(general)
    scm = set_scm(general)
    uri = set_scmuri(general, scm)
    if scm == 'svn':
        set_svncredentials(general, scm)
    else:
        del_setting(general, 'username')
        del_setting(general, 'password')
    
    general['name'] = project_name
    general['type'] = project_type
    general['tool'] = tool
    general['scm'] = scm
    general['uri'] = uri
    projects[project_name] = project_dir
    
    return (project_name, scm)

def init_project_ini(project_dir):
    filename = path.join(project_dir, 'project.ini')
    if path.exists(filename):
        ini = ConfigObj(filename)
    else:
        ini = ConfigObj()
        ini.filename = filename
        ini['general'] = {}
    return ini
        

def open_projects():
    global projects
    projects_filename = path.join(config.dirs.root, 'projects.dat')
    try:
        projects_file = file(projects_filename)
        projects = json.loads(projects_file.read())
        projects_file.close()
    except:
        projects = {}

def save_changes(ini):
    projects_filename = path.join(config.dirs.root, 'projects.dat')
    ini.write()
    
    try:
        projects_file = file(projects_filename, 'w')
        projects_file.write(json.dumps(projects))
    finally:
        projects_file.close()
        
def set_project_name(general, project_dir):
    try:
        project_name = general['name']
        print 'Using project: %s' % project_name
    except:
        while(True):
            project_name = os.path.basename(project_dir)
            if project_name in projects:
                project_name = None  
            project_name = _input('Enter unique project name', general, 'name', project_name)
            if project_name not in projects:
                break
    return project_name

def set_project_type(general, project_dir):
    inputm = "Enter project's deployer number, supported types: \n"
    for idx in deployers.types:
        inputm += " [%d] %s\n" % (idx, deployers.types[idx].getDescription())
    inputm += " "
    while(True):
        project_type = _input(inputm, general, 'type')
        try:
            project_type = int(project_type)
        except:
            project_type = None
        if project_type not in deployers.types.keys():
            print >> sys.stderr, "Please, choose one of deplyers"
        else:
            break
    if deployers.types[project_type].supportsSharedfiles():
        print_sharedfiles_notice(project_dir)
    return project_type

def print_sharedfiles_notice(project_dir):
    common_file = os.path.join(project_dir, '.sharedfiles')
    print '''
Shared folders and files will be read from the file "%s".
This file should contain relative paths to files and 
directories that should be shared between versions of 
applications such as "web/upload" directory
        ''' % common_file 
        
def set_svncredentials(general, scm):
    """
    @type general: ConfigObj
    @param general: section general of ini config
    @type scm: string
    @param scm: scm type
    """    
    try:
        default = ' (confirm: %s)' % general['username']
    except:
        default = '' 
    username = raw_input('Enter SVN username%s:' % default)
    if username == '' and default != '':
        username = general['username']
    try:
        old_pass = general['password']
        passrepr = None
        if old_pass == 'None':
            old_pass = None
        else:
            passrepr = len(old_pass) * '*'
    except:
        old_pass = None
    def_pass = ''
    if passrepr != None:
        def_pass = ' (confirm: %s)' % passrepr
    
    password = getpass.getpass('Enter SVN password%s:' % def_pass)
    if password == '' and def_pass != '':
        password = general['password']
    general['username'] = username
    general['password'] = password

def set_scmuri(general, scm):
    """
    @type general: ConfigObj
    @param general: section general of ini config
    @type scm: string
    @param scm: scm type
    @return: scm repo uri
    @rtype: string
    """
    uri = None
    while(True and scm != 'none'):
        try:
            default = ' (confirm: %s)' % general['uri']
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
    return uri

def set_scm(general):
    """
    @type general: ConfigObj
    @param general: section general of ini config
    @rtype: string
    @return: selected scm
    """
    while(True):
        try:
            default = ' (confirm: %s)' % general['scm']
        except:
            default = ''        
        scm = raw_input('Choose SCM type [hg, git, svn, none]%s: ' % default)
        if scm == '' and default != '':
            scm = general['scm']
        if scm not in 'svn,git,hg,none'.split(','):
            print >> sys.stderr, 'Invalid SCM type: %s' % scm
        else:
            break
    return scm
def set_tool(general):
    """
    @type general: ConfigObj
    @param general: section general of ini config
    @rtype: string
    @return: selected tool
    """
    while(True):
        try:
            default = ' (confirm: %s)' % general['tool']
        except:
            default = ''
        tool = raw_input('Choose project management tool [phing, ant, maven, none]%s: ' % default)
        if tool == '' and default != '':
            tool = general['tool']
        if tool not in 'phing,ant,maven,none'.split(','):
            print >> sys.stderr, 'Invalid tool type: %s' % tool
        else:
            break
        
    if tool != 'none':
        general['target_setup'] = _input('Enter setup target', general, 'target_setup', 'build')
        general['target_install'] = _input('Enter install target', general, 'target_install')
        general['target_uninstall'] = _input('Enter uninstall target', general, 'target_uninstall')
    else:
        del_setting(general, 'target_setup')
        del_setting(general, 'target_install')
        del_setting(general, 'target_uninstall')
    
    return tool

def phelp():
    parser.print_help()

