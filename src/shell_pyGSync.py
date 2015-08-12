# Copyright (c) 2008 Roi Dayan
# This file is part of the pyGSync project.
# http://pygsync.googlecode.com

import e32
import sys, os

python_dir = '\Python'
pyGSync_dir = '%s\pyGSync' %python_dir

if e32.in_emulator():
    pys60rcPath = 'C:%s' %pyGSync_dir
else:
    pys60rcPath = 'E:%s' %pyGSync_dir

os.chdir(pys60rcPath)
sys.path.append(pys60rcPath)

import pyGSync
pyGSync.main()
