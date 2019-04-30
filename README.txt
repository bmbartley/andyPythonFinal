# andyPythonFinal
The fruits of my labor

This tool performs a "density extraction" on marine species data, which creates a single shape file that will be used as modeling input in NAEMO (Navy Acoustic Effects Model).  It is a three step process which first performs some directory and data checks, creates the necessary folders if they are not present, and then clips the target species data by an existing area of interest (AOI) file.  Then the third and final tool checks over the data to make sure it is the correct file type and in the proper coordinate system.  

# The first tool identifies an Area of Interest (AOI) as a clipping feature, checks its validity, then proceeds
# to clip whatever the target species are. The AOI file must contain "AOI" in the name. It also checks to see if the
# output folders for this step and the output for the next tool (the merge) are created, and if they aren't,
# it creates them. Currently, the target species must be in a folder called "species".

# The second tool takes the output of the clipping tool and merges everything into a single "extraction".  This extraction
# goes on to be the modeling input for NAEMO (Navy Acoustic Effects Model).

# The third and final tool serves as a QAQC method, so the user can make sure that extraction is the correct file type,
# correct projection, and correct coordinate system. If a extraction of any type aside from NAD83 WGS84 goes into
# NAEMO Web, it will product incorrect results, but the NAEMO program itself does not perform any of these checks
# itself, so it is incumbent upon the GIS side to make sure everything is kosher.
