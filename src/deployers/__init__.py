import abc


class AbstractDeployer:
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def switch(self, project, version):
        """
        Switches project to target version and runs appopriate uninstall/install jobs
        
        @type project: string
        @param project: a project name to work on
        @type version: string
        @param version: version to switch to
        """
        return
    
    def version(self, project):
        return
    
    def purge(self, project):
        pass
    
    def list(self):
        pass
    
    def delete(self, project, version):
        pass
    
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