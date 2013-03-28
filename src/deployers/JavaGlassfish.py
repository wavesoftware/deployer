'''
Created on 28-03-2013

@author: ksuszyns
'''
from deployers import AbstractDeployer

class JavaGlassfishWar(AbstractDeployer):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super(JavaGlassfishWar, self).__init__()

    def install(self, subprojects, targetpath, general, verbose=False):
        raise NotImplementedError()
    
    def uninstall(self, subprojects, targetpath, general, verbose=False):
        raise NotImplementedError()
        
    @staticmethod
    def getDescription():
        return "Glassfish Java EE 6 WAR artifact project"
    
    @staticmethod
    def supportsSharedfiles():
        """
        @rtype: bool
        """
        return False