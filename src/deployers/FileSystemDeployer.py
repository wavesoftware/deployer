'''
Created on 27-03-2013

@author: ksuszyns
'''
from deployers import AbstractDeployer
import os

class FileSystemDeployer(AbstractDeployer):
    '''
    Generic file system deployer
    
    Deploys files and directories for standard web projects (HTML, PHP, Python and Ruby)
    
    Fires install and uninstall target of build file if it is set.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super(FileSystemDeployer, self).__init__()
    
    def install(self, project_name, tag, subprojects, targetpath, general, verbose=False):
        for project_path in subprojects:
            project_path = project_path.strip()
            if project_path == '':
                continue
            scmpath = general.get('scmpath', '')
            subproject_dir = os.path.join(targetpath, scmpath, project_path)
            if not os.path.isdir(subproject_dir):
                continue
            os.chdir(subproject_dir)
            tool = general.get('tool', None)
            target = general.get('target_install', None)
            if tool and tool != 'none' and target:
                
                print "Installing: %s" % project_path
                if tool == 'maven':
                    self.run('mvn %s' % self.modify_install_target(tool, target), verbose)
                    
                if tool == 'phing':
                    self.run('phing %s -logger phing.listener.DefaultLogger' % self.modify_install_target(tool, target), verbose)
                
                if tool == 'ant':
                    self.run('ant %s' % self.modify_install_target(tool, target), verbose)
                    
    def uninstall(self, project_name, tag, subprojects, targetpath, general, verbose=False):
        for project_path in subprojects:
            project_path = project_path.strip()
            if project_path == '':
                continue
            scmpath = general.get('scmpath', '')
            subproject_dir = os.path.join(targetpath, scmpath, project_path)
            if not os.path.isdir(subproject_dir):
                continue
            os.chdir(subproject_dir)
            tool = general.get('tool', None)
            target = general.get('target_uninstall', None)
            if tool and tool != 'none' and target:
                print "Uninstalling previous version: %s" % project_path
                if tool == 'maven':
                    self.run('mvn %s' % self.modify_uninstall_target(tool, target), verbose)
                    
                if tool == 'phing':
                    self.run('phing %s -logger phing.listener.DefaultLogger' % self.modify_uninstall_target(tool, target), verbose)
                
                if tool == 'ant':
                    self.run('ant %s' % self.modify_uninstall_target(tool, target), verbose)
    
    @staticmethod
    def init(general):
        pass
    
    @staticmethod
    def getDescription():
        return "File system (for ex.: HTML, PHP, Python and Ruby projects)"

    @staticmethod
    def supportsSharedfiles():
        """
        @rtype: bool
        """
        return True