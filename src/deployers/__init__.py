import abc
import os
import config
import json
from configobj import ConfigObj
import subprocess
import sys
import binascii
import time
from subprocess import CalledProcessError


class AbstractDeployer:
    __metaclass__ = abc.ABCMeta
    
    def __default_runner(self, cmd):
        return subprocess.check_call(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)
    def __default_output_runner(self, cmd):
        return subprocess.check_output(cmd, shell=True).strip()
    
    def set_runner(self, runner, output_runner):
        """
        @param runner: internal command runner (shell)
        @type runner: function
        @param output_runner: internal command runner returning output (shell)
        @type output_runner: function
        """
        self.__runner = runner
        self.__output_runner = output_runner
    
    def __init__(self):
        self.set_runner(AbstractDeployer.__default_runner, AbstractDeployer.__default_output_runner)
    
    def run(self, cmd, verbose = False, throw = True):
        if verbose:
            print '>>> ' + cmd
        ret = -999
        try:
            ret = self.__runner(self, cmd)
        except CalledProcessError, e:
            ret = e.returncode
            if throw:
                raise e
        if ret != 0 and throw:
            raise RuntimeError("Error[%d] in command execution: '%s'" % (ret, cmd))
        return ret
    
    def output(self, cmd, verbose = False, throw = False):
        if verbose:
            print '>>> ' + cmd
        ret = -999
        try:
            ret = self.__output_runner(self, cmd)
        except BaseException, e:
            ret = e.returncode
            if throw:
                raise e
        return ret
    
    @abc.abstractmethod
    def uninstall(self, project_name, tag, subprojects, targetpath, general, verbose = False):
        """
        Uninstalls tag before switch
        
        @type subprojects: list
        @param subprojects: list of sub paths to run install command to
        @type targetpath: string
        @param targetpath: path to install tag
        @type general: ConfigObj
        @param general: general section from INI file
        @type verbose: bool
        @param verbose: is verbose
        """        
        pass
    
    @abc.abstractmethod
    def install(self, project_name, tag, subprojects, targetpath, general, verbose = False):
        """
        Installs switched tag and runs all installation targets
        
        @type subprojects: list
        @param subprojects: list of sub paths to run install command to
        @type targetpath: string
        @param targetpath: path to install tag
        @type general: ConfigObj
        @param general: general section from INI file
        @type verbose: bool
        @param verbose: is verbose
        """
        pass
    
    def switch(self, project_name, tag, verbose = False):
        """
        Switches project to target version and runs appopriate uninstall/install jobs
        
        @type project_name: string
        @param project_name: a project name to work on
        @type tag: string
        @param tag: version to switch to
        @type verbose: bool
        @param verbose: is verbose
        @rtype: None
        """
        start_time = time.time()
        try:
            project_dir = get_project_dir(project_name)
        except:
            print >> sys.stderr, 'Project is not being setup! Use `deployer init [dir]` first'
            return 2
        
        try:
            general = get_ini(project_name)
            general['tool']
        except:
            print >> sys.stderr, "Unknown manage tool"
            return 3
        
        switched = False
        try:
            latest_dir = os.path.join(project_dir, 'src')
            tag_dir = os.path.join(project_dir, 'tags', tag)
            if not os.path.exists(tag_dir):
                print >> sys.stderr, "Tag %s has not been installed. Use checkout or register first!" % tag
                return 1
            
            subprojects_file = os.path.join(tag_dir, '.subprojects')
            if not os.path.exists(subprojects_file):
                subprojects = ['./']
            else:
                f = file(subprojects_file)
                subprojects = f.readlines()
                f.close()    
            
            if os.path.exists(latest_dir):
                lasttag = os.readlink(latest_dir).split(os.sep)[-1:][0]
                self.uninstall(project_name, lasttag, subprojects, latest_dir, general, verbose)
            
            print "Switching version to tag: %s" % tag
            
            if os.path.exists(latest_dir):
                self.run('rm -Rf %s/src' % project_dir, verbose)
            self.run('ln -s %s %s/src' % (tag_dir, project_dir), verbose)
            switched = True
            
            self.install(project_name, tag, subprojects, tag_dir, general, verbose)
        
            print 'Done. Successfully switched to tag: %s for "%s"' % (tag, project_name)
            print 'Completed in %.2f sec.' % (time.time() - start_time)
            return 0
        except Exception, e:
            if switched:
                try:
                    self.switch_back(project_name, subprojects, general, project_dir, latest_dir, verbose)
                except BaseException, be:
                    print >> sys.stderr, 'Failed to switch back to tag: %s for "%s": %s' % (os.path.basename(latest_dir), project_name, repr(be))
            print >> sys.stderr, 'There was errors. Failed to switch to tag: %s for "%s": %s' % (tag, project_name, repr(e))
            return (binascii.crc32(repr(e)) % 255) + 1
        
    def switch_back(self, project_name, subprojects, general, project_dir, latest_dir, verbose = False):
        self.run('rm -Rf %s/src' % project_dir, verbose)
        if os.path.exists(latest_dir):
            self.run('ln -s %s %s/src' % (latest_dir, project_dir), verbose)
            tag = os.path.basename(latest_dir)
            self.install(project_name, tag, subprojects, latest_dir, general, verbose)
    
    def version(self, project_name):
        """
        Lists versions of project
        
        @type project_name: string
        @param project_name: project to list
        @rtype: number
        """
        try:
            project_dir = get_project_dir(project_name)
            real = os.path.realpath(os.path.join(project_dir, 'src'))
            tag = os.path.basename(real)
        except:
            tag = None
            project_dir = 'Not available'
        deployer = create(project_name)
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
                    v_author = deployer.output('ls -ld %s/%s | cut -d \' \' -f 3' % (tags_dir, version))
                    v_date = deployer.output('ls -ld %s/%s | cut -d \' \' -f 6' % (tags_dir, version))
                    v_time = deployer.output('ls -ld %s/%s | cut -d \' \' -f 7' % (tags_dir, version))
                    
                    if version == tag:
                        line = ' * '
                    else:
                        line = '   '
                    line += "%s    %s   %s %s" % (version, v_author, v_date, v_time)
                    print line
            except:
                print '>> None <<'
            print ''       
            if tag == 'src':
                tag = None 
            print "Actual version: %s" % tag        
        print ''
        return 0
    
    def purge(self, project_name, yes = False, verbose = False):
        """
        Purge project and all its versions
        
        @type project_name: string
        @param project_name: project to list
        @type yes: bool
        @param yes: Confirms all safety questions
        @type verbose: bool
        @param verbose: is verbose
        @rtype: None
        """
        try:
            projects = get_projects()
            project_dir = get_project_dir(project_name)
            general = get_ini(project_name)
        except:
            print >> sys.stderr, 'Project is not being managed! Mispelled?'
            return 2
        
        print 'Project: %s (%s)' % (project_name, project_dir)
        if not yes:
            while(True):
                ans = raw_input('Do you relly want to delete whole project with all common data? [yes, NO]: ')
                if ans.lower() not in 'yes,no,'.split(','):
                    pass
                else:
                    break
            if ans.lower() == 'no' or ans == '':
                return 5
        
        del projects[project_name]
        
        try:
            projects_filename = os.path.join(config.dirs.root, 'projects.dat')
            projects_file = file(projects_filename, 'w')
            projects_file.write(json.dumps(projects))
        finally:
            projects_file.close()

        tag_dir = os.readlink(os.path.join(project_dir, 'src'))
        subprojects_file = os.path.join(tag_dir, '.subprojects')
        if not os.path.exists(subprojects_file):
            subprojects = ['./']
        else:
            f = file(subprojects_file)
            subprojects = f.readlines()
            f.close()
        
        tag = os.path.basename(tag_dir)
        self.uninstall(project_name, tag, subprojects, tag_dir, general, verbose)
        return self.run('rm -Rf %s' % project_dir, verbose)
    
    @staticmethod
    def list():
        """
        Lists projects and theirs version
        
        @rtype: None
        """
        projects = get_projects()
        deployer = FileSystemDeployer.FileSystemDeployer()
            
        print 'Managed projects:'
        no = True
        for project_name, project_dir in projects.items():
            
            try:
                real = os.path.realpath(os.path.join(project_dir, 'src'))
                if os.path.exists(real):
                    tag = os.path.basename(real)
                    v_author = deployer.output('ls -ld %s | cut -d " " -f 3' % real)
                    v_date = deployer.output('ls -ld %s | cut -d " " -f 6' % real)
                    v_time = deployer.output('ls -ld %s | cut -d " " -f 7' % real)
                else:
                    tag = '-'
                    v_author = '-'
                    v_date = '-'
                    v_time = '-'
                no = False
            except:
                continue
                
            print " - %s %s %s %s %s %s" % (project_name.ljust(15), tag.ljust(8), v_author.ljust(15), v_date.ljust(10), v_time.ljust(5), project_dir)
        if no:
            print 'There is no managed project. Initiate one using: %s init [dir]' % config.program.name
        print ''
    
    def delete(self, project_name, tag, verbose = False):
        """
        Deletes project  version and runs appopriate uninstall jobs
        
        @type project_name: string
        @param project_name: a project name to work on
        @type tag: string
        @param tag: version to switch to
        @type verbose: bool
        @param verbose: is verbose
        """
        try:
            project_dir = get_project_dir(project_name)
            real = os.path.realpath(os.path.join(project_dir, 'src'))
            actual_tag = os.path.basename(real)
            tags_dir = os.path.join(project_dir, 'tags')
        except:
            print >> sys.stderr, 'Project is not being setuped! Use `%s init [dir]` first' % config.program.name
            return 2
        
        if tag == actual_tag:
            print >> sys.stderr, 'Cant delete tag that is activly being used!'
            return 3
        
        target = os.path.join(tags_dir, tag)
        if os.path.exists(target) == False:
            print 'Tag %s does not exists for project: %s' % (tag, project_name)              
            return 4
        self.run('rm -Rf %s' % target, verbose)
        print 'Tag: %s deleted for project: %s' % (tag, project_name)
    
    def after_fetch(self, tag_dir, project_name, verbose = False):
        if not os.path.isdir(tag_dir):
            return
        os.chdir(tag_dir)
        general = get_ini(project_name)
        tool = general['tool']
        project_dir = get_project_dir(project_name)
        common_paths_file = os.path.join(tag_dir, 'config', 'sharedfiles.conf')
        if not os.path.exists(common_paths_file):
            common_paths_file = os.path.join(tag_dir, '.sharedfiles')
        if os.path.exists(common_paths_file):
            print 'Deleting shared directories and linking...'
            
            f = file(common_paths_file)
            common_paths = f.readlines()
            f.close()
            for pathd in common_paths:
                pathd = pathd.strip()
                if pathd == '':
                    continue
                target = '%s/data/%s' % (project_dir, pathd)
                tag_path = '%s/%s' % (tag_dir, pathd)
                if not os.path.exists(target):
                    if os.path.isfile(tag_path):
                        self.run('mkdir -p %s' % os.path.dirname(target), verbose)
                        self.run('cp %s %s' % (tag_path, target), verbose)
                    else:
                        self.run('mkdir -p %s' % target, verbose)
                self.run('rm -Rf %s' % tag_path, verbose)
                if os.path.isfile(target):
                    self.run('ln %s %s' % (target, tag_path), verbose)
                else:
                    self.run('ln -s %s %s' % (target, tag_path), verbose)
        
        subprojects_file = os.path.join(tag_dir, '.subprojects')
        if not os.path.exists(subprojects_file):
            subprojects = ['./']
        else:
            f = file(subprojects_file)
            subprojects = f.readlines()
            f.close()
            
        scmpath = general.get('scmpath', '')
        for project_path in subprojects:
            project_path = os.path.join(scmpath, project_path).strip()
            subproject_dir = os.path.join(tag_dir, project_path)
            os.chdir(subproject_dir)
            try:
                target = general['target_setup']
            except:
                target = False
            if tool != 'none' and target:
                print 'Setting up application: %s' % os.path.relpath(project_path)
                if tool == 'maven':
                    self.run('mvn %s' % self.modify_build_target(tool, target), verbose)
                    
                if tool == 'phing':
                    self.run('phing %s -logger phing.listener.DefaultLogger' % self.modify_build_target(tool, target), verbose)
                
                if tool == 'ant':
                    self.run('ant %s' % self.modify_build_target(tool, target), verbose)
                    
    def modify_build_target(self, tool, target):
        return target
    
    def modify_install_target(self, tool, target):
        return target
    
    def modify_uninstall_target(self, tool, target):
        return target
    
    @staticmethod
    def init(general):
        pass
    
    @staticmethod
    def supportsSharedfiles():
        """
        @rtype: bool
        """
        return False
    
    @staticmethod
    def getDescription():
        """
        Gets description on this deployer
        
        @rtype: string
        @return: Description on this deployer
        """
        return ''
    
import FileSystemDeployer
import JavaGlassfish
types = {
    1: FileSystemDeployer.FileSystemDeployer,
    2: JavaGlassfish.JavaGlassfishWar
}

def create(project_name):
    """
    
    @type dtype: string
    @return: initiated AbstractDeployer
    @rtype: deployers.AbstractDeployer
    """
    general = get_ini(project_name)
    dtype = int(general['type'])
    cls = types[dtype]
    return cls()

def get_ini(project_name):
    project_dir = get_project_dir(project_name)
    filename = os.path.join(project_dir, 'project.ini')
    ini = ConfigObj(filename)
    return ini['general']

def get_project_dir(project_name):
    projects = get_projects()
    project_dir = projects[project_name]
    return project_dir
    
def get_projects():
    projects_filename = os.path.join(config.dirs.root, 'projects.dat')
    try:
        projects_file = file(projects_filename)
        projects = json.loads(projects_file.read())
        projects_file.close()
    except:
        projects = {}
    return projects