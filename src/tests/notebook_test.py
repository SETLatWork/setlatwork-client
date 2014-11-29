# exploring the Tkinter expansion module ttk notebook
# tested with Python 3.1 and Tkinter 8.5 by vegaseat
 
import Tkinter as tk
import ttk as ttk
 
root = tk.Tk()
# use width x height + x_offset + y_offset (no spaces!)
root.geometry("%dx%d+%d+%d" % (300, 200, 100, 50))
root.title('test the ttk.Notebook')
 
nb = ttk.Notebook(root)
nb.pack(fill='both', expand='yes')
 
# create a child frame for each page
f1 = tk.Frame(bg='red')
f2 = tk.Frame(bg='blue')
f3 = tk.Frame(bg='green')
 
# create the pages
nb.add(f1, text='page1')
nb.add(f2, text='page2')
nb.add(f3, text='page3')
 
# put a button widget on child frame f1 on page1
btn1 = tk.Button(f1, text='button1')
btn1.pack(side='left', anchor='nw', padx=3, pady=5)
 
root.mainloop()