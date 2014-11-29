import Tkinter
import logging

log = logging.getLogger(__package__)

class Tab(Tkinter.Frame):
    """
    A base tab class - with vertical scrolling
    """
    def __init__(self, master, name='test', *args, **kwargs):
        Tkinter.Frame.__init__(self, master, bd=2, relief="sunken", *args, **kwargs)
        self.name = name
        self.root = master

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Tkinter.Scrollbar(self, orient=Tkinter.VERTICAL)
        vscrollbar.pack(side="right", fill="y",  expand="false")
        self.canvas = Tkinter.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set, **kwargs)
        self.canvas.pack(side="left", fill="both", expand="true")
        vscrollbar.config(command=self.canvas.yview)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Tkinter.Frame(self.canvas, *args, **kwargs)
        self.interior.pack(fill="both", expand="true")

        self.canvas.create_window(0, 0, window=interior, anchor="nw")

        self.bind('<Configure>', self.set_scrollregion)


    def _on_mousewheel(self, event):
        #test = -1*(event.delta/120)
        self.canvas.yview_scroll(-1*(event.delta/120), "units")

    def set_scrollregion(self, event=None):
        """ Set the scroll region on the canvas"""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    """
    def add(self, tab, button):
        # hide the tab on init
        tab.pack_forget()

        # add it to the list of tabs
        # pack the button to the left most of self
        self.tabs[tab.name] = tab
        # add it to the list of buttons
        self.buttons[tab.name] = button

    def switch_tab(self, name):
        if self.current_tab:
            # hide the current tab
            self.tabs[self.current_tab].pack_forget()
        # add the new tab to the display
        self.tabs[name].pack(expand="true", fill="both")
        self.root.title("Smart Tools - %s" % name)
        # set the current tab to itself
        self.current_tab = name

        # Maintains the back/forward order
        if self.current_tab == 'Home':
            self.tab_order = ['Home']
            self.tab_order_index = 0
            self.btn_back.config(state="disabled")
        else:
            self.tab_order.append(self.current_tab)
            self.tab_order_index = self.tab_order.index(self.current_tab)
            self.btn_back.config(state="normal")

    def back(self):
        log.debug(self.tab_order)
        log.debug(self.tab_order_index)
        self.tab_order_index = self.tab_order.index(self.current_tab)-1
        self.switch_tab(self.tab_order[self.tab_order_index])


    def forward(self):
        log.debug(self.tab_order)
        log.debug(self.tab_order_index)
        self.tab_order_index = self.tab_order.index(self.current_tab)+1
        self.switch_tab(self.tab_order[self.tab_order_index])
    """

if __name__ == '__main__':
    root = Tkinter.Tk()
    main = Tab(root, 'test')
    main.pack()
    for x in range(20):
        Tkinter.Checkbutton(main.interior, text="hello world! %s" % x).grid(row=x, column=0)
    root.mainloop()
