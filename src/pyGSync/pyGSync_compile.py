# Copyright (c) 2008 Roi Dayan
# This file is part of the pyGSync project.
# http://pygsync.googlecode.com

import py_compile
import os
import time
import shutil
import sys

print sys.version

root=os.getcwd()
print root

py_compile.compile(root+"\pyGSync.py")
shutil.copy(root+"\pyGSync.pyc","compiled")
os.remove(root+"\pyGSync.pyc")

lib_files=os.listdir(root+"\lib")
print lib_files

for i in lib_files:
    fi='%s\lib\%s' %(root,i)
    i2=os.path.splitext(fi)
    if (i2[1]=='.py'):
        i2=i2[0]+'.pyc'
        print 'Compiling %s' %i
        py_compile.compile(fi)
        shutil.copy(i2,root+"\compiled\lib")
        os.remove(i2)
print "done."
print "enter any key."
sys.stdin.read(1)
