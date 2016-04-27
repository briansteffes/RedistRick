# Brian P. Steffes
# April 23, 2016
# The Ohio State University
# Geog5223: GIS Design and Implementation

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import arcpy
from arcpy import env


# Custom Functions:
# ------------------------------------------------------------------------------------


# Custom Function 1: numDistricts(featureclass), returns integer
# returns and integer representing the number of districts
# assigned in a feature class with attribute Dist_ID.
# Districts are numbered 1 to n
def numDistricts(infc):
        field_values = []
        rows = arcpy.SearchCursor(infc, fields="Dist_ID")
        for row in rows:
            instance = row.getValue("Dist_ID")
            field_values.append(instance)

        value_set = set(field_values)
        present_values = list(value_set)
        return len(present_values)

# --------------------------------------------------------------------------------------


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Redistricting Toolbox"
        # List of tool classes associated with this toolbox
        self.tools = [Add_Integer_Field_Tool,
                      Split_Layer_Tool,
                      Build_Districts_Tool]



class Add_Integer_Field_Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Update District ID"
        self.description = "Enter integer value for the district that will be assigned to selected features"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Census Tract Layer (Or other polygon layer with population data that needs to be aggregated)
        param0 = arcpy.Parameter(
            displayName="Input Feature Class",
            name="in_feature",
            datatype= ["GPFeatureLayer", "GPString"],
            parameterType="Required",
            direction="Input")

        # Read the directory of infc from temp.txt file
        f = open(r'temp.txt','r')
        param0.value = f.readline()                         # Not sure if '\n' appended will cause a problem

        # Name of Field to be Added
        # Ideally the datatype would be 'Field' and the parameter would be dependent to
        #   param0. If param0 does not have the appropriate attribute then the tool will add one automatically
        param1 = arcpy.Parameter(
            displayName="District ID Field",
            name="district_field",
            datatype="Field",
            parameterType="Optional",                       # if not provided then execute block add "Dist_ID" Field of type Long
            direction="Input")

        param1.parameterDependencies = [param0.name]
        param1.filter.list = ["FID","LONG","DOUBLE"]
        param1.value = 'N/A'                               # Default to Identify no existing field, If user does not change then create new field

        # District Number
        param2 = arcpy.Parameter(
            displayName="Field Integer Value",
            name="field_value",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")

        # allow only normal numbers
        param2.filter.type = "Range"
        param2.filter.list = [1,100]                        # Hard coded upper bound, but should be derived from the number of polygons in param0.
        param2.value = 0

        # list of parameters for tool
        parameters = [param0, param1, param2]
        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def execute(self, parameters, messages):
        # Access the parameters: (Returns values as stringtypes)
        infc = parameters[0].valueAsText
        field_name = parameters[1].valueAsText
        field_value = int(parameters[2].valueAsText)
        self.run(infc, field_name, field_value)

    def run(self, infc, field_name, field_value):
        # -----------------------------------------------------------------
        # Frequently Used Variables
        infc_dir = os.path.split(arcpy.Describe(infc).catalogPath)[0]
        infc_name = arcpy.Describe(infc).file
        # -----------------------------------------------------------------

        # define the workspace using the path name of the input feature class
        env.workspace = infc_dir

        # Add field if the parameter was left blank
        # Add Field to the Feature Class

        if field_name == 'N/A':
            try:
                field_name = 'Dist_ID'
                arcpy.management.AddField(infc_name, field_name, "LONG")
            except arcpy.ExecuteError:
                print arcpy.GetMessages(2)

        # Populate the Field
        mxd = arcpy.mapping.MapDocument("CURRENT")
        layers = arcpy.mapping.ListLayers(mxd)
        selected_lyr = []
        for layer in layers:
            fids = arcpy.Describe(layer).FIDSet
            if len(fids) > 0:
                selected_lyr.append(layer)

        # Only deal with the first selected layer in array if user has made
        # Selections across multiple layers

        # TODO: Error message for selecting from multiple .lyr files.

        desc = arcpy.Describe(selected_lyr[0])
        fids = [int(s) for s in (desc.FIDSet.split("; "))]

        rows = arcpy.UpdateCursor(infc_name)

        for row in rows:
            if int(row.getValue("FID")) in fids:
                row.setValue(field_name, field_value)
                rows.updateRow(row)

        # Prevent locks on the layer
        del row
        del rows
# Tool to Select Features by Attribute and create a new feature class from them

class Split_Layer_Tool(object):
    def __init__(self):
        """Define the tool"""
        self.label = "Split Layer"
        self.description = "Creates new features based on an attribute value"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Input Feature Class
        param0 = arcpy.Parameter(
            displayName="Input Feature Class",
            name="in_feature",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")

        # only accept Polygon Feature Class
        param0.filter.list = ["Polygon"]

        # Field Selection is Based off of
        param1 = arcpy.Parameter(
            displayName="Field Name",
            name="field_name",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        param1.parameterDependencies = [param0.name]
        param1.filter.list = ["LONG", "SHORT"]

        # Outpath
        param2 = arcpy.Parameter(
            displayName="Output Folder",
            name="field_value",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")

        # list of parameters for tool
        parameters = [param0, param1, param2]
        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def execute(self, parameters, messages):

        infc = parameters[0].valueAsText
        field = parameters[1].valueAsText
        infc_dir = arcpy.Describe(infc).catalogPath
        infc_name = arcpy.Describe(infc).file

        env.workspace = infc_dir
        # Isolate the range of values in present_values list
        field_values = []
        rows = arcpy.SearchCursor(infc_dir, fields="Dist_ID")
        for row in rows:
            instance = row.getValue("Dist_ID")
            field_values.append(instance)

        value_set = set(field_values)
        present_values = list(value_set)

        # Make a Layer from the Feature Class
        arcpy.management.MakeFeatureLayer(infc_name, 'lyr')

        # Select based off attribute value and make a new feature class
        # that is stored in Results folder.
        for i in present_values:
            arcpy.management.SelectLayerByAttribute('lyr',
                                                    "NEW_SELECTION",
                                                    '"Dist_ID" = ' + str(i))
            arcpy.management.CopyFeatures("lyr", os.path.join(
                                          os.path.split(infc_dir)[0],
                                          "district_" + str(i)))

        return True


# This builds districts based off of an attribute, Dist_ID.
# Returns a field class of joined District Polygons


class Build_Districts_Tool(object):
    def __init__(self):
        """Define the tool"""
        self.label = "Build Districts"
        self.description = "Create District Polygons from Dist_ID attribute"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Input Feature Class
        param0 = arcpy.Parameter(
            displayName="Input Feature Class",
            name="in_feature",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")

        # only accept Polygon Feature Class
        param0.filter.list = ["Polygon"]

        # Name of Field to be Added
        param1 = arcpy.Parameter(
            displayName="Field Name",
            name="field_name",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        param1.parameterDependencies = [param0.name]
        param1.filter.list = ["LONG", "SHORT"]

        # Outpath
        param2 = arcpy.Parameter(
            displayName="Output Folder",
            name="field_value",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")

        # list of parameters for tool
        parameters = [param0, param1, param2]
        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def execute(self, parameters, messages):
        infc = parameters[0].valueAsText
        outfc = parameters[2].valueAsText
        self.run(infc, outfc)

    def run(self, infc, outfc):
        env.workspace = os.path.split(infc)[0]

        n = numDistricts(infc)

        # Create Layer from id (default layer name is lyr)
        arcpy.management.MakeFeatureLayer(infc, "lyr")
        # Dissolve layer
        arcpy.management.Dissolve(infc, outfc, "Dist_ID")
        # add dissolveed layer to district_layers array

        # join all members of district_layers array
        # use copy feature management toool to create a new feature class
        # that is held under outfc.
