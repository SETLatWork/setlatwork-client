'''
Created on 6/05/2014

@author: burkej
'''

import Tkinter, ttk
import logging
import pyodbc
from functools import partial

import stsrc.models.tab as tab
import cpn_delivery_check, cpn_delivery_schedule, cpn_delivery_qa

log = logging.getLogger(__package__)

class CPN_Delivery(tab.Tab):
    def __init__(self, root, name, *args, **kwargs):
        
        tab.Tab.__init__(self, root, name)
        
        self.tabs = {}
        self.buttons = {}
        self.current_tab = None
        
        notebook = ttk.Notebook(self.interior)
        notebook.pack(fill='both', expand='yes')
        
        f1 = cpn_delivery_schedule.CPN_Delivery_Schedule(self.root)
        f2 = cpn_delivery_qa.CPN_Delivery_QA(self.root)
        f3 = cpn_delivery_check.CPN_Delivery_Check(self.root)
        
        notebook.add(f1, text='Delivery Schedule')
        notebook.add(f2, text='CPN QA')
        notebook.add(f3, text='Delivery Check')
        

if __name__ == '__main__':
    root = Tkinter.Tk()
    main = CPN_Delivery(root, 'CPN Delivery')
    main.pack(expand="true", fill="both")
    root.mainloop()