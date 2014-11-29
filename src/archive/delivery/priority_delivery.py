# -*- coding: utf-8 -*-#
"""
# Requirements:
# Tables: IcadPriorityChange_H
# Views: vw_IcadPriorityChange
"""

# Hyperlink :: http://effbot.org/zone/tkinter-text-hyperlink.htm

import Tkinter, ttk, tkMessageBox
import logging
import webbrowser
from functools import partial
import sys
import pyodbc

try:
    import stsrc.models.tab as tab
    import stsrc.models.table as table
except:
    sys.path.append(r'C:\Users\burkej\Documents\Projects\SMART Tools\Smart Tools\stsrc')
    import models.tab as tab
    import models.table as table

    format = '%(name)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s'
    logging.basicConfig(format=format, level=logging.NOTSET)

log = logging.getLogger(__package__)

class Priority_Delivery(tab.Tab):
    """
    Verify and send Priority Request data to Comcen.
    """

    def __init__(self, root, name, *args, **kwargs):

        tab.Tab.__init__(self, root, name)

        self.root = root
        self.image_path = r'images\priority_request.gif'

        self.cpn_id_list = []
        try:
            self.dbconn = self.root.con_string
            log.debug('Initiated using SMART Tools')
        except:
            self.dbconn = "DRIVER={SQL Server};SERVER=GeoDB;DATABASE=NZFS_core;Trusted_Connection=True"
            log.debug('Initiated using Test')

    def load(self):
        """
        Initiates the Priority Delivery application when the load button is clicked in the main module
        """
        # Search
        self.frame_search = Tkinter.Frame(self.interior)
        self.frame_search.grid(column=0, row=0, sticky="nsew")

        Tkinter.Label(self.frame_search, text="CPN/PFA Number").grid(row=0, column=0, padx=1, pady=1)

        self.entry_number = Tkinter.Entry(self.frame_search)
        self.entry_number.grid(row=0, column=1, padx=5)
        self.entry_number.bind('<Return>', self.search) # enter key searches when text box is focused

        btn_search = Tkinter.Button(self.frame_search, text="Search", command=self.search)
        btn_search.grid(row=0, column=2, padx=1, pady=1)

        self.status_results_frame = None
        self.data_results_frame = None

        # Load Priority Change Table
        self.load_priority_changes()

    def export_to_csv(self):
        """
        Export the contents of the IcadPriorityChange tables into csv files
        """
        import csv, datetime

        # Create csv files of the priority records to be sent
        with pyodbc.connect(self.dbconn) as cnxn:
            cursor = cnxn.cursor()

            # Get data from all the IcadPriorityChange tables to export to csv
            table_list = ['cpn', 'alias', 'message', 'alarm']
            for table in table_list:
                pr_table = cursor.execute("""SELECT *
                                    FROM [NZFS_core].[coredata].[IcadPriorityChange%s]""" % table).fetchall()
                log.debug('priority change data %s: %s' % (table, pr_table))

                with open(r'P:\ICTS\DSA\Smart Tools\Test\%s_%s_pr.csv' % (datetime.datetime.now().strftime("%Y%m%d"), table), 'wb') as myfile:
                    wr = csv.writer(myfile, delimiter="|", quoting=csv.QUOTE_ALL)

                    # Write the header to the csv file
                    table_header = cursor.execute("""SELECT COLUMN_NAME
                                                        FROM NZFS_core.INFORMATION_SCHEMA.COLUMNS
                                                        WHERE TABLE_NAME = 'IcadPriorityChange%s'""" % table).fetchall()
                    #log.debug("table header: %s" % table_header)

                    table_header = [item for sublist in table_header for item in sublist]
                    log.debug("table header: %s" % table_header)

                    wr.writerow(table_header)

                    # Write each record to the csv file
                    for record in pr_table:
                        wr.writerow(record)

                        if table == 'cpn':
                            self.cpn_id_list.append(str(record[0]))

    def create_email(self):
        """
        Generate an email to send to integraph & police with the priority changes
        """
        import webbrowser

        cpn_id = []
        # Create csv files of the priority records to be sent
        with pyodbc.connect(self.dbconn) as cnxn:
            cursor = cnxn.cursor()

            # Create a list of the priority changes to be displayed in the email
            try:
                cpn_list = cursor.execute("""SELECT DISTINCT CPN_Name + ': ' +
                                                    CASE WHEN CPN_in_ICAD = 'True' THEN 'Existing CPN, ' ELSE 'New CPN,' END +
                                                    CASE WHEN PFA_in_ICAD = 'True' THEN 'Existing PFA' ELSE 'New PFA' END +
                                                    CASE WHEN SRZ_in_ICAD = 'True' THEN '' ELSE ', New SRZ (' + CONVERT(varchar(10), SRZ) + ')' END
                                                    FROM [NZFS_core].[coredata].[IcadPriorityChange_H]
                                                    WHERE CPN_ID IN (%s) AND DATEDIFF(DAY, Date_Sent, GETDATE()) < 3""" % ",".join(self.cpn_id_list)).fetchall()
                log.debug("cpn list: %s" % cpn_list)
            except Exception as e:
                log.warning("CPN List Warning: %s" % e)
                tkMessageBox.showinfo("Warning", "No records found in the IcadPriorityChange tables.")
                return

            cpn_text = '%0D%0A'.join(str(elem[0]) for elem in cpn_list)
            log.debug(cpn_list)
            #
            webbrowser.open_new('mailto:Ross.Pickard@intergraph.com;Peter.Livesey@police.govt.nz;ips.change.control@intergraph.co.nz;application.support@police.govt.nz;Justin.Harris@police.govt.nz?cc=Data.Change@fire.org.nz&subject=NZFS CPN/PFA Priority two Update: ' + str(cpn_list[0][0]).split(':')[0] + '&body=Hi All,%0D%0A%0D%0ACan the attached CPN/PFA changes please be applied to all databases. DB%0D%0A' + cpn_text + '%0D%0A%0D%0ACheers,%0D%0A%0D%0A')


    def search(self, event=None): # 250186  3020143851 # 114926 3000000120
        """
        Using the input id entered in the Entry box search for relate CPN and PFA data
        """
        input_id = self.entry_number.get()
        input_id = "\',\'".join(self.entry_number.get().split(',')).replace(" ", "")

        cpn_no = None

        log.debug('input id: %s' % input_id)

        # Open a connection to the Database
        with pyodbc.connect(self.dbconn) as cnxn:
            cursor = cnxn.cursor()
            try:
                # Get the CPN ID from DeliveryAlarm using the input id (assumed pfa no)
                pfa_check = cursor.execute("""SELECT CMPNSUFI, SUPPLIER_SUFI
                                        FROM [NZFS_core].[coredata].[vw_IcadDeliveryAlarm]
                                        WHERE SUPPLIER_SUFI IN ('%s')""" % input_id).fetchall()
                log.debug('pfa data: %s' % pfa_check)

                cpn_check = cursor.execute("""SELECT CPN_ID
                                        FROM [NZFS_core].[coredata].[vw_IcadDeliveryCPN]
                                        WHERE CPN_ID IN ('%s')""" % input_id).fetchall()
                log.debug('cpn data: %s' % cpn_check)




                # If no record exists use input id (now assumed cpn no)
                if len(pfa_check) > 1:
                    x = [x[0] for x in pfa_check]
                    x = set(x)
                    x = list(x)
                    if len(x) == 1:
                        cpn_no = x[0]
                        log.debug('TEST1: %s' % cpn_no)
                    else:
                        x = map(str, x)
                        cpn_no = "\',\'".join(x)
                        log.debug('TEST2: %s' % cpn_no)

                elif pfa_check:
                    cpn_no = pfa_check[0][0]
                elif cpn_check:
                    cpn_no = input_id
                else:
                    tkMessageBox.showinfo("Warning", "ID could not be found, check if the CPN is pending QA")
                    log.warning("ID could not be found, check if the CPN is pending QA")
                    return

                log.debug("CPN Number: %s" % cpn_no)

            except Exception as e:
                log.error("SQL Server Error: %s" % e)
                tkMessageBox.showinfo("Error", "System Error, check input id.")
                return

        self.load_search_results(cpn_no)

        self.load_priority_changes()

    def load_search_results(self, cpn_no): # 250186  3020143851 # 3000049679
        """
        Get a summary of the priority request
        """
        import ttk
        from collections import OrderedDict

        # Remove the current status & data frames
        try:
            self.frame_status_results.grid_forget()
            self.frame_status_results.destroy()
            self.frame_data_results.grid_forget()
            self.frame_data_results.destroy()
        except:
            # No frame results has been initialised
            pass

        cpn_list = OrderedDict()
        table_col_name_list = dict()

        with pyodbc.connect(self.dbconn) as cnxn:
            cursor = cnxn.cursor()

            # Get the Status of the Priority Request - doesn't work for CPN's withouth a PFA
            pr_info = cursor.execute("""SELECT *
                                    FROM [NZFS_core].[coredata].[vw_IcadPriorityChange]
                                    WHERE CPN_ID IN ('%s')""" % cpn_no).fetchall()
            log.debug('priority change data: %s' % pr_info)

            # Get the CPN, Alias, Message and Alarm records relating to the CPN
            table_list = OrderedDict([('CPN','CPN_ID'), ('Alias','CMPNSUFI'), ('Message','CMPNSUFI'), ('Alarm','CMPNSUFI')])
            table_col_name_list = {'CPN':["CPN_ID","ROAD_NAME","ROAD_TYPE","ROAD_SUFFIX","SUBURB_NAME","TLA","CPN_NAME","CATEGORIES","SRZ"],
                                    'Alias':["CMPNSUFI","CPALIAS_ID","CALIASNAME","CATEGORY"],
                                    'Message':["CMPNSUFI","ACCESS_DETAILS","DIRECTIONS","MESSAGE"],
                                    'Alarm':["CMPNSUFI","SUPPLIER_SUFI","ALARMTYPE","ALARM_TYCODE","CALLSOURCE_DESCR","ALARMNAME","INSTRUCTION"]
                                    }
            for table_name, col_name in table_list.iteritems():
                #log.debug(",".join(table_col_name_list))
                cpn_list[table_name] = cursor.execute("""SELECT %s
                                        FROM [NZFS_core].[coredata].[vw_IcadDelivery%s]
                                        WHERE %s IN ('%s')""" %(",".join(table_col_name_list[table_name]),table_name, col_name, cpn_no)).fetchall()
            log.debug("CPN List: %s" % cpn_list)

        if cpn_list:
            # Create a table of the Status results
            self.frame_check_results = Tkinter.LabelFrame(self.interior, text="Check Results")
            self.frame_check_results.grid(row=1, column=0, padx=1, pady=2, sticky="nw")

            self.frame_status_results = Tkinter.LabelFrame(self.frame_check_results, text="Status")
            self.frame_status_results.grid(row=0, column=0, padx=1, pady=2, sticky="nw")

            headers = ['PFA Number', 'CPN ID', 'CPN Name', 'SRZ', 'CPN in ICAD?', 'PFA in ICAD?', 'SRZ in ICAD?']
            results_table = table.Table(self.frame_status_results, headers=headers, data=pr_info)
            results_table.pack()

            # Create a tab menu with tables of the CPN, Alias, etc records
            self.frame_data_results = Tkinter.LabelFrame(self.frame_check_results, text="Data")
            self.frame_data_results.grid(row=1, column=0, padx=1, pady=2, sticky="nsew")
            tab = dict()
            tabs = ttk.Notebook(self.frame_data_results)

            for table_name, data in cpn_list.iteritems():
                tab[table_name] = Tkinter.Frame(tabs)

                headers = table_col_name_list[table_name]
                results_table = table.Table(tab[table_name], headers=headers, data=data)
                results_table.grid()

                tabs.add(tab[table_name], text=table_name)

            tabs.grid()

            # Add all records associated with the CPN
            save_priority_change = partial(self.save_priority_change, cpn_no)
            btn_save = Tkinter.Button(self.frame_check_results, text="Save", command=save_priority_change)
            btn_save.grid(row=2, column=0, padx=1, pady=1, sticky="nw")
        else:
            pass
            #tkMessageBox.showinfo("Warning", "ID could not be found, check if the CPN is pending QA")
            #log.warning("ID could not be found, check if the CPN is pending QA")


    def save_priority_change(self, cpn_no):
        """
        Insert priority changes into the delivery tables
        Create a record in the priority change history table
        """
        log.debug('save priority change')

        with pyodbc.connect(self.dbconn) as cnxn:
            cursor = cnxn.cursor()
            # query tables in the dict, value is the column name used in the where clause
            table_list = {'CPN': 'CPN_ID', 'Alias': 'CMPNSUFI', 'Message': 'CMPNSUFI', 'Alarm': 'CMPNSUFI'}
            for table, col_name in table_list.iteritems():
                cursor.execute("""INSERT INTO [coredata].[IcadPriorityChange%s]
                                        SELECT *
                                        FROM [NZFS_core].[coredata].[vw_IcadDelivery%s]
                                        WHERE %s IN ('%s')""" %(table, table, col_name, cpn_no))
            cnxn.commit()

        self.load_priority_changes()

    def removeall_priority_change(self):
        """
        Deletes all records in the IcadPriorityChange tables
        """
        with pyodbc.connect(self.dbconn) as cnxn:
            cursor = cnxn.cursor()
            for table in ['CPN', 'Alias', 'Message', 'Alarm']:
                cursor.execute("""DELETE FROM NZFS_core.coredata.IcadPriorityChange%s""" %(table))
            cnxn.commit()

        self.load_priority_changes()

    def load_priority_changes(self): # 250186  3020143851 # 3000049679
        """
        Load contents of IcadPriorityChangeCPN into a gui table
        """
        from collections import OrderedDict
        import ttk

        try:
            self.frame_priority_changes.grid_forget()
            self.frame_priority_changes.destroy()
        except:
            # No frame results has been initialised
            pass

        # CALL BACKS #
        def remove_pr_record(cpn_id):
            """
            Remove Priority Request Record Callback
            """
            log.debug(cpn_id)
            with pyodbc.connect(self.dbconn) as cnxn:
                cursor = cnxn.cursor()
                for table in ['CPN', 'Alias', 'Message', 'Alarm']:
                    cursor.execute("""DELETE FROM NZFS_core.coredata.IcadPriorityChange%s WHERE CPN_ID = '%s'""" %(table, cpn_id))
                cnxn.commit()
            self.load_priority_changes()

        def send_priorit_requests():
            """
            Send the saved priority requests
            """
            import webbrowser

            # Get the CPN ID from DeliveryAlarm using the input id (assumed pfa no)
            log.debug("save PR to history")
            with pyodbc.connect(self.dbconn) as cnxn:
                cursor = cnxn.cursor()
                cursor.execute("""INSERT INTO [coredata].[IcadPriorityChange_H]
                                            SELECT *
                                         	  ,GetDate()
                                              FROM [NZFS_core].[coredata].[vw_IcadPriorityChange]
                                              WHERE CPN_ID IN (SELECT CPN_ID FROM [NZFS_Core].[coredata].[IcadPriorityChangeCPN])""")
                cnxn.commit()

            #log.debug("export to csv")
            self.export_to_csv()
            #log.debug("create email")
            self.create_email()
            webbrowser.open_new(r'file://P:\ICTS\DSA\Smart Tools\Test')
            #log.debug("remove all pr")
            self.removeall_priority_change()

        cpn_list = OrderedDict()

        with pyodbc.connect(self.dbconn) as cnxn:
            cursor = cnxn.cursor()
            # Get the CPN ID from DeliveryAlarm using the input id (assumed pfa no)

            # Get the CPN, Alias, Message and Alarm records relating to the CPN
            table_list = ['CPN','Alias','Message','Alarm']
            table_col_name_list = {'CPN':["CPN_ID","ROAD_NAME","ROAD_TYPE","ROAD_SUFFIX","SUBURB_NAME","TLA","CPN_NAME","CATEGORIES","SRZ"],
                                    'Alias':["CPN_ID","CPALIAS_ID","CALIASNAME","CATEGORY"],
                                    'Message':["CPN_ID","ACCESS_DETAILS","DIRECTIONS","MESSAGE"],
                                    'Alarm':["CPN_ID","ALARM_ID","ALARM_TYPE","ALARM_TYCOD","CALL_SOUR","COMPANY","INSTRUCTION"]
                                    }
            for table_name in table_list:
                #log.debug(",".join(table_col_name_list))
                cpn_list[table_name] = cursor.execute("""SELECT %s
                                        FROM [NZFS_core].[coredata].[IcadPriorityChange%s]
                                        """ %(",".join(table_col_name_list[table_name]),table_name)).fetchall()
            log.debug("Table List: %s" % table_list)
            log.debug("CPN List: %s" % cpn_list)

        if cpn_list['CPN']:
            self.frame_priority_changes = Tkinter.LabelFrame(self.interior, text="Priority Changes - DB")
            self.frame_priority_changes.grid(row=4, column=0, padx=1, pady=2, sticky="nw")

            # Remove All Priority Changes
            self.frame_change_buttons = Tkinter.Frame(self.frame_priority_changes)
            self.frame_change_buttons.grid(column=0, row=0, sticky="nw")

            # Remove All Button
            removeall_priority_change = partial(self.removeall_priority_change)
            btn_removeall = Tkinter.Button(self.frame_change_buttons, text="Remove All", command=removeall_priority_change)
            btn_removeall.grid(row=0, column=0, padx=1, pady=1)

            # Send Priority Changes to Police & Intergraph
            frame_send_buttons = Tkinter.Frame(self.frame_priority_changes)
            frame_send_buttons.grid(column=0, row=3, sticky="nw")

            btn_open_csv_dir = Tkinter.Button(frame_send_buttons, text="Create Email", command=send_priorit_requests)
            btn_open_csv_dir.grid(row=0, column=0, padx=1, pady=1)

            # Create a tab menu with tables of the CPN, Alias, etc records
            tab = OrderedDict()
            tabs = ttk.Notebook(self.frame_priority_changes)
            log.debug(cpn_list)

            for table_name, data in cpn_list.iteritems():
                tab[table_name] = Tkinter.Frame(tabs)

                headers = table_col_name_list[table_name]
                if table_name == 'CPN':
                    buttons = [dict(text='Remove', function=lambda row: remove_pr_record(row[0]))]
                else:
                    buttons = []
                results_table = table.Table(tab[table_name], headers=headers, data=data, buttons=buttons)
                results_table.grid()

                tabs.add(tab[table_name], text=table_name)

            tabs.grid(column=0, row=2, sticky="nw")


if __name__ == '__main__':
    root = Tkinter.Tk()
    main = Priority_Delivery(root, "test")
    main.load()
    main.pack(expand="true", fill="both")
    root.mainloop()
    exit()


# ------ END OF FILE ----