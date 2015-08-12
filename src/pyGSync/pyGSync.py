# Copyright (c) 2008 Roi Dayan
# This file is part of the pyGSync project.
# http://pygsync.googlecode.com

import appuifw,e32
import sys, os

#appuifw.note(unicode(os.getcwd()))
#appuifw.note(unicode(appuifw.app.full_name()))

#if os.path.split(appuifw.app.full_name())[-1]!='Python.exe':
#    pyGSync_dir = os.getcwd()
#else:
#    python_dir = '/Python'
#    if e32.in_emulator():
#        pys60rcPath = 'C:%s' %pyGSync_dir
#    else:
#        pys60rcPath = 'E:%s' %pyGSync_dir
#        #pyGSync_dir = '%s/pyGSync' %python_dir

pyGSync_dir=os.getcwd()
pyGSync_libdir = '%s\lib' %pyGSync_dir
sys.path.append(pyGSync_libdir)

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
