#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      burkej
#
# Created:     24/10/2014
# Copyright:   (c) burkej 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def main():
    # Copy text to clipboard
    def copy_text_callback(event):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.text_data.get("1.0", Tkinter.END))

    lbl_copy_text = Tkinter.Label(frame_data, text="Copy to Clipboard", fg="Blue", cursor="hand2")
    lbl_copy_text.grid(row=1, column=0, sticky="w")
    lbl_copy_text.bind("<Button-1>", copy_text_callback)

if __name__ == '__main__':
    main()
