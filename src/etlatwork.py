# -*- coding: utf-8 -*-#

# References
# -----------------------------
# - Tkinter class :: http://sebsauvage.net/python/gui/
# - MVC Influence :: https://bitbucket.org/driscollis/medialocker
# - Tabs :: http://code.activestate.com/recipes/577261-python-tkinter-tabs/
# -----------------------------

import logging
import Tkinter, ttk, tkMessageBox
import modules.mc_listbox as mc_listbox
import modules.multilistbox as multilistbox
import modules.pybonjour as pybonjour
#import src.modules.system_tray as system_tray
import ConfigParser
import os
import server

log = logging.getLogger(__package__)

class etlatwork(Tkinter.Tk):
    def __init__(self, basedir):

        log.debug('start init')
        Tkinter.Tk.__init__(self)

        self.title('ETL@Work')
        self.name = "Home"
        self.minsize(506, 270)
        self.geometry("506x270")
        self.maxsize(506, 270)

        self.notebook_tabs = dict()
        self.basedir = basedir

        self.job_list = []

        self.load()

    def load(self):

        # Start/Stop Server

        self.frame_buttons = Tkinter.Frame(self)
        self.frame_buttons.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        def toggle_server():
            if self.label_status['text'] == 'Server Running':
                # Stop server
                self.server.stop()
                del self.server
                self.label_status['text'] = 'Server Stopped'
                self.button_start['text'] = 'Start Server'
            else:
                # Start server
                try:
                    self.server = server.Stream_Server(root=self, basedir=self.basedir)
                    self.server.daemon = True
                    self.server.start()

                    self.label_status['text'] = 'Server Running'
                    self.button_start['text'] = 'Stop Server'
                except Exception as e:
                    tkMessageBox.showerror('Error', 'Unable to connect to ETL Manager.')
                    log.debug(e)

        # Toggle server
        self.button_start = Tkinter.Button(self.frame_buttons, text="Start Server", command=toggle_server)
        self.button_start.grid(row=0, column=0, padx=(0,10))

        self.label_status = Tkinter.Label(self.frame_buttons, text="Server Stopped")
        self.label_status.grid(row=0, column=1)

        # Notebook - tab manager
        notebook = ttk.Notebook(self)
        notebook.grid(row=1, column=0, sticky="nsew")

        # Jobs
        job_header = [('Job No', 5), ('Name', 40), ('Started', 15), ('User', 15)]
        self.jobs = Jobs(notebook, job_header)
        self.jobs.pack(fill='both')
        notebook.add(self.jobs, text='Jobs')

        # History
        hist_header = [('Job No', 5), ('Name', 25), ('Started', 15), ('Finished', 15), ('User', 15)]
        self.history = History(notebook, hist_header)
        self.history.pack()
        notebook.add(self.history, text='History')

        # Settings
        frame_settings = Settings(notebook, self.basedir)
        frame_settings.pack()
        notebook.add(frame_settings, text='Settings')

    def refresh_list(self):
        self.jobs.delete(0, 'end')
        for job in self.job_list:
            log.debug(job)
            self.jobs.insert('end', (job['id'], job['name'], job['started'], job['user']))

    def insert_job(self, index, job):
        self.job_list.append(job)
        self.refresh_list()

    def delete_job(self, id):
        for i, job in enumerate(self.job_list):
            if job['id'] == id:
                del self.job_list[i]
        self.refresh_list()

    def get_job(self, id):
        for i, job in enumerate(self.job_list):
            if job['id'] == id:
                return self.job_list[i]


class Jobs(multilistbox.MultiListbox):
    def __init__(self, parent, header):

        multilistbox.MultiListbox.__init__(self, parent, header)

class History(multilistbox.MultiListbox):
    def __init__(self, parent, header):

        multilistbox.MultiListbox.__init__(self, parent, header)

class Settings(Tkinter.Frame):

    def __init__(self, parent, basedir):

        Tkinter.Frame.__init__(self, parent)

        self.basedir = basedir

        # ETL Manager URL
        Tkinter.Label(self, text="Manager URL:").grid(row=0, column=0, padx='5', pady='5', sticky='w')
        self.entry_webserver = Tkinter.Entry(self)
        self.entry_webserver.grid(row=0, column=1, padx='5', pady='5')
        #self.webserver.insert('0', 'http://127.0.0.1:8000')

        # Port
        Tkinter.Label(self, text="Port:").grid(row=1, column=0, padx='5', pady='5', sticky='w')
        self.entry_port = Tkinter.Entry(self)
        self.entry_port.grid(row=1, column=1, padx='5', pady='5')

        # Max Jobs
        Tkinter.Label(self, text="Max Jobs:").grid(row=2, column=0, padx='5', pady='5', sticky='w')
        self.entry_maxjobs = Tkinter.Entry(self)
        self.entry_maxjobs.grid(row=2, column=1, padx='5', pady='5')

        # FME Location
        import tkFileDialog

        Tkinter.Label(self, text="FME Exe:").grid(row=3, column=0, padx='5', pady='5', sticky='w')
        def callback_find():
            options = dict()
            options['defaultextension'] = '.exe'
            options['initialdir'] = 'C:'
            #options['mustexist'] = True
            options['initialfile'] = 'fme.exe'
            options['filetypes'] = [('executable','.exe')]
            options['title'] = 'Locate FME Executable'
            self.fme_location = tkFileDialog.askopenfilename(**options) #Tkinter.Entry(frame_settings)
            self.entry_fme_location.delete('0', 'end')
            self.entry_fme_location.insert('0', self.fme_location)

        self.entry_fme_location = Tkinter.Entry(self, text="")
        self.entry_fme_location.grid(row=3, column=1, padx='5', pady='5')

        btn_search = Tkinter.Button(self, text='Find', command=callback_find)
        btn_search.grid(row=3, column=2, padx='5', pady='5')

        self.read_config()

        btn_save_config = Tkinter.Button(self, text='Save', command=self.write_config)
        btn_save_config.grid(row=4, column=0, padx='5', pady='5')

    def read_config(self):
        config = ConfigParser.ConfigParser()
        config.read(os.path.join(self.basedir, 'config.ini'))
        self.entry_webserver.insert('0', config.get('settings', 'manager url'))
        self.entry_port.insert('0', config.get('settings', 'port'))
        self.entry_maxjobs.insert('0', config.get('settings', 'max jobs'))
        self.entry_fme_location.insert('0', config.get('settings', 'fme directory'))

    def write_config(self):
        config = ConfigParser.ConfigParser()
        config.add_section('settings')
        log.debug(self.entry_webserver.get()[:-1])
        if self.entry_webserver.get()[-1] == '/':
            fix_webserver = self.entry_webserver.get()[:-1]
            self.entry_webserver.delete('0', 'end')
            self.entry_webserver.insert('0', fix_webserver)

        config.set('settings', 'manager url', self.entry_webserver.get())
        config.set('settings', 'port', self.entry_port.get())
        config.set('settings', 'max jobs', self.entry_maxjobs.get())
        config.set('settings', 'fme directory', self.entry_fme_location.get())
        config.write(open(os.path.join(self.basedir, 'config.ini'), 'w'))



# -------------------------------
if __name__ == "__main__":
    basedir = r'C:\Users\James\Documents\etlondemand\etlatwork'
    app = etlatwork(basedir)
    app.mainloop()