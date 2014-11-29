'''
Created on 16/05/2014

@author: BurkeJ
'''

import Tkinter, ttk
import logging
import pyodbc
from functools import partial
import arcpy
import datetime
import os

#import stsrc.models.tab as tab

log = logging.getLogger(__package__)

class FSS_Update(): # tab.Tab
    def __init__(self): # , root, name, *args, **kwargs
        
        #tab.Tab.__init__(self, root, name)
        
        # Initialise variables for datetime stamp
        d = datetime.datetime.now()
        dt = d.strftime("%Y%m%d")
        
        self.WorkDir = "P:\ICTS\DSA\SpatialData\FireSeasonStatus\\"
        self.FireSeasonStatus_gdb = "FSS_%s.gdb" % dt
        self.FireSeasonStatus = self.WorkDir+self.FireSeasonStatus_gdb+"\\FSS"
        self.DBConnection = self.WorkDir+"\\GeoDB.sde"
        
        arcpy.env.workspace = self.WorkDir+self.FireSeasonStatus_gdb 
        
    def update(self):
        """
        if os.path.exists(os.path.join(self.WorkDir, self.FireSeasonStatus_gdb)):
            arcpy.Delete_management(os.path.join(self.WorkDir, self.FireSeasonStatus_gdb))
        
        print("Process: Create Fire Season Status File GDB")
        arcpy.CreateFileGDB_management(self.WorkDir, self.FireSeasonStatus_gdb)
        
        print("Process: Create Base Feature Dataset")
        arcpy.CreateFeatureDataset_management(os.path.join(self.WorkDir, self.FireSeasonStatus_gdb), "FSS", "PROJCS['NZGD_2000_New_Zealand_Transverse_Mercator',GEOGCS['GCS_NZGD_2000',DATUM['D_NZGD_2000',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',1600000.0],PARAMETER['False_Northing',10000000.0],PARAMETER['Central_Meridian',173.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]];-4020900 1900 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision")
        
        #
        # Fire Jurisdiction
        #
        print("FJ: Create Feature Class - FireJurisdiction")
        FireJurisdiction = self.DBConnection+"\\nzfs_core.COREDATA.NZFSDerived\\nzfs_core.COREDATA.FireJurisdiction"
        arcpy.FeatureClassToFeatureClass_conversion(FireJurisdiction, self.FireSeasonStatus, "FJ1")
        
        print("FJ: Make modifications to FireJurisdiction")
        arcpy.AddField_management("FSS\\FJ1", "FireAuthorityType", "TEXT", "", "", "50", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management("FSS\\FJ1", "FireAuthorityName", "TEXT", "", "", "100", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management("FSS\\FJ1", "FireAuthoritySubArea", "TEXT", "", "", "50", "", "NULLABLE", "NON_REQUIRED", "")
        #arcpy.AddField_management("FSS\\FJ1", "SubAreaSource", "TEXT", "", "", "50", "", "NULLABLE", "NON_REQUIRED", "")
        #arcpy.AddField_management("FSS\\FJ1", "SubAreaSourceDate", "TEXT", "", "", "50", "", "NULLABLE", "NON_REQUIRED", "")
        #arcpy.AddField_management("FSS\\FJ1", "Note", "TEXT", "", "", "200", "", "NULLABLE", "NON_REQUIRED", "")
        #arcpy.AddField_management("FSS\\FJ1", "StatusConstraints", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        #arcpy.AddField_management("FSS\\FJ1", "StatusCode", "TEXT", "", "", "50", "", "NULLABLE", "NON_REQUIRED", "")
        
        print("FJ: Apply Field Calculator Changes")
        arcpy.CalculateField_management("FSS\\FJ1", 'FireAuthorityType', '!JurisdictionType!', 'PYTHON', '#')
        
        arcpy.MakeFeatureLayer_management("FSS\\FJ1", "tempLayer1")
        
        arcpy.SelectLayerByAttribute_management("tempLayer1", "NEW_SELECTION", "\"FireAuthorityType\" = 'TLA'")
        arcpy.CalculateField_management("tempLayer1", 'FireAuthorityName', '!AuthorityName! + " Council"', 'PYTHON', '#')
        
        arcpy.SelectLayerByAttribute_management("tempLayer1", "NEW_SELECTION", "\"FireAuthorityType\" = 'RFD' AND \"AuthorityName\" IN ('Burnham Defence', 'Linton Military Camp Defence', 'Ohakea Defence', 'Raumai Defence', 'Tekapo Military Training Area Defence', 'West Melton', 'Woodbourne Defence')")
        arcpy.CalculateField_management("tempLayer1", 'FireAuthorityName', '"New Zealand Defence Force"', 'PYTHON', '#')
        arcpy.CalculateField_management("tempLayer1", 'FireAuthoritySubArea', '!AuthorityName!', 'PYTHON', '#')
        arcpy.CalculateField_management("tempLayer1", 'FireAuthorityType', '"Defence"', 'PYTHON', '#')
        
        arcpy.SelectLayerByAttribute_management("tempLayer1", "NEW_SELECTION", "\"FireAuthorityType\" = 'RFD'")
        arcpy.CalculateField_management("tempLayer1", 'FireAuthorityName', '!AuthorityName! + " Rural Fire District"', 'PYTHON', '#')
        
        arcpy.SelectLayerByAttribute_management("tempLayer1", "NEW_SELECTION", "\"FireAuthorityType\" = 'DOC'")
        arcpy.CalculateField_management("tempLayer1", 'FireAuthorityName', '"Department of Conservation"', 'PYTHON', '#')
        arcpy.CalculateField_management("tempLayer1", 'FireAuthoritySubArea', '!AuthorityName!', 'PYTHON', '#')
        
        arcpy.SelectLayerByAttribute_management("tempLayer1", "NEW_SELECTION", "\"FireAuthorityType\" = 'UFD'")
        arcpy.CalculateField_management("tempLayer1", 'FireAuthoritySubArea', '!AuthorityName!', 'PYTHON', '#')
        
        arcpy.SelectLayerByAttribute_management("tempLayer1", "CLEAR_SELECTION")
        arcpy.CopyFeatures_management("tempLayer1", "FSS//FJ2")
        
        print("FJ: Remove unneeded fields")
        arcpy.DeleteField_management("FSS\\FJ2", "AuthorityName")
        arcpy.DeleteField_management("FSS\\FJ2", "JurisdictionID")
        arcpy.DeleteField_management("FSS\\FJ2", "JurisdictionType")
        arcpy.DeleteField_management("FSS\\FJ2", "LastModified")
        arcpy.DeleteField_management("FSS\\FJ2", "LastModifiedUser")
        arcpy.DeleteField_management("FSS\\FJ2", "SHAPE_STArea__")
        arcpy.DeleteField_management("FSS\\FJ2", "SHAPE_STLength__")
        
        #
        # TLA
        #
        print("TLA: Feature Class to Feature Class - TLA")
        TLA_DB = self.DBConnection+"\\nzfs_core.COREDATA.StatisticsNZ\\nzfs_core.COREDATA.TerritorialAuthority"
        arcpy.FeatureClassToFeatureClass_conversion(TLA_DB, self.FireSeasonStatus, "TLA")
        
        arcpy.AddField_management("FSS\\TLA", "FireAuthorityNameUFD", "TEXT", "", "", "100", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management("FSS\\TLA", 'FireAuthorityNameUFD', '!TerritorialAuthorityName! + " Council"', 'PYTHON', '#')
        arcpy.DeleteField_management("FSS\\TLA", "TerritorialAuthorityId")
        arcpy.DeleteField_management("FSS\\TLA", "TerritorialAuthorityName")
        arcpy.DeleteField_management("FSS\\TLA", "TerritorialAuthorityCode")
        arcpy.DeleteField_management("FSS\\TLA", "SHAPE_STArea__")
        arcpy.DeleteField_management("FSS\\TLA", "SHAPE_STLength__")
        
        
        #
        # Merge Fire Jurisdiction UFD and TLA
        #
        print("Merge (FJ,UFD,TLA): Intersect modified FireJurisdiction with modified TLA")
        arcpy.MakeFeatureLayer_management("FSS\\FJ2", "tempLayer2")
        arcpy.SelectLayerByAttribute_management("tempLayer2", "NEW_SELECTION", "\"FireAuthorityType\" = 'UFD'")
        arcpy.Intersect_analysis(["tempLayer2", "FSS\\TLA"], "FSS\\FJ_UFD1", "NO_FID", "0.5 Meters", "INPUT")
        
        arcpy.CalculateField_management("FSS\\FJ_UFD1", 'FireAuthorityName', '!FireAuthorityNameUFD!', 'PYTHON', '#')
        arcpy.DeleteField_management("FSS\\FJ_UFD1", "FireAuthorityNameUFD")
        
        
        #arcpy.DeleteField_management("FSS\\FJ_UFD1", "SHAPE_STArea__")
        #arcpy.DeleteField_management("FSS\\FJ_UFD1", "SHAPE_STLength__")
        
        #arcpy.SelectLayerByAttribute_management("tempLayer1", "CLEAR_SELECTION")
        #arcpy.CopyFeatures_management("tempLayer1", "FSS//FJ2")
        
        print("Merge (FJ,UFD,TLA): Erase UFD Areas from FireJurisdiction")
        arcpy.SelectLayerByAttribute_management("tempLayer2", "NEW_SELECTION", "\"FireAuthorityType\" = 'UFD'")
        arcpy.DeleteFeatures_management("tempLayer2")
        arcpy.RepairGeometry_management("FSS\\FJ2", "DELETE_NULL")
        arcpy.Integrate_management("FSS\\FJ2", "")
        
        print("Merge (FJ,UFD,TLA): Merge new UFD areas into FireJurisdiction")
        arcpy.Merge_management(["FSS//FJ2", "FSS\\FJ_UFD1"], "FSS\\FJ4", "")
        arcpy.DeleteField_management("FSS\\FJ4", "AuthorityName")
        
        #arcpy.MakeFeatureLayer_management("FSS\\FJ1", "tempLayer3")
        #arcpy.SelectLayerByAttribute_management("tempLayer3", "NEW_SELECTION", "\"FireAuthorityName\" IN ( 'Ashburton District Council', 'Auckland Council', 'Central Otago District Council', 'Christchurch City Council', 'Clutha District Council', 'Dunedin City Council', 'Far North District Council', 'Gisborne District Council', 'Gore District Council', 'Kapiti Coast District Council', 'Lower Hutt City Council', 'Manawatu District Council', 'Marlborough District Council', 'Napier City Council', 'New Plymouth District Council', 'Palmerston North City Council', 'Queenstown-Lakes District Council', 'South Wairarapa District Council', 'Southland District Council', 'Stratford District Council', 'Tararua District Council', 'Tauranga City Council', 'Thames-Coromandel District Council', 'Timaru District Council', 'Waikato District Council', 'Waimate District Council', 'Waipa District Council', 'Wairoa District Council', 'Wanganui District Council', 'Wellington City Council', 'Whakatane District Council' )")
        #arcpy.CalculateField_management("tempLayer3", 'Note', '"Check local authority bylaw"', 'PYTHON', '#')
        
        
        #
        # CAB
        #
        #Locality_gdb = "P:\ICTS\DSA\SpatialData\NZLocalities\NZ Localities Extracts\NZLocalities.gdb" 
        #LocalityCoast = Locality_gdb+"\\LocalitiesDerived\\Coast"
        
        print("CAB: Create Feature Class - CAB")
        CAB = self.WorkDir+"\\CAB.gdb\\CAB\\CAB_cleaned"
        arcpy.FeatureClassToFeatureClass_conversion(CAB, self.FireSeasonStatus, "CAB")
        
        #print("CAB: Clip CAB Areas to Coast")
        #arcpy.Clip_analysis("FSS\\CAB", LocalityCoast, "FSS\\CAB_Clip", "")
        
        #
        # FSS
        #
        print("FSS: Union FireJurisdiction and CAB Areas")
        arcpy.MakeFeatureLayer_management("FSS\\FJ4", "tempLayer4")
        arcpy.SelectLayerByAttribute_management("tempLayer4", "NEW_SELECTION", "\"FireAuthorityType\" IN ('TLA','RFD')")
        arcpy.Union_analysis(["tempLayer4", "FSS\\CAB"], "FSS\\FJ5", "NO_FID")
        arcpy.SelectLayerByAttribute_management("tempLayer4", "NEW_SELECTION", "\"FireAuthorityType\" NOT IN ('TLA','RFD')")
        
        arcpy.Merge_management(["FSS//FJ5", "tempLayer4"], "FSS\\FSS1", "")
        
        #arcpy.SelectLayerByAttribute_management("tempLayer4", "CLEAR_SELECTION")
        #arcpy.CopyFeatures_management("tempLayer4", "FSS//FSS1")
        
        print("FSS: Reassign FireAuthoritySubArea")
        arcpy.MakeFeatureLayer_management("FSS\\FSS1", "tempLayer5")
        #arcpy.SelectLayerByAttribute_management("tempLayer4", "NEW_SELECTION", "\"FireAuthorityName\" = ''")
        #arcpy.DeleteFeatures_management("tempLayer4")
        arcpy.SelectLayerByAttribute_management("tempLayer5", "NEW_SELECTION", "\"FireAuthorityName\" = \"FireAuthorityName_1\"")
        arcpy.CalculateField_management("tempLayer5", 'FireAuthoritySubArea', '!FireAuthoritySubArea_1!', 'PYTHON', '#')
        
        print("FSS: Assign StatusCodes")
        arcpy.SelectLayerByAttribute_management("tempLayer5", "NEW_SELECTION", "\"FireAuthorityType\" = 'UFD'")
        arcpy.CalculateField_management("tempLayer5", 'StatusCode', '"Z"', 'PYTHON', '#')
        arcpy.SelectLayerByAttribute_management("tempLayer5", "NEW_SELECTION", "\"StatusCode\" = ''")
        arcpy.CalculateField_management("tempLayer5", 'StatusCode', '"O"', 'PYTHON', '#')
        
        arcpy.SelectLayerByAttribute_management("tempLayer5", "CLEAR_SELECTION")
        arcpy.CopyFeatures_management("tempLayer5", "FSS//FSS2")
        
        print("FSS: Dissolve FSS by FireAuthority Name/Type/SubArea")
        arcpy.Dissolve_management("FSS\\FSS2", "FSS\\FSS3", "FireAuthorityName;FireAuthoritySubArea", "FireAuthorityType FIRST;SubAreaSource FIRST;SubAreaSourceDate FIRST;Note FIRST;StatusConstraints FIRST;StatusCode FIRST", "MULTI_PART", "DISSOLVE_LINES")
        
        
        arcpy.MakeFeatureLayer_management("FSS\\FSS3", "tempLayer6")
        arcpy.SelectLayerByAttribute_management("tempLayer6", "NEW_SELECTION", "\"FireAuthorityName\" = ''")
        arcpy.DeleteFeatures_management("tempLayer6")
        arcpy.SelectLayerByAttribute_management("tempLayer6", "CLEAR_SELECTION")
        arcpy.CopyFeatures_management("tempLayer6", "FSS//FSS4")
        
        print("FSS: Repairing Geometries and remove slivers/gabs")
        arcpy.RepairGeometry_management("FSS\\FSS4", "DELETE_NULL")
        arcpy.Integrate_management("FSS\\FSS4", "1 Meters")
        """
        
        #
        # Update Status Codes
        #
        arcpy.MakeFeatureLayer_management("FSS\\FSS4", "tempLayer7")
        with pyodbc.connect("DRIVER={SQL Server};SERVER=sv-gis-sql1;DATABASE=NZFS_core;Trusted_Connection=True") as cnxn:
            cursor = cnxn.cursor()
            current_fss = cursor.execute("select FireAuthorityName, CASE WHEN FireAuthoritySubArea IS NOT NULL THEN FireAuthoritySubArea ELSE '' END, StatusCode from coredata.fireseasonstatus").fetchall()
        
        for record in current_fss:
            print record
            arcpy.SelectLayerByAttribute_management("tempLayer7", "NEW_SELECTION", "\"FireAuthorityName\" = '%s' AND \"FireAuthoritySubArea\" = '%s'" %(record[0].replace("'","''"), record[1].replace("'","''")))
            arcpy.CalculateField_management("tempLayer7", 'FIRST_StatusCode', "'%s'" % record[2], 'PYTHON', '#')
            
        
        """
        # Create and validate no gaps topology
        #FJ_Topology = "\\FSS_Topology"
        
        # Process: Create Topology
        arcpy.CreateTopology_management("FSS", "FSS_Topology", "")
        
        # Process: Add Feature Class To Topology
        arcpy.AddFeatureClassToTopology_management("FSS\\FSS_Topology", "FSS4", "1", "1")
        
        # Process: Add Rule To Topology
        arcpy.AddRuleToTopology_management("FSS\\FSS_Topology", "Must Not Overlap (Area)", "FSS4", "", "", "")
        
        # Process: Validate Topology
        arcpy.ValidateTopology_management("FSS\\FSS_Topology", "Full_Extent")
        """

if __name__ == '__main__':
    print "Started: %s" % datetime.datetime.now().strftime("%Y%m%d %H:%M")
    #root = Tkinter.Tk()
    main = FSS_Update() #(root, 'FSS Update')
    main.update()
    print "Finished %s" % datetime.datetime.now().strftime("%Y%m%d %H:%M")
    #main.pack(expand="true", fill="both")
    #root.mainloop()