# -*- coding: utf-8 -*-#
"""
# Requirements:
# Tables:
# Views:
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

class Cpn_Delivery(tab.Tab):
    """
    CPN Delivery
    """

    def __init__(self, root, name, *args, **kwargs):

        tab.Tab.__init__(self, root, name)

        self.root = root
        self.image_path = r'images\placeholder.gif'

        # For test purposes, load GeoDBStage connection string
        try:
            self.dbconn = self.root.con_string
            log.debug('Initiated using SMART Tools')
        except:
            self.dbconn = "DRIVER={SQL Server};SERVER=GeoDBStage;DATABASE=NZFS_core;Trusted_Connection=True"
            log.debug('Initiated using Test')

        # Enter any instance variables here

    def load(self):
        """
        Initiates the CPN Delivery application when the load button is clicked in the main module
        """
        self.frame_delivery = Tkinter.Frame(self.interior)
        self.frame_delivery.grid(column=0, row=0, sticky="nsew")
        with pyodbc.connect(self.dbconn) as cnxn:
            cursor = cnxn.cursor()
            delivery_schedule = cursor.execute("""Select DeliveryNumber as DeliveryNumber,
                                                    DeliveryDate as DeliveryDate,
                                                    TrainingDate,
                                                    LiveDate,
                                                    CONVERT(VARCHAR(10), ExtractDateTime, 120) as ExtractDateTime,
                                                    CONVERT(VARCHAR(10), TrainingLoadDateTime, 120) as TrainingLoadDateTime,
                                                    CONVERT(VARCHAR(10), LiveLoadDateTime, 120) as LiveLoadDateTime
                                                From coredata.IcadCPNDeliverySchedule
                                                Where DeliveryDate > DATEADD(day, -30, GETDATE()) --and DATEADD(day, 30, GETDATE())
                                                order by DeliveryNumber desc""").fetchall()

        headers = ['Delivery No', 'Delivery Date', 'Training Date', 'Live Date', 'Delivery Ran', 'Loaded into Training', 'Loaded into Live']
        row = None
        links = [dict(header='', body=lambda row: self.create_link(row))]
        self.table_schedule = table.Table(self.frame_delivery, headers=headers, data=delivery_schedule, links=links)
        self.table_schedule.pack()

        #self.text_results = Tkinter.Text(self.frame_delivery, height="10")
        #self.text_results.pack(pady=("10","5"))

        #btn_run = Tkinter.Button(self.frame_delivery, text="Run")
        #btn_run.pack(side="right")

    def create_link(self, row):
        """
        Creates a button or label for each delivery depending on the stage which the delivery is in.
        Label = blank - if the delivery is not ready to be run
        Button = Start Delivery - if the delivery is ready to be run
        Button = Update Training - if the delivery needs to be run into training
        Button = Update Live - if the delivery needs to be run into live
        Label = Complete - if the delivery process is completed
        """
        import datetime, time

        if datetime.datetime.now() < datetime.datetime.strptime(row[1], "%Y-%m-%d"):
            return Tkinter.Label(text="")
        if not row[4] and datetime.datetime.now() >= datetime.datetime.strptime(row[1], "%Y-%m-%d"):
            action_with_arg = partial(self.start_delivery, row.DeliveryNumber)
            return Tkinter.Button(text="Start Delivery", command=action_with_arg)
        elif not row[5]:
            action_with_arg = partial(self.update_training, row.DeliveryNumber)
            return Tkinter.Button(text="Update Training", command=action_with_arg)
        elif not row[6]:
            action_with_arg = partial(self.update_live, row.DeliveryNumber)
            return Tkinter.Button(text="Update Live", command=action_with_arg)
        else:
            return Tkinter.Label(text="Complete")


    def start_delivery(self, delivery_number):
        # Create the Delivery Class (window)
        frame_delivery = Delivery(self.root, name="Delivery", delivery_number=delivery_number, bd=2, relief="sunken")
        frame_delivery.pack(expand="true", fill="both")
        frame_delivery.load()

        self.root.add(frame_delivery, None)
        self.root.switch_tab("Delivery")


        # QA CPN's to deliver

        # Create Delivery Folder

        # Run Stored Procedure

        # Export to csv

        # Zip and ship
        pass

    def update_training(self, temp):
        pass

    def update_live(self, temp):
        pass


class Delivery(tab.Tab):
    """
    """
    def __init__(self, root, name, delivery_number, *args, **kwargs):

        tab.Tab.__init__(self, root, name)

        self.root = root
        self.delivery_number = delivery_number

        # For test purposes, load GeoDBStage connection string
        try:
            self.dbconn = self.root.con_string
            log.debug('Initiated using SMART Tools')
        except:
            self.dbconn = "DRIVER={SQL Server};SERVER=GeoDBStage;DATABASE=NZFS_core;Trusted_Connection=True"
            log.debug('Initiated using Test')

    def load(self):

        self.frame_delivery = Tkinter.Frame(self.interior)
        self.frame_delivery.grid(column=0, row=0, sticky="nsew")
        with pyodbc.connect(self.dbconn) as cnxn:
            cursor = cnxn.cursor()
            delivery_schedule = cursor.execute("""Select DeliveryNumber as DeliveryNumber,
                                                    DeliveryDate as DeliveryDate,
                                                    TrainingDate,
                                                    LiveDate,
                                                    CONVERT(VARCHAR(10), ExtractDateTime, 120) as ExtractDateTime,
                                                    CONVERT(VARCHAR(10), TrainingLoadDateTime, 120) as TrainingLoadDateTime,
                                                    CONVERT(VARCHAR(10), LiveLoadDateTime, 120) as LiveLoadDateTime
                                                From coredata.IcadCPNDeliverySchedule
                                                Where DeliveryNumber = '%s'
                                                order by DeliveryNumber desc""" % self.delivery_number).fetchall()

        headers = ['Delivery No', 'Delivery Date', 'Training Date', 'Live Date', 'Delivery Ran', 'Loaded into Training', 'Loaded into Live']

        self.table_schedule = table.Table(self.frame_delivery, headers=headers, data=delivery_schedule)
        self.table_schedule.pack()

        self.text_results = Tkinter.Text(self.frame_delivery, height="10")
        self.text_results.pack(pady=("10","5"))

        btn_run = Tkinter.Button(self.frame_delivery, text="Run", command=self.run_check)
        btn_run.pack(side="right")

    def run_check(self):
        with pyodbc.connect(self.dbconn) as cnxn:
            cursor = cnxn.cursor()
            # CPN's with no primary address assigned
            self.text_results.insert("end", "Fixing CPN's with no primary address assigned...")
            cursor.execute("""update coredata.mv_PlaceAddress set PrimaryAddress = 1 where PrimaryAddress = 0
                                and ObjectID in (select top 1 ObjectID from coredata.mv_PlaceAddress where PrimaryAddress = 0 and PlaceID not in (select PlaceID from coredata.mv_PlaceAddress where PrimaryAddress = 1))""")
            self.text_results.insert("end", "Done\n")

            # CPN's with no primary name assigned
            self.text_results.insert("end", "Fixing CPN's with no primary name assigned...")
            cursor.execute("""update coredata.mv_PlaceName set PrimaryName = 1 where PrimaryName = 0
                                and ObjectID in (select top 1 ObjectID from coredata.mv_PlaceName where PrimaryName = 0 and PlaceID not in (select PlaceID from coredata.mv_PlaceName where PrimaryName = 1))""")
            self.text_results.insert("end", "Done\n")

            # CPN's where the primary name has changed
            self.text_results.insert("end", "Fixing Alarm names where the CPN primary name has changed...")
            cursor.execute("""update coredata.mv_placealarm set alarmname = ''
                                where placeid in (select pa.placeid
                                    from coredata.mv_placealarm pa join (select * from coredata.mv_PlaceName where LastModified is not null and PrimaryName = 1) b on pa.PlaceID = b.placeid
                                    where pa.AlarmName <> b.Name and pa.AlarmName <>'')""")
            cursor.execute("""update coredata.mv_placealarm set alarmname = '' where PlaceID not in
                            (select PlaceID from coredata.mv_PlaceName) and PFANumber not in ('999941','999940') """)
            self.text_results.insert("end", "Done\n")


if __name__ == '__main__':
    root = Tkinter.Tk()
    root.minsize(700, 300)
    root.geometry("700x500")

    #main = Cpn_Delivery(root, "test")
    main = Delivery(root, "test", '34.1.0')
    main.load()
    main.pack(expand="true", fill="both")

    root.mainloop()
    exit()


# ------ END OF FILE ----