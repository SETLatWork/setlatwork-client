#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup


setup(app=['setlatwork.py'],
      #version=web2py_version,
      description="SETL@Work",
      author="J P Burke",
      license="GPL v3",
      data_files=[
      'LICENSE',
      'icon.ico',
      ],
      options={'py2app': {
                'argv_emulation': True,
                #'bundle_files': 1,
                'compressed':True,
                'includes': 'decimal',
                'iconfile': 'icon.ico',
                #'excludes':['fmeobjects'],
                'optimize': 0
               }},
      setup_requires=['py2app'])

