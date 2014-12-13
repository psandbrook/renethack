import sys
import os
import time

def get_maindir():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def get_millitime():
    return time.time() * 1000.0
