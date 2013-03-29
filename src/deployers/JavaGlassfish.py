'''
Created on 28-03-2013

@author: ksuszyns
'''
from deployers.FileSystemDeployer import FileSystemDeployer
import os
import re
from commands import init
from util import SystemException
from subprocess import CalledProcessError
import sys

class JavaGlassfishWar(FileSystemDeployer):
    '''
    classdocs
    '''
    
    __paths = os.environ['PATH']

    def __init__(self):
        '''
        Constructor
        '''
        super(JavaGlassfishWar, self).__init__()
        self.__glbin = None
                    
    def __get_search_paths(self):
        paths = JavaGlassfishWar.__paths.split(os.pathsep)
        glassfish_paths = [
            'glassfish',
            'glassfish-3.1.2.2',
            'glassfish-3.1.2',
            'glassfish-3.1',
            'glassfish-3',
            'glassfish3',
        ]
        search_paths = [
            os.path.join('/','opt'),
            os.path.join('/','usr', 'lib'),
            os.path.join('/','usr', 'share'),
            os.path.join('/','usr', 'local', 'lib'),
            os.path.join('/','usr', 'local', 'share'),
        ]
        out_paths = []
        for p in paths:
            out_paths.append(p.strip('"'))
        for sp in search_paths:
            for gp in glassfish_paths:
                path = os.path.join(sp, gp, 'bin')
                if os.path.exists(path) and os.path.isdir(path):
                    out_paths.append(path)
        return out_paths
        
    def __which(self, program):
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    
        fpath = os.path.split(program)[0]
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in self.__get_search_paths():
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file
    
        return None
        
    def find_glassfish_admin(self):
        if self.__glbin != None:
            return self.__glbin
        
        asadmin = 'asadmin'
        try:
            glhome = os.environ['GLASSFISH_HOME']
            glbin = os.path.join(glhome, 'bin', asadmin)
            if os.path.isfile(glbin) and os.access(glbin, os.X_OK):
                print 'Using "%s" as Glassfish home' % glhome
                self.__glbin = glbin
                return glbin
            raise Exception
        except:
            glbin = self.__which(asadmin)
            self.__glbin = glbin
            glhome = self.find_glassfish_home()
            print 'Using "%s" as Glassfish home' % glhome
            return glbin
        
    def find_glassfish_home(self):
        glbin = self.find_glassfish_admin()
        binasadmin = os.path.join('bin', 'asadmin')
        glhome = glbin.split(binasadmin)[0].rstrip(os.sep)
        return glhome

    def find_war(self, path):
        cmd = 'find %s -name *.war' % path
        wars = self.output(cmd).split("\n")
        if len(wars) < 1:
            raise SystemException("Can't find .war artifact in search path: \"%s\"" % path)
        return wars.pop().strip()
    
    def get_name(self, project_name, subproject, tag):
        subname = '%s-%s' % (project_name, subproject)
        subname = re.sub('-{2,}', '-', re.sub('[^a-z0-9]', '-', subname)).strip('-')
        return '%s:%s' % (subname, tag)

    def is_server_running(self):
        glbin = self.find_glassfish_admin()
        command = [ glbin ]
        command.append('list-domains')
        command.append('|')
        command.append('grep')
        command.append('-q')
        command.append("running")
        ret = self.run(' '.join(command), throw=False)
        return ret == 0
    
    def start_server(self):
        glbin = self.find_glassfish_admin()
        command = [ glbin ]
        command.append('start-domain')
        self.run(' '.join(command))
    
    def ensure_server_running(self):
        if not self.is_server_running():
            self.start_server()
    
    def is_deployed(self, name):
        glbin = self.find_glassfish_admin()
        command = [ glbin ]
        command.append('list-applications')
        command.append('|')
        command.append('grep')
        command.append('-q')
        command.append("'%s'" % name)
        ret = self.run(' '.join(command), throw=False)
        return ret == 0
    
    def get_last_log(self, lines):
        glhome = self.find_glassfish_home()
        log_dir = os.path.join(glhome, 'glassfish', 'domains', 'domain1', 'logs')
        log_file = os.path.join(log_dir, 'server.log')
        return self.output('tail -n %d %s' % (lines, log_file), throw = False)

    def install(self, project_name, tag, subprojects, targetpath, general, verbose=False):
        super(JavaGlassfishWar, self).install(project_name, tag, subprojects, targetpath, general, verbose)
        self.ensure_server_running()
        glbin = self.find_glassfish_admin()
        
        for sub in subprojects:
            scmpath = general.get('scmpath', '')
            war_search = os.path.join(targetpath, scmpath, sub).replace('/./', '/')
            war = self.find_war(war_search)
            context = general.get('context', '/')
            name = self.get_name(project_name, sub, tag)
            if self.is_deployed(name):
                self.uninstall(project_name, tag, subprojects, targetpath, general, verbose)
            
            command = [ glbin ]
            command.append('deploy')
            command.append('--contextroot')
            command.append(context)
            command.append('--name')
            command.append(name)
            command.append(war)
            
            print 'Deploying "%s" (%s) app into "%s" context' % (name, war, context)
            try:
                self.run(' '.join(command), verbose, throw=True)
            except CalledProcessError, e:
                log = self.get_last_log(50)
                print >> sys.stderr, log
                print >> sys.stderr, repr(e)
    
    def uninstall(self, project_name, tag, subprojects, targetpath, general, verbose=False):
        super(JavaGlassfishWar, self).uninstall(project_name, tag, subprojects, targetpath, general, verbose)
        self.ensure_server_running()
        glbin = self.find_glassfish_admin()
        
        for sub in subprojects:
            name = self.get_name(project_name, sub, tag)
            command = [ glbin ]
            command.append('undeploy')
            command.append(name)
            
            print 'Undeploying "%s" app' % (name)
            try:
                self.run(' '.join(command), verbose)
            except CalledProcessError, e:
                log = self.get_last_log(50)
                print >> sys.stderr, log
                print >> sys.stderr, repr(e)
            
    def __attr_glhome(self, tool, target):        
        if tool == 'ant':
            glbin = self.find_glassfish_admin()
            binasadmin = os.path.join('bin', 'asadmin')
            glhome = glbin.split(binasadmin)[0].rstrip(os.sep)
            glhome = os.path.join(glhome, 'glassfish')
            return '-Dj2ee.server.home=%s %s' % (glhome, target)
        return target
    
    def modify_build_target(self, tool, target):
        return self.__attr_glhome(tool, target)
    
    def modify_install_target(self, tool, target):
        return self.__attr_glhome(tool, target)
    
    def modify_uninstall_target(self, tool, target):
        return self.__attr_glhome(tool, target)
    
    @staticmethod
    def init(general):
        context = init.inputdef('Enter app context', general, 'context', '/')
        general['context'] = context

    @staticmethod
    def getDescription():
        return "Glassfish Java EE 6 WAR artifact project"
    
    @staticmethod
    def supportsSharedfiles():
        """
        @rtype: bool
        """
        return False