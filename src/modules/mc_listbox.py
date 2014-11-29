"""
Based on: https://code.google.com/p/python-ttk/source/browse/trunk/pyttk-samples/treeview_multicolumn.py?r=21
"""

import Tkinter #as tk
import ttk as ttk

class McListBox(Tkinter.Frame):
    """
    Multi-column List Box
    Displays data in a
    """
    def __init__(self, parent, headers=[], data=[], **kwargs):

        Tkinter.Frame.__init__(self, parent)

        self.tree = None

        self.headers = headers
        self.data = data

        self.tree = ttk.Treeview(columns=self.headers, show="headings")
        vsb = ttk.Scrollbar(orient="vertical",command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal",command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set,xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=self)
        vsb.grid(column=1, row=0, sticky='ns', in_=self)
        hsb.grid(column=0, row=1, sticky='ew', in_=self)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.build_tree()

    def build_tree(self):
        def sortby(tree, col, descending):
            data = [(tree.set(child, col), child) \
                    for child in tree.get_children('')]
            data.sort(reverse=descending)
            for ix, item in enumerate(data):
                tree.move(item[1], '', ix)
            tree.heading(col, command=lambda col=col: sortby(tree, col, \
                                                          int(not descending)))
        print 'do cols'
        for col in self.headers:
            print col
            self.tree.heading(col, text=col.title(),
                              command=lambda c=col: sortby(self.tree, c, 0))
            self.tree.column(col,
                              width=len(col.title()))
        print 'do rows'
        for item in self.data:
            self.tree.insert('', 'end', values=item)
            for ix, val in enumerate(item):
                col_w = len(val)
                if self.tree.column(self.headers[ix],width=None)<col_w:
                    self.tree.column(self.headers[ix], width=col_w)
        print 'end'



if __name__ == "__main__":
    headers = ['car', 'repair']
    data = [
                ('Hyundai', 'brakes') ,
                ('Honda', 'light') ,
                ('Lexus', 'battery') ,
                ('Benz', 'wiper') ,
                ('Ford', 'tire') ,
                ('Chevy', 'air') ,
                ('Chrysler', 'piston') ,
                ('Toyota', 'brake pedal')]

    root = Tkinter.Tk()
    root.wm_title("multicolumn ListBox")
    mc_listbox = McListBox(root, headers=headers, data=data)
    mc_listbox.pack(fill='both', expand=True)
    root.mainloop()