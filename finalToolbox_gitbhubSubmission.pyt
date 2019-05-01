import arcpy
import sys
import os

# Amazing little gem that overwrites shape file output - set to "False" to turn functionality off
arcpy.env.overwriteOutput = True

class Toolbox(object): # this is the toolbox itself - the 'red icon'
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Set of tools for final_v5"
        self.alias = "version 5 - version just prior to finalizing my last submission"

        # List of tool classes associated with this toolbox
        self.tools = [Extraction_Step_1, Extraction_Step_2, Extraction_file_report]


# This first tool identifies an Area of Interest (AOI) as a clipping feature, checks its validity, then proceeds
# to clip whatever the target species are. The AOI file must contain "AOI" in the name. It also checks to see if the
# output folders for this step and the output for the next tool (the merge) are created, and if they aren't,
# it creates them. Currently, the target species must be in a folder called "species".

class Extraction_Step_1(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 1 of extraction process: Clip"
        self.description = "This tool will use the existing AOI file to clip all target species. All species files " \
                           "must reside in a single folder together."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = []
        aoi_file = arcpy.Parameter(name="AOI_file",
                                   displayName="Area of interest file",
                                   datatype="DEShapefile",
                                   parameterType="Required",  # Required|Optional|Derived
                                   direction="Input",  # Input|Output
                                   )
        params.append(aoi_file)
        species_folder = arcpy.Parameter(name="Species_folder",
                                         displayName="Folder that contains the target species",
                                         datatype="DEWorkspace",
                                         parameterType="Required",  # Required|Optional|Derived
                                         direction="Input",  # Input|Output
                                         )
        params.append(species_folder)

        return params


    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        aoi_file = parameters[0].valueAsText
        species_folder = parameters[1].valueAsText

        arcpy.env.workspace = parameters[1].valueAsText

        arcpy.AddMessage("NOTE!... " + str(arcpy.env.workspace) + " is the extraction workspace.")
        # Set the spatial reference
        spRef = arcpy.SpatialReference(4326)  # 4326 == WGS 1984

        # Define the input directory, aka folder where shape files exist and output will go
        if not os.path.exists(os.path.join(arcpy.env.workspace, "clipOutput")):
            os.mkdir(os.path.join(arcpy.env.workspace, "clipOutput"))
            arcpy.AddMessage("Clipping output folder created")
        else:
            arcpy.AddMessage("Clipping output folder exists")

        if not os.path.exists(os.path.join(arcpy.env.workspace, "mergeOutput")):
            os.mkdir(os.path.join(arcpy.env.workspace, "mergeOutput"))
            arcpy.AddMessage("Merged output folder created")
        else:
            arcpy.AddMessage("Merged output folder exists")

        # setting up directory variables
        input_directory = species_folder
        clip_output_dir = os.path.join(arcpy.env.workspace, "clipOutput")

        # working in input_directory
        arcpy.env.workspace = input_directory
        arcpy.AddMessage("NOTE... " + input_directory + " is now the current workspace.")
        shp_files_all = arcpy.arcpy.ListFeatureClasses("*")

        # setting up to detect AOI polygon shape file within the shape files directory
        aoi_file = ""
        aoi_found = 0
        # looking for the AOI in the shape files. Alert if not present. Continue if present
        # and valid type (polygon, Geographic coordinate system)
        for i in shp_files_all:
            if "AOI" in i:
                aoi_found = 1
                aoi_file = i

        if aoi_found == 0:
            arcpy.AddMessage("NO AOI FILE FOUND...ADD AOI TO WORKSPACE!!!")
            sys.exit()
        else:
            arcpy.AddMessage("AOI found, inspecting file...")
            aoi_file_charac = arcpy.Describe(aoi_file)
            if (aoi_file_charac.shapeType == "Polygon") and (aoi_file_charac.spatialReference.type == "Geographic"):
                arcpy.AddMessage("Valid polygon found! Proceeding to clip species to AOI...")
            else:
                aoi_file_charac = arcpy.Describe(aoi_file)
                arcpy.AddMessage(
                    "ERROR: Need to provide a POLYGON for clipping, or existing polygon is in the wrong coordinate"
                    " system. See below:")
                arcpy.AddMessage("--- Selected AOI file type is " + aoi_file_charac.shapeType)
                arcpy.AddMessage(
                    "--- Current projection of selected AOI file is " + aoi_file_charac.spatialReference.type)
                sys.exit()

        # Clipping the AOI (extraction area) from each individual species file, makes sure only to incorporate species
        # by looking for month name - ignoring the AOI file.
        for shp in shp_files_all:
            if ("spring" in shp) or ("fall" in shp):
                arcpy.AddMessage("processing file: " + shp)
                arcpy.Clip_analysis(shp, aoi_file, os.path.join(clip_output_dir, shp + "_clip"), "")

        arcpy.AddMessage("All species successfully clipped")

# This tool takes the output of the clipping tool and merges everything into a single "extraction".  This extraction
# goes on to be the modeling input for NAEMO (Navy Acoustic Effects Model).

class Extraction_Step_2(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 2 of extraction process: Merge"
        self.description = "This tool will merge the clipped species into a single shape file, the result of which " \
                           "is the final extraction.  Make sure to run the extraction check tool (3rd tool in box.)"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = []
        clipped_input = arcpy.Parameter(name="clipped_input",
                                        displayName="The individual species that were previously clipped",
                                        datatype="DEWorkspace",
                                        parameterType="Required",  # Required|Optional|Derived
                                        direction="Input",  # Input|Output
                                        )
        params.append(clipped_input)
        merged_output = arcpy.Parameter(name="merged_output",
                                        displayName="Folder that will contain the merged data (the extraction)",
                                        datatype="DEFolder",
                                        parameterType="Required",  # Required|Optional|Derived
                                        direction="Input",  # Input|Output
                                        )
        params.append(merged_output)
        return params


    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        clipped_input = parameters[0].valueAsText
        merged_output = parameters[1].valueAsText

        arcpy.env.workspace = clipped_input

        list_feature_classes = arcpy.ListFeatureClasses("*")

        arcpy.AddMessage("NOTE!...Final merged output will reside in: " + str(merged_output))
        arcpy.AddMessage("Merging... " + str(len(list_feature_classes)) + " files..")
        arcpy.Merge_management(list_feature_classes, os.path.join(merged_output, "All_species_merge.shp"))
        arcpy.AddMessage("Merge successfully completed")
        arcpy.AddMessage("Extraction is ready.")

# The third and final tool serves as a QAQC method, so the user can make sure that extraction is the correct file type,
# correct projection, and correct coordinate system. If a extraction of any type aside from NAD83 WGS84 goes into
# NAEMO Web, it will product incorrect results, but the NAEMO program itself does not perform any of these checks
# itself, so it is incumbent upon the GIS side to make sure everything is kosher.

class Extraction_file_report(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Step 3: Extraction evaluation report"
        self.description = "To be used to determine whether the extraction is valid for modeling input. " \
                           "Checks file type and coordinate system."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = []
        input_file = arcpy.Parameter(name="input_file",
                                     displayName="Step 3: Extraction to be evaluated",
                                     datatype="DEShapefile",
                                     parameterType="Required",  # Required|Optional|Derived
                                     direction="Input",  # Input|Output
                                     )
        params.append(input_file)
        return params


    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""


        def describe_shp(input_shapefile):
            desc = arcpy.Describe(input_shapefile)
            arcpy.AddMessage(("Describing: " + str(input_shapefile)))
            if arcpy.Exists(input_shapefile):
                if desc.dataType == "ShapeFile":
                    arcpy.AddMessage(("Feature Type:  " + desc.shapeType))
                    arcpy.AddMessage(("Coordinate System Type:  " + desc.spatialReference.type))
                    arcpy.AddMessage(("Coordinate System used:  " + desc.spatialReference.GCSName))

                else:
                    arcpy.AddMessage(("Input data not ShapeFile.."))
            else:
                arcpy.AddMessage(("Dataset not found, please check the file path.."))

        input_shapefile = parameters[0].valueAsText
        describe_shp(input_shapefile)
        return
