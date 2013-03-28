'''
Created on 27-03-2013

@author: ksuszyns
'''
from deployers import AbstractDeployer

class FileSystemDeployer(AbstractDeployer):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
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