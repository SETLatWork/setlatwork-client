# -*- coding: utf-8 -*-#

# References
# -----------------
# - tkFileDialog :: http://tkinter.unpythonic.net/wiki/tkFileDialog
# - import all files :: http://stackoverflow.com/questions/1057431/loading-all-modules-in-a-folder-in-python
# -----------------

import Tkinter, tkFileDialog
import csv
import logging
import ttk
from collections import OrderedDict

import stsrc.models.tab as tab

log = logging.getLogger(__package__)

class CPN_Check(tab.Tab):

    def __init__(self, root, name, *args, **kwargs):
        
        tab.Tab.__init__(self, root, name)
        
        self.map_values = OrderedDict()
        
        bt_view = Tkinter.Button(self.interior, text="Load...", command=self.open)
        bt_view.grid(row=0, column=0, padx=1, pady=5)


    def load_grid(self):
        import pyodbc
        import webbrowser
        from functools import partial
        
        with open(self.filename, 'rb') as f:
            my_reader = csv.reader(f)
            headers = my_reader.next()
            
            Tkinter.Label(self.interior, text="ID", bg="grey").grid(row=1, column=0, padx=1, pady=1, sticky="nsew")
            Tkinter.Label(self.interior, text="CPN Name", bg="grey").grid(row=1, column=1, padx=1, pady=1, sticky="nsew")
            Tkinter.Label(self.interior, text="Address", bg="grey").grid(row=1, column=2, padx=1, pady=1, sticky="nsew")
            Tkinter.Label(self.interior, text="Notes", bg="grey").grid(row=1, column=3, padx=1, pady=1, sticky="nsew")
            Tkinter.Label(self.interior, text="X Coord", bg="grey").grid(row=1, column=4, padx=1, pady=1, sticky="nsew")
            Tkinter.Label(self.interior, text="Y Coord", bg="grey").grid(row=1, column=5, padx=1, pady=1, sticky="nsew")
            Tkinter.Label(self.interior, text="", bg="grey").grid(row=1, column=6, padx=1, pady=1, sticky="nsew")
            
            i = 2
            x_coord = y_coord = None
            for row in my_reader:
                
                if self.map_values['cpn_id']['index'] != -1:
                    text_col = Tkinter.Text(self.interior, bg=self.interior.cget('bg'), relief="flat", height=1, width=len(row[self.map_values['cpn_id']['index']]))
                    text_col.grid(row=i, column=0, padx=1, pady=1, sticky='w')
                    text_col.insert("1.0", row[self.map_values['cpn_id']['index']])
                    text_col.configure(state="disabled")
                
                if self.map_values['cpn_name']['index'] != -1:
                    text_col = Tkinter.Text(self.interior, bg=self.interior.cget('bg'), relief="flat", height=1, width=len(row[self.map_values['cpn_name']['index']]))
                    text_col.grid(row=i, column=1, padx=1, pady=1, sticky='w')
                    text_col.insert("1.0", row[self.map_values['cpn_name']['index']])
                    text_col.configure(state="disabled")
                
                #Tkinter.Label(frame_row, text=row[self.map_values['cpn_name']['index']] or ' ').grid(row=0, column=1, padx=1, pady=1, sticky='w')
                address = ''
                for x in range(1,4):
                    if self.map_values['address%s' % x]['index'] != -1:
                        address += row[self.map_values['address%s' % x]['index']] + ' '
                
                Tkinter.Label(self.interior, text=address).grid(row=i, column=2, padx=1, pady=1, sticky='w')
                
                if self.map_values['notes']['index'] != -1:
                    Tkinter.Label(self.interior, text=row[self.map_values['notes']['index']] or ' ', wraplength=500, justify="left").grid(row=i, column=3, padx=1, pady=1, sticky='w')
                
                # Get the X, Y Coords from GeoDB
                if    self.map_values['cpn_id']['value'] != 'None':
                    with pyodbc.connect('DRIVER={SQL Server};SERVER=pr-gis-sql1;DATABASE=NZFS_core;Trusted_Connection=True', autocommit=True) as cnxn:
                        cursor = cnxn.cursor()
                        x_coord, y_coord = cursor.execute("SELECT SHAPE.STX, SHAPE.STY FROM coredata.PLACE WHERE PlaceID = %s" % row[self.map_values['cpn_id']['index']]).fetchone()
                elif self.map_values['x_coord']['value'] != 'None' and self.map_values['y_coord']['value'] != 'None':
                    x_coord = row[self.map_values['x_coord']['index']]
                    y_coord = row[self.map_values['y_coord']['index']]
                
                Tkinter.Label(self.interior, text=x_coord or ' ').grid(row=i, column=4, padx=1, pady=1, sticky='w')
                Tkinter.Label(self.interior, text=y_coord or ' ').grid(row=i, column=5, padx=1, pady=1, sticky='w')
                
                # Create a Link to SMART Map
                
                frame_row_buttons = Tkinter.Frame(self.interior)
                frame_row_buttons.grid(row=i, column=6)
                action_with_arg = partial(webbrowser.open_new, "http://gis.fire.org.nz/apps/smartmap/index.htm?isextent=true&srid=2193&xmax=%s&ymax=%s&xmin=%s&ymin=%s" %(x_coord+100, y_coord+100, x_coord-100, y_coord-100))
                bt_view = Tkinter.Button(frame_row_buttons, text="View", command=action_with_arg)
                bt_view.grid(row=0, column=0)
                
                bt_view = Tkinter.Button(frame_row_buttons, text="X", command=None)
                bt_view.grid(row=0, column=1)
                i += 1

    def open(self):
        """
        Dialog that allows the user to choose which csv to load
        """
        options = {}
        options['defaultextension'] = '.csv'
        options['filetypes'] = [('all files', '.*'), ('text files', '.csv')]
        options['initialdir'] = 'C:\\'
        #options['initialfile'] = 'myfile.txt'
        options['parent'] = self
        options['title'] = 'This is a title'
        
        self.filename = tkFileDialog.askopenfilename(**options)
        
        # Map fields of csv data
        self.map()
        
        #print self.map_values
        
        self.load_grid()
        
    
    def map(self):
        """
        Dialog that allows the user to choose which csv fields to map
        """
        
        headers = ['None']
        
        with open(self.filename, 'rb') as f:
            my_reader = csv.reader(f)
            headers_all = my_reader.next()
            for h in headers_all:
                headers.append(h)
        
        
        print('csv_headers: %s' % headers)
                    
        top = Tkinter.Toplevel(self)
        
        # ID
        Tkinter.Label(top, text="ID").grid(row=0, column=0, sticky="w")
        self.map_values['cpn_id'] = dict(object = Tkinter.StringVar())
        self.map_values['cpn_id']['object'].set("None")
        lb_id = ttk.Combobox(top, textvariable=self.map_values['cpn_id']['object'], state='readonly')
        lb_id['values'] = filter(None, headers)
        lb_id.grid(row=0, column=1)
        
        # CPN
        Tkinter.Label(top, text="CPN Name").grid(row=1, column=0, sticky="w")
        self.map_values['cpn_name'] = dict(object = Tkinter.StringVar())
        self.map_values['cpn_name']['object'].set("None")
        lb_cpn = ttk.Combobox(top, textvariable=self.map_values['cpn_name']['object'], state='readonly')
        lb_cpn['values'] = filter(None, headers)
        lb_cpn.grid(row=1, column=1)
        
        # Address1
        Tkinter.Label(top, text="Address1").grid(row=2, column=0, sticky="w")
        self.map_values['address1'] = dict(object = Tkinter.StringVar())
        self.map_values['address1']['object'].set("None")
        lb_address = ttk.Combobox(top, textvariable=self.map_values['address1']['object'], state='readonly')
        lb_address['values'] = filter(None, headers)
        lb_address.grid(row=2, column=1)
        
        # Address2
        Tkinter.Label(top, text="Address2").grid(row=3, column=0, sticky="w")
        self.map_values['address2'] = dict(object = Tkinter.StringVar())
        self.map_values['address2']['object'].set("None")
        lb_address = ttk.Combobox(top, textvariable=self.map_values['address2']['object'], state='readonly')
        lb_address['values'] = filter(None, headers)
        lb_address.grid(row=3, column=1)
        
        # Address3
        Tkinter.Label(top, text="Address3").grid(row=4, column=0, sticky="w")
        self.map_values['address3'] = dict(object = Tkinter.StringVar())
        self.map_values['address3']['object'].set("None")
        lb_address = ttk.Combobox(top, textvariable=self.map_values['address3']['object'], state='readonly')
        lb_address['values'] = filter(None, headers)
        lb_address.grid(row=4, column=1)
        
        # Notes
        Tkinter.Label(top, text="Notes").grid(row=5, column=0, sticky="w")
        self.map_values['notes'] = dict(object = Tkinter.StringVar())
        self.map_values['notes']['object'].set("None")
        lb_address = ttk.Combobox(top, textvariable=self.map_values['notes']['object'], state='readonly')
        lb_address['values'] = filter(None, headers)
        lb_address.grid(row=5, column=1)
        
        # X COORD
        Tkinter.Label(top, text="X Coord").grid(row=6, column=0, sticky="w")
        self.map_values['x_coord'] = dict(object = Tkinter.StringVar())
        self.map_values['x_coord']['object'].set("None")
        lb_address = ttk.Combobox(top, textvariable=self.map_values['x_coord']['object'], state='readonly')
        lb_address['values'] = filter(None, headers)
        lb_address.grid(row=6, column=1)
        
        # Y COORD
        Tkinter.Label(top, text="Y Coord").grid(row=7, column=0, sticky="w")
        self.map_values['y_coord'] = dict(object = Tkinter.StringVar())
        self.map_values['y_coord']['object'].set("None")
        lb_address = ttk.Combobox(top, textvariable=self.map_values['y_coord']['object'], state='readonly')
        lb_address['values'] = filter(None, headers)
        lb_address.grid(row=7, column=1)
        
        top.wait_window()
        
        for k, v in self.map_values.iteritems():
            self.map_values[k]['value'] = v['object'].get()
            self.map_values[k]['index'] = headers.index(v['object'].get())-1
            
        print self.map_values


if __name__ == '__main__':
    root = Tkinter.Tk()
    main = CPN_Check(root, 'test')
    main.pack(expand="true", fill="both")
    root.mainloop()
    

# ------ END OF FILE ----    