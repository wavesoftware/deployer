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
        
    @staticmethod
    def getDescription():
        return "Glassfish Java EE 6 WAR artifact project"