import Tkinter as tk
import ttk

class App:
    def __init__(self):
        headings = ['One']


        self.tree = ttk.Treeview(self.root, columns=headings)
        self.tree.pack()

        self.tree.heading(headings[0], text="Test")
        for i in range(10):
            self.tree.insert("", "end", text="Item %s" % i)
        self.tree.bind("<Double-1>", self.OnDoubleClick)


    def OnDoubleClick(self, event):
        item = self.tree.selection()[0]
        print "you clicked on", self.tree.item(item,"text")

if __name__ == "__main__":
    root = tk.Tk()
    app=App()
    root.mainloop()