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
    
    def install(self, subprojects, targetpath, general, verbose=False):
        for project_path in subprojects:
            project_path = project_path.strip()
            if project_path == '':
                continue
            subproject_dir = os.path.join(targetpath, project_path)
            os.chdir(subproject_dir)
            tool = general['tool']
            target = general['target_install']
            if tool != 'none' and target != 'None':
                
                print "Installing: %s" % project_path
                if tool == 'phing':
                    self._run('phing %s -logger phing.listener.DefaultLogger' % target, verbose)
                
                if tool == 'ant':
                    self._run('ant %s' % target, verbose)
                    
    def uninstall(self, subprojects, targetpath, general, verbose=False):
        for project_path in subprojects:
            project_path = project_path.strip()
            if project_path == '':
                continue
            subproject_dir = os.path.join(targetpath, project_path)
            os.chdir(subproject_dir)
            tool = general['tool']
            target = general['target_uninstall']
            if tool != 'none' and target != 'None':
                print "Uninstalling previous version: %s" % project_path
                if tool == 'phing':
                    self._run('phing %s -logger phing.listener.DefaultLogger' % target, verbose)
                
                if tool == 'ant':
                    self._run('ant %s' % target, verbose)
    
   
    @staticmethod
    def getDescription():
        return "File system (for ex.: HTML, PHP, Python and Ruby projects)"

    @staticmethod
    def supportsSharedfiles():
        """
        @rtype: bool
        """
        return True