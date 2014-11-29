# -*- coding: utf-8 -*-#

# References
# -----------------------------
# - Tkinter class :: http://sebsauvage.net/python/gui/
# - MVC Structure :: https://bitbucket.org/driscollis/medialocker/src/4771c5a1f5b6?at=default
# -----------------------------

# baseapp for TerraCheck #

import sys
import os
basedir, f = os.path.split(__file__)


# Logging
import logging, logging.config
logConfigFile = os.path.join(basedir, 'logging.conf')
if os.path.exists(logConfigFile):
    logging.config.fileConfig(logConfigFile)
else:
    format = '%(name)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s'
    logging.basicConfig(format=format, level=logging.NOTSET)

log = logging.getLogger(__package__)
log.debug("logging is setup")

# UI Base Class
import Tkinter

class BaseApp(Tkinter.Tk):
    def __init__(self, parent):
        log.debug('start init')
        Tkinter.Tk.__init__(self, parent)
        self.parent = parent

        # set base folder
        self.baseDir, f = os.path.split(__file__)

        # Set data folder (location of json files)
        pPath, pFolder = os.path.split(self.baseDir)
        self.dataDir = os.path.join(pPath, 'data')

        log.debug('end init')