import logging
import wx
import os
import sys
import server
import requests
import socket

log = logging.getLogger(__name__)
 

class CustomTaskBarIcon(wx.TaskBarIcon):
    """"""
    TBMENU_RESTORE = wx.NewId()
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
        self.Bind(wx.EVT_MENU, self.OnTaskBarActivate, id=self.TBMENU_RESTORE)
        self.Bind(wx.EVT_MENU, self.OnTaskBarManager, id=self.TBMENU_MANAGER)
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_CLOSE)

        self.server = server.Server_Thread(basedir, user)
        self.server.daemon = True
        self.server.start()

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


    def create_menu_item(self, menu, label, func):
        item = wx.MenuItem(menu, -1, label)
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        menu.AppendItem(item)
        return item

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        self.server.stop()
        r = requests.post("%s/api/client_log" % self.user['manager'], params=dict(worker=socket.gethostname()), files={'file': open(os.path.join(self.basedir, 'logs/client.log'))}, headers=self.user['bearer'], verify=self.user['cert_path'])
        log.info('POST:Client_Log - Status Code: %s' % r)
        sys.exit(1)

    def OnTaskBarActivate(self, evt):
        if self.frame.IsIconized():
            self.frame.Iconize(False)
        if not self.frame.IsShown():
            self.frame.Show(True)
        self.frame.Raise()

    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(self.TBMENU_RESTORE, "SETL@Work")
        menu.Append(self.TBMENU_MANAGER, "Manager")
        menu.Append(self.TBMENU_CLOSE, "E&xit")
        wx.EVT_MENU(self, self.TBMENU_CLOSE, self.on_exit)
        return menu
