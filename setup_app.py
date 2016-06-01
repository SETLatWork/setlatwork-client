#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup
import requests.certs

setup(app=['setlatwork.py'],
      version="0.0.1",
      description="SETL@Work",
      author="J P Burke",
      license="GPL v3",
      data_files=[
        'LICENSE',
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

