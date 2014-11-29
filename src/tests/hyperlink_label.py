'''
Created on 6/05/2014

@author: burkej
'''

if __name__ == '__main__':
    import Tkinter
    import webbrowser
    
    def google_link_callback(event):
        webbrowser.open_new(r"http://www.google.com")
    
    
    root = Tkinter.Tk()
    lbl_google_link = Tkinter.Label(root, text="Google Hyperlink", fg="Blue", cursor="hand2")
    lbl_google_link.pack()
    lbl_google_link.bind("<Button-1>", google_link_callback)
    root.mainloop()