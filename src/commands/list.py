'''
Created on 27-01-2012

@author: ksuszynski
'''
import deployers

description = 'Prints all installed projects'

def run(args):
    deployers.AbstractDeployer.list()

def phelp():
    print description