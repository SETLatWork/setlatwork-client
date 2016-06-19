#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup
import requests.certs
import datetime

VERSION = "0.0.1"

with open('VERSION', 'w') as f:
  f.write('%s+%s' % (VERSION, datetime.datetime.now()))

setup(app=['setlatwork.py'],
      version=VERSION,
      description="SETL@Work Client",
      author="SETL@Work Limited",
      license="GPL v3",
      data_files=[
        'LICENSE',
        'VERSION',
        'icon.ico',
        requests.certs.where()],
      options={'py2app': {
                'argv_emulation': False,
                #'bundle_files': 1,
                'compressed':True,
                'includes': 'decimal',
                'iconfile': 'icon',
                #'excludes':['tlc'],
                'optimize': 0
               }},
      setup_requires=['py2app'])



