# -*- coding: utf-8 -*-#
# Copyright:   see copyright in the doc folder
# License:     see license in the doc folder
#-----------------------------------------------------------------------------
#!/usr/bin/env python

from setuptools import setup
import py2exe
from glob import glob
import sys, shutil

# Delete Source Folder and Copy over the latest source
try:
    shutil.rmtree(r'P:\ICTS\DSA\Smart Tools\Source')
    shutil.rmtree(r'P:\ICTS\DSA\Smart Tools\Smart Tools')
except:
    print"failed to delete folders"
    # folders don't exist
    pass

# Copy source code to P:
shutil.copytree(r'C:\Users\burkej\Documents\Projects\SMART Tools\Smart Tools', r'P:\ICTS\DSA\Smart Tools\Source')

# Copy required C++ bindings over
sys.path.append(r'C:\Program Files (x86)\ArcGIS\Desktop10.2\bin\Microsoft.VC90.CRT')
data_files = [("Microsoft.VC90.CRT", glob(r'C:\Program Files (x86)\ArcGIS\Desktop10.2\bin\Microsoft.VC90.CRT\*.*'))]

# Include images in the build
data_files.append(('images', glob(r"C:\Users\burkej\Documents\Projects\SMART Tools\Smart Tools\images/*.gif")))

# This setup is suitable for "python setup.py develop".
setup(
        windows=['Smart Tools.py'],
        data_files=data_files,
        options = {
            'py2exe': {
                'packages': ['stsrc'],
                'includes': 'decimal',
                'excludes': ['_ssl','pyreadline', 'difflib', 'doctest', 'locale', 'optparse', 'pickle', 'calendar'],
                'dll_excludes':['msvcr71.dll'],
                'optimize': 0,
                'compressed': True,
                'dist_dir': r'P:\ICTS\DSA\Smart Tools\Smart Tools'
            }
        }
)