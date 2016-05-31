#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup
import requests.certs

setup(app=['setlatwork.py'],
      #version=web2py_version,
      description="S ETL@Work",
      author="J P Burke",
      license="GPL v3",
      data_files=[
      'LICENSE',
      'icon.ico',
      requests.certs.where()
      ],
      options={'py2app': {
                'argv_emulation': False,
                #'bundle_files': 1,
                'compressed':True,
                'includes': 'decimal',
                'iconfile': 'icon',
                #'excludes':['fmeobjects'],
                'optimize': 0
               }},
      setup_requires=['py2app'])

