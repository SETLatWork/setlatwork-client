import logging
import wx
import os
import sys
import server
import requests
import socket
import threading
import gzip

# from wx.lib.pubsub import setuparg1
# from wx.lib.pubsub import pub as Publisher

log = logging.getLogger(__name__)
 
TBMENU_RESTORE = wx.NewId()
TBMENU_RUNNING = wx.NewId()
TBMENU_CLOSE   = wx.NewId()
TBMENU_MANAGER = wx.NewId()

class CustomTaskBarIcon(wx.TaskBarIcon):
    """"""

    def __init__(self, frame, basedir, user):
        """Constructor"""
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        self.basedir = basedir
        self.user = user

        # Set Icon
        icon = wx.IconFromBitmap(wx.Bitmap(os.path.join(basedir, 'icon.ico')))
        self.SetIcon(icon, 'SETL@Work')

        # bind some events
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarActivate)
        self.Bind(wx.EVT_MENU, self.OnTaskBarChange, id=TBMENU_RESTORE)
        self.Bind(wx.EVT_MENU, self.OnTaskBarManager, id=TBMENU_MANAGER)
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=TBMENU_CLOSE)

        self.server = server.Server_Thread(basedir, user)
        self.server.daemon = True
        self.server.start()


    def OnTaskBarChange(self, evt):
        self.server.running = True if not self.server.running else False
        if self.server.running:
            self.server = server.Server_Thread(self.basedir, self.user)
            self.server.daemon = True
            self.server.start()
        else:
            self.server.stop()

    def OnTaskBarActivate(self, evt):
        pass

    def OnTaskBarManager(self, evt):
        import webbrowser
        webbrowser.open_new_tab(self.user['manager'])

    def OnTaskBarClose(self, evt):
        wx.CallAfter(self.Destroy)
        self.server.stop()
        try:
            with open(os.path.join(self.basedir, 'logs/client.log'), 'rb') as orig_file:
                with gzip.open(os.path.join(self.basedir, 'logs/client.log.gz'), 'wb') as zipped_file:
                    zipped_file.writelines(orig_file)
        except Exception as e:
            log.error(e)
        
        try:
            r = requests.post("%s/api/client_log" % self.user['manager'], params=dict(worker=socket.gethostname()), files={'file': open(os.path.join(self.basedir, 'logs/client.log.gz'))}, headers=self.user['bearer'], verify=self.user['cert_path'])
            log.info('POST:Client_Log - Status Code: %s' % r)
        except requests.ConnectionError:
            pass
        os.unlink(os.path.join(self.basedir, 'logs/client.log.gz'))
        self.frame.Close()

    def OnTaskBarActivate(self, evt):
        if self.frame.IsIconized():
            self.frame.Iconize(False)
        if not self.frame.IsShown():
            self.frame.Show(True)
        self.frame.Raise()

    def CreatePopupMenu(self):
        menu = wx.Menu()
        offset = 2 if self.server.running else 1
        menu.Append(TBMENU_RESTORE, "Deactivate" if self.server.running else "Activate")
        menu.Append(TBMENU_RUNNING, "Running: %s" % str(threading.activeCount() - offset))
        menu.Append(TBMENU_MANAGER, "Manager")
        menu.AppendSeparator()
        menu.Append(TBMENU_CLOSE, "E&xit")
        
        return menu
