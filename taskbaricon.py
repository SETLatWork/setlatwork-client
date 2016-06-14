import logging
import wx
import os
import sys
import server
import requests
import socket
import threading

# from wx.lib.pubsub import setuparg1
# from wx.lib.pubsub import pub as Publisher

log = logging.getLogger(__name__)
 

class CustomTaskBarIcon(wx.TaskBarIcon):
    """"""
    TBMENU_RESTORE = wx.NewId()
    TBMENU_RUNNING = wx.NewId()
    TBMENU_CLOSE   = wx.NewId()
    TBMENU_MANAGER = wx.NewId()

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
        self.Bind(wx.EVT_MENU, self.OnTaskBarChange, id=self.TBMENU_RESTORE)
        self.Bind(wx.EVT_MENU, self.OnTaskBarManager, id=self.TBMENU_MANAGER)
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_CLOSE)

        # http://www.blog.pythonlibrary.org/2010/05/22/wxpython-and-threads/
        # Publisher.subscribe(self.UpdateMenu, "jobs_running")

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
        """"""
        pass

    def OnTaskBarManager(self, evt):
        import webbrowser
        webbrowser.open_new_tab(self.user['manager'])

    def OnTaskBarClose(self, evt):
        """
        Destroy the taskbar icon and frame from the taskbar icon itself
        """
        self.frame.Close()

    # def UpdateMenu(self, message):
    #     self.jobs = message.data # self.menu.SetLabel(self.TBMENU_RUNNING, 'Running: %s' % message)

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        self.server.stop()
        try:
            r = requests.post("%s/api/client_log" % self.user['manager'], params=dict(worker=socket.gethostname()), files={'file': open(os.path.join(self.basedir, 'logs/client.log'))}, headers=self.user['bearer'], verify=self.user['cert_path'])
            log.info('POST:Client_Log - Status Code: %s' % r)
        except requests.ConnectionError:
            pass
        sys.exit(0)

    def OnTaskBarActivate(self, evt):
        if self.frame.IsIconized():
            self.frame.Iconize(False)
        if not self.frame.IsShown():
            self.frame.Show(True)
        self.frame.Raise()

    def CreatePopupMenu(self):
        menu = wx.Menu()
        offset = 2 if self.server.running else 1
        menu.Append(self.TBMENU_RESTORE, "Deactivate" if self.server.running else "Activate")
        menu.Append(self.TBMENU_RUNNING, "Running: %s" % str(threading.activeCount() - offset))
        menu.Append(self.TBMENU_MANAGER, "Manager")
        menu.AppendSeparator()
        menu.Append(self.TBMENU_CLOSE, "E&xit")
        wx.EVT_MENU(self, self.TBMENU_CLOSE, self.on_exit)
        return menu
