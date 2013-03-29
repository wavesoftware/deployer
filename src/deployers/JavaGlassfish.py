'''
Created on 28-03-2013

@author: ksuszyns
'''
from deployers import AbstractDeployer
from deployers.FileSystemDeployer import FileSystemDeployer
import os
import re
import glob
from commands import init
from util import SystemException

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
        asadmin = 'asadmin'
        try:
            glhome = os.environ['GLASSFISH_HOME']
            glbin = os.path.join(glhome, 'bin', asadmin)
            if os.path.isfile(glbin) and os.access(glbin, os.X_OK):
                print 'Using "%s" as Glassfish home' % glhome
                return glbin
            raise Exception
        except:
            glbin = self.__which(asadmin)
            binasadmin = os.path.join('bin', asadmin)
            glhome = glbin.split(binasadmin)[0].rstrip(os.sep)
            print 'Using "%s" as Glassfish home' % glhome
            return glbin

    def find_war(self, path):
        wars = glob.glob('%s**/*.war' % path)
        if len(wars) < 1:
            raise SystemException("Can't find .war artifact in search path: \"%s\"" % path)
        return os.path.relpath(wars.pop())
    
    def get_name(self, project_name, subproject, tag):
        subname = '%s-%s' % (project_name, subproject)
        subname = re.sub('-{2,}', '-', re.sub('[^a-z0-9]', '-', subname)).strip('-')
        return '%s:%s' % (subname, tag)

    def install(self, project_name, tag, subprojects, targetpath, general, verbose=False):
        super(JavaGlassfishWar, self).install(project_name, tag, subprojects, targetpath, general, verbose)
        glbin = self.find_glassfish_admin()
        
        for sub in subprojects:
            scmpath = general.get('scmpath', '')
            war_search = os.path.join(targetpath, scmpath, sub)
            war = self.find_war(war_search)
            name = self.get_name(project_name, sub, tag)
            command = [ glbin ]
            command.append('deploy')
            command.append('--contextroot')
            command.append(general['context'])
            command.append('--name')
            command.append(name)
            command.append(war)
            
            print 'Deploying "%s" (%s) app into "%s" context' % (name, war, general['context'])
            self.output(' '.join(command), verbose)
    
    def uninstall(self, project_name, tag, subprojects, targetpath, general, verbose=False):
        super(JavaGlassfishWar, self).uninstall(project_name, tag, subprojects, targetpath, general, verbose)
        glbin = self.find_glassfish_admin()
        
        for sub in subprojects:
            name = self.get_name(project_name, sub, tag)
            command = [ glbin ]
            command.append('undeploy')
            command.append(name)
            
            print 'Undeploying app from "%s" name' % (name)
            self.output(' '.join(command), verbose)
            
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