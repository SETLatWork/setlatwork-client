# -*- coding: utf-8 -*-#

import main
import os
import sys
import datetime
import logging

format = '%(asctime)s::%(name)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s'
datefmt = '%Y%m%d %H:%M:%S'

if '__file__' in globals():
    basedir = os.path.dirname(os.path.abspath(__file__))
    #logging.basicConfig(format=format, level=logging.NOTSET, datefmt=datefmt)
elif hasattr(sys, 'frozen'):
    basedir = os.path.dirname(os.path.abspath(sys.executable))  # for py2exe
    #logging.basicConfig(format=format, level=logging.NOTSET, filename=r'logs\%s.log' % datetime.datetime.now().strftime("%Y%m%d"), datefmt=datefmt)
else:  # should never happen
    basedir = os.getcwd()

if not os.path.exists(os.path.join(basedir, 'logs')):
    os.mkdir(os.path.join(basedir, 'logs'))

logging.basicConfig(format=format, level=logging.NOTSET, filename=r'{0}/logs/{1}.log'.format(basedir, datetime.datetime.now().strftime("%Y%m%d")), datefmt=datefmt)
os.chdir(basedir)
sys.path = [basedir] + [p for p in sys.path if not p == basedir]

log = logging.getLogger(__package__)

log.info(" Application Launched")
log.info("--------------------------------------------------------------------")

#----------------------------------------------------------------------
if __name__ == "__main__":
    import wx

    try:
        from multiprocessing import freeze_support
        freeze_support()
    except:
        log.error('Freeze Support Error')

    app = wx.App()
    #main.Login(None, 'SETL@Work', basedir)
    main.MainFrame(basedir)
    #main.TaskBarIcon(basedir, None)
    app.MainLoop()
    sys.exit()