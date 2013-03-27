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
   
    def getDescription(self):
        return "File system"
