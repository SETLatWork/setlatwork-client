# -*- coding: utf-8 -*-#
import logging
import wx
import ConfigParser
import os
import sys
import getpass

log = logging.getLogger(__name__)

import taskbaricon
 
########################################################################
class MainFrame(wx.Frame):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self, basedir):
        self.user = dict()

        wx.Frame.__init__(self, None, title='SETL@Work', size=(250, 250), style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN)
        self.panel = wx.Panel(self)
        #self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.basedir = basedir

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.icon = wx.Icon("icon.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)

        # Email
        text_email = wx.StaticText(self.panel, -1, 'Email:', (45, 1))
        self.email = wx.TextCtrl(self.panel, -1, size=(240,-1))
        sizer.Add(text_email, 0, wx.LEFT|wx.RIGHT|wx.TOP, 5)
        sizer.Add(self.email, 0, wx.LEFT|wx.RIGHT|wx.TOP, 5)

        # Password
        text_password = wx.StaticText(self.panel, -1, 'Password:', (45, -1))
        self.password = wx.TextCtrl(self.panel, -1, style=wx.TE_PASSWORD, size=(240,-1))
        sizer.Add(text_password, 0, wx.LEFT|wx.RIGHT|wx.TOP, 5)
        sizer.Add(self.password, 0, wx.LEFT|wx.RIGHT|wx.TOP, 5)

        # FME Location
        def get_fme_loc(e):
            if sys.platform == "darwin":
                openFileDialog = wx.FileDialog(self, "Find FME file", "/Library/FME", "fme", "", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            elif sys.platform == 'win32':
                openFileDialog = wx.FileDialog(self, "Find FME file", "C:/", "fme.exe", "EXE files (*.exe)|*.exe", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        text_fme = wx.StaticText(self.panel, -1, 'FME Location:', (45, -1))
        self.fme_location = wx.FilePickerCtrl(parent=self.panel, id=-1, path="", size=(240,-1), message="Find FME Executable") # , wildcard="EXE files (*.exe)|*.exe"
        self.Bind(wx.EVT_BUTTON, get_fme_loc, self.fme_location)
        sizer.Add(text_fme, 0, wx.LEFT|wx.RIGHT|wx.TOP, 5)
        sizer.Add(self.fme_location, 0, wx.LEFT|wx.RIGHT|wx.TOP, 5)

        # Save Password
        self.save_password = wx.CheckBox(self.panel, -1, 'Save Password', (10, 10))
        sizer.Add(self.save_password, 0, wx.ALL, 5)

        try:
            config = ConfigParser.ConfigParser()
            config.read(os.path.join(basedir, 'setup'))
            self.email.SetValue( config.get(getpass.getuser(), 'email'))
            if config.get(getpass.getuser(), 'password'):
                self.password.SetValue( config.get(getpass.getuser(), 'password').decode('base64'))
                self.save_password.SetValue(True)
            self.fme_location.SetPath( config.get(getpass.getuser(), 'fme location'))
        except:
            pass

        self.button_login = wx.Button(self.panel, -1, "Login")
        self.Bind(wx.EVT_BUTTON, self.login, self.button_login)
        sizer.Add(self.button_login, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        self.button_login.SetDefault()

        self.panel.SetSizer(sizer)

        #self.tbIcon = taskbaricon.CustomTaskBarIcon(self, basedir)
 
        self.Bind(wx.EVT_ICONIZE, self.onMinimize)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.Show()

    def login(self, e):
        # validate login details
        import requests
        import json

        try:
            if os.path.isfile(os.path.join(os.path.abspath('.'), 'cacert.pem')):
                cert_path = os.path.join(os.path.abspath('.'), 'cacert.pem')
            else:
                cert_path = False

            r = requests.get("https://www.setlatwork.com/manager/default/user/jwt", params=dict(username=self.email.GetValue(), password=self.password.GetValue()), verify=cert_path)
            log.info('GET:User - Status Code: %s' % r.status_code)
        except requests.ConnectionError as e:
            log.error(e, exc_info=True)
            wx.MessageBox('Unable to connect to the server at this time', 'Server Connection Error', wx.OK | wx.ICON_ERROR)
            exit(1)
            return

        if r.status_code != 200:
            wx.MessageBox('Unable to connect using the supplied login details', 'Invalid Login', wx.OK | wx.ICON_ERROR)
            log.error(r.text)
            return

        # check fme location
        if not os.path.isfile(self.fme_location.GetPath()):
            wx.MessageBox('Could not location FME.exe from the specified location', 'Invalid FME Location', wx.OK | wx.ICON_ERROR)
            return

        # save config
        config = ConfigParser.ConfigParser()
        config.add_section(getpass.getuser())
        config.set(getpass.getuser(), 'email', self.email.GetValue())

        if self.save_password.GetValue():
            config.set(getpass.getuser(), 'password', self.password.GetValue().encode('base64'))

        config.set(getpass.getuser(), 'fme location', self.fme_location.GetPath())
        config.write(open(os.path.join(self.basedir, 'setup'), 'w'))

        user = dict(token={"Authorization":"Bearer %s" % json.loads(r.text)['token']}, fme=self.fme_location.GetPath())

        self.tbIcon = taskbaricon.CustomTaskBarIcon(self, self.basedir, user)
        self.Hide()
 
    #----------------------------------------------------------------------
    def onClose(self, evt):
        """
        Destroy the taskbar icon and the frame
        """
        #self.tbIcon.RemoveIcon()
        #self.tbIcon.Destroy()
        #self.Hide()
        self.Destroy()
 
    #----------------------------------------------------------------------
    def onMinimize(self, event):
        """
        When minimizing, hide the frame so it "minimizes to tray"
        """
        self.Hide()




if __name__ == "__main__":
    app = wx.App(False)
    MainFrame(None)
    app.MainLoop()
    sys.exit(0)

# ------- END OF FILE