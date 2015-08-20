# -*- coding: utf-8 -*-#

from setuptools import setup
import py2exe
from glob import glob
import sys, shutil, os, zipfile
import datetime

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Copy required C++ bindings over
sys.path.append(r'C:\Windows\winsxs\x86_microsoft.vc90.crt_1fc8b3b9a1e18e3b_9.0.30729.4148_none_5090ab56bcba71c2')
data_files = [("Microsoft.VC90.CRT", glob(r'C:\Windows\winsxs\x86_microsoft.vc90.crt_1fc8b3b9a1e18e3b_9.0.30729.4148_none_5090ab56bcba71c2\*.*'))]

# This setup is suitable for "python setup.py develop".
setup(
        windows=[{'script':'setlatwork.py',
                    'icon_resources': [(1, 'icon.ico')]
                    }],
        description="SETL@Work",
        author="J P Burke",
        license="GPL v3",
        data_files=data_files,
        zipfile = None,
        options = {
            'py2exe': {
                'bundle_files': 1,
                'compressed':True,
                'includes': 'decimal',
                'excludes':['fmeobjects'],
                'optimize': 0
            }
        }
)