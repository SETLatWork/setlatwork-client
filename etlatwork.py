# -*- coding: utf-8 -*-#

import src.etlatwork as etlatwork
import os, sys, datetime

basedir, f = os.path.split(__file__)

# Logging
import logging, logging.config
logConfigFile = os.path.join(basedir, 'logging.conf')
if os.path.exists(logConfigFile):
    logging.config.fileConfig(logConfigFile)
else:
    format = '%(asctime)s::%(name)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s'
    datefmt = '%Y%m%d %H:%M:%S'
    logging.basicConfig(format=format, level=logging.NOTSET, datefmt=datefmt) #  % datetime.date.today() , filename='etlatwork.log'

log = logging.getLogger(__package__)
log.info("Application Launched")
log.info("--------------------")

#----------------------------------------------------------------------
if __name__ == "__main__":
    app = etlatwork.etlatwork(basedir)
    app.mainloop()
    sys.exit()