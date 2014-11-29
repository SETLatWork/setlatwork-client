'''
Created on 10/05/2014

@author: James
'''
import Tkinter
from functools import partial
import logging

format = '%(name)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s'
logging.basicConfig(format=format, level=logging.NOTSET)

log = logging.getLogger(__package__)

class Table(Tkinter.Frame):

    def __init__(self, parent, headers, data, links=[], buttons=[], pagination=0, delete=False, *args, **kwargs):
        """
        headers: list - column headers
        data: list of list - data to display
        links: list of dict - (header=header label, body=lambda expression)
            Note: the difference between a link and a button, a link can be anything a button is a button.
        buttons: list of dict - (header=button label, function=lambda expression)
        pagination: integer - number of rows for each page
        delete: bool - superficial delete button remove the row from the table
                but has no affect on the underlaying data.
        """
        Tkinter.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.headers = headers
        self.data = data
        self.links = links
        self.buttons = buttons
        self.pagination = pagination
        self.delete = delete

        self.frame_table = Tkinter.Frame(self)
        self.frame_table.pack()

        if self.pagination:
            self.page_change(1)
        else:
            self.load_table(data, None)

    def load_table(self, data, selected_page):
        header_i = 0

        for header in self.headers:
            Tkinter.Label(self.frame_table, text=header, bg="grey").grid(row=0, column=header_i, padx=1, pady=1, sticky='nsew')
            header_i += 1
        for link in self.links:
            Tkinter.Label(self.frame_table, text=link['header'], bg="grey").grid(row=0, column=header_i, padx=1, pady=1, sticky='nsew')
            header_i += 1
        if self.buttons:
            Tkinter.Label(self.frame_table, text="", bg="grey").grid(row=0, column=header_i, padx=1, pady=1, sticky='nsew')

        col_i = 1
        row_i = 1
        for row in data:
            row_list = []
            col_i = 0
            for col in row:
                if col_i == len(self.headers):
                    break
                row_item = Tkinter.Label(self.frame_table, text=col)
                row_item.grid(row=row_i, column=col_i, padx=1, pady=1, sticky='w')
                row_list.append(row_item)
                col_i += 1
            for link in self.links:
                row_item = link['body'](row) #.replace("Parent", "self.frame_table"))
                row_item.grid(row=row_i, column=col_i, padx=1, pady=1, sticky='w', in_=self.frame_table)
                row_list.append(row_item)
                #log.debug(link)
                col_i += 1
            if self.buttons or self.delete:
                frame_btns = Tkinter.Frame(self.frame_table)
                frame_btns.grid(row=row_i, column=col_i)
                row_list.append(frame_btns)
                btn_i = 0
                if self.buttons:
                    for button in self.buttons:
                        try:
                            param = button['parameters']
                        except:
                            param = row
                        map_command = partial(button['function'], param)
                        btn_map = Tkinter.Button(frame_btns, text=button['text'], command=map_command)
                        btn_map.grid(row=0, column=btn_i, padx=1, pady=1, sticky='w')
                        btn_i += 1
                if self.delete:
                    btn_map = Tkinter.Button(frame_btns, text="Remove", command=lambda row_list=row_list, row_i=row_i:self.delete_row(row_list, row_i-1))
                    btn_map.grid(row=0, column=btn_i, padx=1, pady=1, sticky='w')
                col_i += 1
            row_i += 1

        #try:
        if self.pagination:
            import math

            frame_page = Tkinter.Frame(self.frame_table)
            frame_page.grid(row=row_i, column=col_i-1, columnspan=col_i, sticky="e")
            pages = int(math.ceil(float(len(self.data)) / float(self.pagination))) + 1

            page_i = 0
            for page in range(1, pages):
                if page == selected_page:
                    btn_map = Tkinter.Button(frame_page, text=page, relief="sunken", command=lambda page=page:self.page_change(page))
                else:
                    btn_map = Tkinter.Button(frame_page, text=page, command=lambda page=page:self.page_change(page))
                btn_map.grid(row=0, column=page_i, padx=1, pady=1, sticky='w')
                page_i += 1
        #except Exception as e:
        #   log.warning('pagination warning: %s' % e)

    def delete_row(self, row, index):
        del self.data[index]
        for item in row:
            item.grid_forget()

    def page_change(self, page):
        self.frame_table.pack_forget()
        self.frame_table.destroy()
        self.frame_table = Tkinter.Frame(self)
        self.frame_table.grid()

        if page == 1:
            start = 0
            end = self.pagination
        elif page == 2:
            start = self.pagination
            end = self.pagination + self.pagination
        else:
            start = (page - 1) * self.pagination
            end = ((page - 1) * self.pagination) + self.pagination
        self.load_table(self.data[start:end], page)

if __name__ == '__main__':
    def btn_click(p):
        print p

    headers = ['test', 'test1']
    data = [['r%s_c1' % x,'r%s_c2' % x] for x in range(1,20)]

    links = [dict(header='Test', body="Tkinter.Label(Parent, text='rolf')")]
    buttons = [dict(text='test1', function=lambda row: btn_click(row[0])),
               dict(text='test2', function=btn_click, parameters=dict(hello='world'))]

    root = Tkinter.Tk()
    table = Table(parent=root, headers=headers, data=data, links=links, buttons=buttons, pagination=5, delete=True)
    table.pack()
    root.mainloop()