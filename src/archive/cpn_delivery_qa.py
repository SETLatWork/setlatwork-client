'''
Created on 7/05/2014

@author: burkej
'''
import Tkinter
import logging
import pyodbc
from functools import partial
import webbrowser

import stsrc.models.table as table

log = logging.getLogger(__package__)

class CPN_Delivery_QA(Tkinter.Frame):
    def __init__(self, root, *args, **kwargs):
        
        Tkinter.Frame.__init__(self, root, *args, **kwargs)
        self.root = root
                
        btn_refresh = Tkinter.Button(self, text="Refresh", command=self.display_qa)
        btn_refresh.grid(row=0, column=1, padx=1, pady=1)
        
        self.display_qa()
        
    def display_qa(self):
        with pyodbc.connect(self.root.con_string) as cnxn:
            cursor = cnxn.cursor()
            
            # Number of CPN's requiring QA
            cpn_qa = cursor.execute("""
                                    select cr.ChangeRequestID,
                                    cr.UserName,
                                    Datediff(dd,Submitted,GETDATE()) Days,
                                    convert(varchar,GETDATE()-Submitted,108) Hours,
                                    cr.LastModified,
                                    cr.Submitted,
                                    case 
                                    when PFANumber is not null then 'Y'
                                    else 'N'
                                    end as Alarmed,
                                    'http://fireportal.fire.org.nz/site/smartchange/Lists/SMART%20Change%20Requests/All%20Items.aspx?FilterField1=RequestID&FilterValue1='+cast(ChangeRequestID as varchar) SharepointLink
                                    from coredata.CHANGEREQUEST cr 
                                    left outer join NZFS_Lookup.coredata.STATUS s on cr.StatusID = s.StatusID
                                    outer apply (select top 1 pa.PlaceID, pa.PFANumber from coredata.mv_PlaceAlarm pa where pa.PlaceID = cr.PlaceID) as pa
                                    where qausername is null
                                    order by Alarmed desc, 4 desc, 5 desc
                                    """).fetchall()
        
        def open_link_callback(p):
            #import webbrowser
            webbrowser.open_new(p)
        
        headers = ['CR ID', 'User Name', 'Days Active', 'Hours Active', 'Last Modified', 'Submitted', 'Alarmed?']
        buttons = [dict(text='SMART Change', function=lambda row: open_link_callback(row[6])),
                   dict(text='SMART Map', function=lambda row: open_link_callback(row[7]))]
        change_request_qa = table.Table(self, headers=headers, data=cpn_qa, buttons=buttons, pagination=20)
        change_request_qa.grid(row=1, column=1, padx=1, pady=1)
        
if __name__ == '__main__':
    pass