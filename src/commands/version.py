'''
Created on 27-01-2012

@author: ksuszynski
'''
import subprocess
import sys
import argparse

description = 'Print project version'

parser = argparse.ArgumentParser(description=description, usage='%(prog)s version [options]')
parser.add_argument('-d', '--dir', 
    nargs=1, 
    required=True, 
    help="Relative directory of project in ex.: 000/livespace"
)

def run(args):
    pass


def __run(cmd, verbose):
    if verbose:
        print '>>> ' + cmd
    subprocess.check_call(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)

def help():
    parser.print_help()