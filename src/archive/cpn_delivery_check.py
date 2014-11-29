'''
Created on 7/05/2014

@author: burkej
'''

import Tkinter
import logging
import pyodbc
from functools import partial
from collections import OrderedDict

import stsrc.models.table as table

log = logging.getLogger(__package__)

class CPN_Delivery_Check(Tkinter.Frame):
    def __init__(self, root, *args, **kwargs):
        
        Tkinter.Frame.__init__(self, root, *args, **kwargs)
        self.root = root
        
        btn_refresh = Tkinter.Button(self, text="Refresh", command=self.load_check)
        btn_refresh.grid(row=1, column=1, padx=1, pady=1)
        
        self.results = OrderedDict()
        
        self.load_check()
    
    
    def load_check(self):
        with pyodbc.connect(self.root.con_string) as cnxn:
            cursor = cnxn.cursor()
            
            # Number of CPN's without an Address or Name
            self.results['cpn_no_address'] = cursor.execute("select * from coredata.mv_PlaceAddress where PrimaryAddress = 0 and PlaceID not in(select PlaceID from coredata.mv_PlaceAddress where PrimaryAddress = 1)").fetchall()
        
            self.results['cpn_no_name'] = cursor.execute("select * from coredata.mv_PlaceName where PrimaryName  = 0 and PlaceID not in (select PlaceID from coredata.mv_PlaceName where PrimaryName = 1)").fetchall()
        
            # Number of CPN's with multiple Primary Name or Addresses
            self.results['cpn_multi_address'] = cursor.execute("""
                                                        select p.PlaceID,
                                                        NumberFlat + ' ' + RoadName + ' ' + RoadType +
                                                        CASE
                                                            WHEN RoadSuffix is not null THEN ' ' + RoadSuffix
                                                            ELSE ''
                                                        END + ' ' + LocalityName as FullAddress,
                                                        'http://gis.fire.org.nz/apps/smartmap/index.htm?isextent=true&srid=2193&xmax=' + str(SHAPE.STX+10, 15, 8) + '&ymax=' + str(SHAPE.STY+10, 15, 8) + '&xmin=' + str(SHAPE.STX-10, 15, 8) + '&ymin=' + str(SHAPE.STY-10, 15, 8) SmartLink
                                                        from coredata.mv_PlaceAddress pa
                                                        inner join coredata.mv_Place p
                                                        on pa.PlaceID = p.PlaceID
                                                        where pa.PlaceID in (select placeid from coredata.mv_PlaceAddress where primaryaddress = 1 group by PlaceID, PrimaryAddress having COUNT(*) > 1)
                                                        """).fetchall()
                                                        
            self.results['cpn_multi_name'] = cursor.execute("""select pn.PlaceID,
                                                        pn.Name,
                                                        'http://gis.fire.org.nz/apps/smartmap/index.htm?isextent=true&srid=2193&xmax=' + str(SHAPE.STX+10, 15, 8) + '&ymax=' + str(SHAPE.STY+10, 15, 8) + '&xmin=' + str(SHAPE.STX-10, 15, 8) + '&ymin=' + str(SHAPE.STY-10, 15, 8) SmartLink
                                                        from coredata.mv_PlaceName pn
                                                        inner join coredata.mv_Place p
                                                        on pn.PlaceID = p.PlaceID
                                                        where pn.PlaceID in (select placeid from coredata.mv_PlaceName where primaryName = 1 group by PlaceID, PrimaryName having COUNT(*) > 1)
                                                        """).fetchall()
            
            # Alarm Names - updates any Alarm names to '' where the CPN name has changed
            self.results['alarm_name_change'] = cursor.execute("""select pa.placeid 
                                                        from coredata.mv_placealarm pa 
                                                        join (select * from coredata.mv_PlaceName 
                                                        where LastModified is not null and PrimaryName = 1) b on pa.PlaceID = b.placeid 
                                                        where pa.AlarmName <> b.Name and pa.AlarmName <>''
                                                        """).fetchall()
            # Panel Info length > 73 characters
            self.results['panel_length'] = cursor.execute("""select pa.PlaceID,
                                                    pn.Name,
                                                    'http://gis.fire.org.nz/apps/smartmap/index.htm?isextent=true&srid=2193&xmax=' + str(SHAPE.STX+10, 15, 8) + '&ymax=' + str(SHAPE.STY+10, 15, 8) + '&xmin=' + str(SHAPE.STX-10, 15, 8) + '&ymin=' + str(SHAPE.STY-10, 15, 8) SmartLink
                                                    From coredata.mv_placealarm pa
                                                    inner join coredata.mv_Place p on pa.PlaceID = p.PlaceID
                                                    inner join coredata.mv_PlaceName pn on pn.PlaceID = p.PlaceID
                                                    where len(panelinfo) > 73
                                                    """).fetchall()
            
            # Duplicate PlaceID's
            #self.results['dup_placeid'] = cursor.execute("""select placeid from coredata.mv_Place group by PlaceID having COUNT(*) > 1
            #                                        """).fetchall()
        
            self.results['dup_placeid'] = cursor.execute("""select p.ObjectID, 
                                                    p.PlaceID,
                                                    pn.Name
                                                    from coredata.mv_Place p 
                                                    inner join (select placeid from coredata.mv_Place group by PlaceID having COUNT(*) > 1) pc on p.placeid = pc.placeid
                                                    inner join coredata.mv_PlaceName pn on pn.PlaceID = p.PlaceID""").fetchall()
                                                    
            # SRZ Not in Deployment database
            self.results['srz_deployment'] = cursor.execute("select SRZ from coredata.mv_Place where SRZ not in (select ESZ from openquery(CCD_READ,'select distinct ESZ from nzfs_deploy.deployment.ESZ where len(ESZ) = 8'))").fetchall()
        
        i = 2
        for k, v in self.results.iteritems():
            print k , v
            Tkinter.Label(self, text=k).grid(row=i, column=0, padx=1, pady=1, sticky='w')
            Tkinter.Label(self, text=len(v)).grid(row=i, column=1, padx=1, pady=1, sticky='w')
            my_btn_command = partial(self.fix_me, k)
            btn_fix_me = Tkinter.Button(self, text="Fix", command=my_btn_command)
            btn_fix_me.grid(row=i, column=2, padx=1, pady=1, sticky='w')
            i += 1

    def open_smartmap_callback(self, p):
        import webbrowser
        webbrowser.open_new(p)

    def fix_me(self, issue):
        print issue
                
        if issue == "cpn_no_address":
            with pyodbc.connect(self.root.con_string) as cnxn:
                cursor = cnxn.cursor()
                cursor.execute("""
                                update coredata.mv_PlaceAddress set PrimaryAddress = 1 where PrimaryAddress = 0 
                                and ObjectID in (select top 1 ObjectID from coredata.mv_PlaceAddress where PrimaryAddress = 0 and PlaceID not in (select PlaceID from coredata.mv_PlaceAddress where PrimaryAddress = 1))
                                """)
        elif issue == "cpn_no_name":
            with pyodbc.connect(self.root.con_string) as cnxn:
                cursor = cnxn.cursor()
                cursor.execute("""
                                update coredata.mv_PlaceName set PrimaryName = 1 where PrimaryName = 0 
                                and ObjectID in (select top 1 ObjectID from coredata.mv_PlaceName where PrimaryName = 0 and PlaceID not in (select PlaceID from coredata.mv_PlaceName where PrimaryName = 1)) 
                                """)
        elif issue == "cpn_multi_address":
            top = Tkinter.Toplevel(self)
            print self.results["cpn_multi_address"]
            
            headers = ['CPN ID', 'Address']
            buttons = [dict(text='SMART Map Link', function=lambda row: self.open_smartmap_callback(row[2]))]
            table_multi_address = table.Table(top, headers=headers, data=self.results["cpn_multi_address"], buttons=buttons)
            table_multi_address.pack()
                
        elif issue == "cpn_multi_name":
            top = Tkinter.Toplevel(self)
            print self.results["cpn_multi_name"]
            
            headers = ['CPN ID', 'CPN Name']
            buttons = [dict(text='SMART Map Link', function=lambda row: self.open_smartmap_callback(row[2]))]
            table_multi_address = table.Table(top, headers=headers, data=self.results["cpn_multi_name"], buttons=buttons)
            table_multi_address.pack()
            
        elif issue == "alarm_name_change":
            with pyodbc.connect(self.root.con_string) as cnxn:
                cursor = cnxn.cursor()
                cursor.execute("""
                               update coredata.mv_placealarm set alarmname = '' 
                                where placeid in (select pa.placeid 
                                    from coredata.mv_placealarm pa join (select * from coredata.mv_PlaceName where LastModified is not null and PrimaryName = 1) b on pa.PlaceID = b.placeid 
                                    where pa.AlarmName <> b.Name and pa.AlarmName <>'')
                                    """)
                cursor.execute("""
                                update coredata.mv_placealarm set alarmname = '' where PlaceID not in 
                                (select PlaceID from coredata.mv_PlaceName) and PFANumber not in ('999941','999940') """)

                
        elif issue == "panel_length":
            top = Tkinter.Toplevel(self)
            print self.results["panel_length"]
            
            headers = ['CPN ID', 'CPN Name']
            buttons = [dict(text='SMART Map Link', function=lambda row: self.open_smartmap_callback(row[2]))]
            table_multi_address = table.Table(top, headers=headers, data=self.results["panel_length"], buttons=buttons)
            table_multi_address.pack()
            
        elif issue == "dup_placeid":
            def dup_delete_callback(p):
                print p
                with pyodbc.connect(self.root.con_string) as cnxn:
                    cursor = cnxn.cursor()
                    cursor.execute("""
                                delete from coredata.mv_place
                                where objectid = ?
                                """, p)
                top.destroy()
            
            top = Tkinter.Toplevel(self)
            print self.results["dup_placeid"]
            
            headers = ['Object ID', 'CPN ID', 'CPN Name']
            buttons = [dict(text='Delete', function=lambda row: dup_delete_callback(row[0]))]
            table_multi_address = table.Table(top, headers=headers, data=self.results["dup_placeid"], buttons=buttons)
            table_multi_address.pack()
                    
        elif issue == "srz_deployment":
            import webbrowser
            srzs = '%0D%0A'.join(str(elem[0]) for elem in self.results['srz_deployment'])
            print srzs
            webbrowser.open_new('mailto:hock.oh@fire.org.nz?cc=james.burke@fire.org.nz&subject=CPN Delivery - SRZ not in deployment DB&body=Hi,%0D%0A%0D%0AThe following SRZ were NOT found in the Deployment DB%0D%0A' + srzs + '%0D%0A%0D%0ACheers,%0D%0A%0D%0A')
    
        
if __name__ == '__main__':
    root = Tkinter.Tk()
    main = CPN_Delivery_Check(root, 'test', None)
    main.pack(expand="true", fill="both")
    root.mainloop()