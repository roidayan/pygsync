# Copyright (c) 2008 Roi Dayan
# This file is part of the pyGNotify project.
# pyGSync project: http://pygsync.googlecode.com

import appuifw,e32
import sys, os

pyGNotify_dir=os.getcwd()
pyGNotify_libdir = '%s\lib' %pyGNotify_dir
sys.path.append(pyGNotify_libdir)

applock=None
txtLog=None
from interface import *

def main():
    applock = init_interface()
    try:
        create_interface()
        post_load()
        applock.wait()
    except:
        harness(applock)

if __name__=='__main__':
    main()
