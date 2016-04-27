import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import arcpy
from arcpy import env
from arcpy import mapping
import pythonaddins
import imp
imp.load_source('RedistrictingToolbox',
                os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'Redistricting.pyt'))
from RedistrictingToolbox import *

def ensure_dist_id(infc):
    if field_exists(infc, 'Dist_ID') is False:
        create_dist_id(infc)
        return False
    return True

def field_exists(infc, name):
   fieldList = arcpy.ListFields(infc)
   for field in fieldList:
      if field.name == name:
         return True
   return False

def create_dist_id(infc):
    add_id = Add_Integer_Field_Tool()
    add_id.run(infc, 'N/A', 1)

def GetSelectedLayers(return_layer=False):
    # TODO set infc properly based on the selected feature input layer
    # Iterate through all of the layers present in the mxd file

    mxd = mapping.MapDocument("CURRENT")
    layers = mapping.ListLayers(mxd)
    selected_lyr = []
    for layer in layers:
        name = layer.name
        desc = arcpy.Describe(name)
        selected_FID = desc.FIDSet
        if len(selected_FID) > 0:
            if return_layer is True:
                return layer
            else:
                selected_lyr.append(layer.dataSource)

    return selected_lyr

def updateSymbolization():
    lyr = GetSelectedLayers(return_layer=True)
    if lyr.symbologyType == "UNIQUE_VALUES":
      lyr.symbology.valueField = "Dist_ID"
      lyr.symbology.addAllValues()
    arcpy.RefreshActiveView()
    arcpy.RefreshTOC()

class SummaryButon(object):
    """Implementation for DSaddin_district.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        infc = (GetSelectedLayers())[0]
        ensure_dist_id(infc)

        script = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "result_dialog.py")
        os.system("python " + script + " \"" + infc + "\" 1>log.txt 2>&1")


class DistrictButon(object):
    """Implementation for DSaddin_district.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        # If features selected from multiple layers only the first one is addressed by script.
        infc = (GetSelectedLayers())[0]
        if ensure_dist_id(infc):
            add_id = Add_Integer_Field_Tool()
            add_id.run(infc, 'Dist_ID', numDistricts(infc))
        updateSymbolization()
