'''
Created on 7/05/2014

@author: burkej
'''

import Tkinter
import logging
import pyodbc
from functools import partial
import webbrowser

#import stsrc.models.tab as tab

log = logging.getLogger(__package__)

class CPN_Delivery_Schedule(Tkinter.Frame):
    def __init__(self, root, *args, **kwargs):
        
        Tkinter.Frame.__init__(self, root, *args, **kwargs)
        self.root = root
        
        Tkinter.Label(self, text="Delivery No", bg="grey").grid(row=1, column=0, padx=1, pady=1, sticky="nsew")
        Tkinter.Label(self, text="Delivery Date", bg="grey").grid(row=1, column=1, padx=1, pady=1, sticky="nsew")
        Tkinter.Label(self, text="Training Date", bg="grey").grid(row=1, column=2, padx=1, pady=1, sticky="nsew")
        Tkinter.Label(self, text="Live Date", bg="grey").grid(row=1, column=3, padx=1, pady=1, sticky="nsew")
        Tkinter.Label(self, text="Extracted Date", bg="grey").grid(row=1, column=4, padx=1, pady=1, sticky="nsew")
        Tkinter.Label(self, text="Training Date", bg="grey").grid(row=1, column=5, padx=1, pady=1, sticky="nsew")
        Tkinter.Label(self, text="Live Date", bg="grey").grid(row=1, column=6, padx=1, pady=1, sticky="nsew")
        Tkinter.Label(self, text="", bg="grey").grid(row=1, column=7, padx=1, pady=1, sticky="nsew")
        
        delivery_schedule = None
        with pyodbc.connect(self.root.con_string) as cnxn:
            cursor = cnxn.cursor()
            cursor.execute("""Select DeliveryNumber as DeliveryNumber, 
                                DeliveryDate as DeliveryDate, 
                                TrainingDate as TrainingDate, 
                                LiveDate as LiveDate, 
                                CONVERT(VARCHAR(10), ExtractDateTime, 120) as ExtractDateTime, 
                                CONVERT(VARCHAR(10), TrainingLoadDateTime, 120) as TrainingLoadDateTime, 
                                CONVERT(VARCHAR(10), LiveLoadDateTime, 120) as LiveLoadDateTime 
                                From coredata.IcadCPNDeliverySchedule 
                                order by DeliveryNumber desc""")
            delivery_schedule = cursor.fetchall()
            
        i = 2
        for row in delivery_schedule:
            j = 0
            for col in row:
                Tkinter.Label(self, text=col).grid(row=i, column=j, padx=1, pady=1, sticky='w')
                j += 1
            if not row.ExtractDateTime:
                action_with_arg = partial(self.cpn_delivery, row.DeliveryNumber)
                test = Tkinter.Button(self, text="Deliver", command=action_with_arg)
                test.grid(row=i, column=j)
            elif not row.TrainingLoadDateTime:
                action_with_arg = partial(self.update_training, row.DeliveryNumber)
                test = Tkinter.Button(self, text="Update Training", command=action_with_arg)
                test.grid(row=i, column=j)
            elif not row.LiveLoadDateTime:
                action_with_arg = partial(self.update_live, row.DeliveryNumber)
                test = Tkinter.Button(self, text="Update Live", command=action_with_arg)
                test.grid(row=i, column=j)
            else:
                pass
            
            i += 1
    
    
    def cpn_delivery(self, delivery_number):
        print delivery_number
        top = Tkinter.Toplevel(self)
        
        Tkinter.Label(top, text="This process is not currently automated.").grid(row=0, column=0, padx=10, pady=5, columnspan=2, sticky="w")
        
        Tkinter.Label(top, text="Documentation is located").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        def open_callback(event):
                webbrowser.open_new(r"http://fireportal/site/ICTS-DSA/DSA%20Process/Process%20Documentation/SMART%20Map%20Data%20Extracts/CPN%20Delivery%20Process.doc")
            
        lbl_open_xls = Tkinter.Label(top, text="here", fg="Blue", cursor="hand2")
        lbl_open_xls.grid(row=1, column=1, sticky="w")
        lbl_open_xls.bind("<Button-1>", open_callback)
        
        Tkinter.Label(top, text="Proceed to Step 3: Run the extract package").grid(row=2, column=0, padx=10, pady=5, columnspan=2, sticky="w")
    
    def update_training(self, delivery_number):
        print delivery_number
        with pyodbc.connect(self.root.con_string) as cnxn:
            cursor = cnxn.cursor()
            cursor.execute("EXEC coredata.spICADCPNTraining '%s'" % delivery_number)
    
    def update_live(self, delivery_number):
        print delivery_number
        with pyodbc.connect(self.root.con_string) as cnxn:
            cursor = cnxn.cursor()
            cursor.execute("EXEC coredata.spICADCPNLive '%s'" % delivery_number)
if __name__ == '__main__':
    pass