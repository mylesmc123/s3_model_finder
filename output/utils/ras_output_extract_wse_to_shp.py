#*************************************************************************************
#-------This script exports 2D Flow area polygons & WSE results for each Timestep
#-------Cross-section (XS) polylines and WSE results are also exported to shapefile
#-------HDF format must be developed from Hec-RAS 6.0 Beta 3---------------------


import os
import shutil

import numpy as np
import h5py
import shapefile
import time
# from osgeo import ogr, gdal, osr
from osgeo import ogr
# import geopandas as gpd

# import utils.ras_output_wse_shp_to_nc

#-------------Delete Temp Directory--------
def tempDirSweep(tempDir):
    if not os.path.exists(tempDir):
        os.makedirs(tempDir)

    for f in os.listdir(tempDir):
        file_object_path = os.path.join(tempDir, f)
        if os.path.isfile(file_object_path):
            os.unlink(file_object_path)
        else:
            shutil.rmtree(file_object_path)
    return None
#------------------------------------------

#******Create/Sweep temp folder***
# tempDirSweep(tempDir)
#***********************************

# Simply gets the names of the 2D Flow Areas in the Plan's geometry
def get2DAreaNames(hf):
    hdf2DFlow = hf['Results']['Unsteady']['Geometry Info']['2D Area(s)']
    AreaNames = []
    for key in hdf2DFlow:
        if key in ['Cell Spacing', "Manning's n", 'Names', 'Tolerances']:
            continue
        else:
            AreaNames.append(key)  # List of 2D Area names
    return AreaNames


def get2DArea_cellcenter_pts(curr_2DArea, hf):
    hdf2DFlow_geo = hf['Geometry']['2D Flow Areas']
    dataset = hdf2DFlow_geo[curr_2DArea]['Cells Center Coordinate']
    data_list = np.zeros((2,), dtype='float64')
    data_list = np.array(dataset).tolist()
    # print(data_list)
    return data_list


def get2DCells_min_elev(curr_2DArea, hf):
    hdf2DFlow_geo = hf['Geometry']['2D Flow Areas']
    dataset = hdf2DFlow_geo[curr_2DArea]['Cells Minimum Elevation']
    # print (dataset)
    #data_list = np.zeros([1, ], dtype='float64')
    data_list = np.array(dataset).tolist()
    return data_list


def get2DArea_wse_data(curr_2DArea, hf):
    hdf2DFlow_wse_data = hf['Results']['Unsteady']['Output']['Output Blocks'] \
        ['Base Output']['Unsteady Time Series']['2D Flow Areas']

    dataset = hdf2DFlow_wse_data[curr_2DArea]['Water Surface']

    # data_list = np.zeros((timesteps,), dtype='float64')
    # dataset.read_direct(data_list, np.s_[0:timesteps,], np.s_[0:timesteps])
    data_list = np.array(dataset).tolist()

    return data_list


def get_timesteps(hf):
    hdf_timesteps = hf['Results']['Unsteady']['Output']['Output Blocks']['Base Output'] \
        ['Unsteady Time Series']['Time']
    timesteps = hdf_timesteps.shape[0]
    return timesteps


def getXSAttributes(hf):
    hdfXSAttributes = hf['Geometry']['Cross Sections']['Attributes']
    XSAttributes = []
    for key in hdfXSAttributes:
        if key in ['Cell Spacing', "Manning's n", 'Names', 'Tolerances']:
            continue
        else:
            XSAttributes.append(key)  # List of 2D Area names
    return XSAttributes


def get_FacePoints_Coordinates(hf, curr_2DArea):
    hdf2DFacePoints_Coordinates = hf['Geometry']['2D Flow Areas']
    dataset = hdf2DFacePoints_Coordinates[curr_2DArea]['FacePoints Coordinate']
    data_list = np.array(dataset).tolist()
    return data_list


def get_Cells_Face_Info(hf, curr_2DArea):
    hdf2DCell_Face_Info = hf['Geometry']['2D Flow Areas']
    dataset = hdf2DCell_Face_Info[curr_2DArea]['Cells Face and Orientation Info']
    data_list = np.array(dataset).tolist()
    return data_list


def get_Cells_FacePoints_Index(hf, curr_2DArea):
    hdf2DCell_Face_Index = hf['Geometry']['2D Flow Areas']
    dataset = hdf2DCell_Face_Index[curr_2DArea]['Cells FacePoint Indexes']
    data_list = np.array(dataset).tolist()
    return data_list


def is_FacePoint_perimeter(hf, curr_2DArea):
    hdf2DCell_Face_is_perimeter = hf['Geometry']['2D Flow Areas']
    dataset = hdf2DCell_Face_is_perimeter[curr_2DArea]['FacePoints Is Perimeter']
    data_list = np.array(dataset).tolist()
    return data_list


def get_faces_FacePoint_Index (hf, curr_2DArea):
    hdf2DCell = hf['Geometry']['2D Flow Areas']
    dataset = hdf2DCell[curr_2DArea]['Faces FacePoint Indexes']
    data_list = np.array(dataset).tolist()
    return data_list


def get_faces_Perimeter_Info (hf, curr_2DArea):
    hdf2DCell = hf['Geometry']['2D Flow Areas']
    dataset = hdf2DCell[curr_2DArea]['Faces Perimeter Info']
    data_list = np.array(dataset).tolist()
    return data_list


def get_faces_Perimeter_Values (hf, curr_2DArea):
    hdf2DCell = hf['Geometry']['2D Flow Areas']
    dataset = hdf2DCell[curr_2DArea]['Faces Perimeter Values']
    data_list = np.array(dataset).tolist()
    return data_list


def get_face_orientation_info (hf, curr_2DArea):
    hdf2DCell = hf['Geometry']['2D Flow Areas']
    dataset = hdf2DCell[curr_2DArea]['Cells Face and Orientation Info']
    data_list = np.array(dataset).tolist()
    return data_list


def get_face_orientation_values (hf, curr_2DArea):
    hdf2DCell = hf['Geometry']['2D Flow Areas']
    dataset = hdf2DCell[curr_2DArea]['Cells Face and Orientation Values']
    data_list = np.array(dataset).tolist()
    return data_list

#********************************Buffer to fix self-intersections*********************************
def createBuffer(inputfn, outputBufferfn, bufferDist):
    inputds = ogr.Open(inputfn)
    inputlyr = inputds.GetLayer()

    shpdriver = ogr.GetDriverByName('ESRI Shapefile')
    
    if os.path.exists(outputBufferfn):
        shpdriver.DeleteDataSource(outputBufferfn)
    
    outputBufferds = shpdriver.CreateDataSource(outputBufferfn)
    bufferlyr = outputBufferds.CreateLayer(outputBufferfn, geom_type=ogr.wkbPolygon)
    featureDefn = bufferlyr.GetLayerDefn()

    for feature in inputlyr:
        ingeom = feature.GetGeometryRef()
        geomBuffer = ingeom.Buffer(bufferDist)
        outFeature = ogr.Feature(featureDefn)
        outFeature.SetGeometry(geomBuffer)
        bufferlyr.CreateFeature(outFeature)
        outFeature = None

    inputds = None
    inputlyr = None


#*************************************************************************************************
#-----------------------------Loop through and get XS Polylines and Results-----------------------
#*************************************************************************************************
def get_XS_names (hf):
    try:
        dfXS_geo = hf['Geometry']['Cross Sections']['Attributes']
        dataset = dfXS_geo
        # print (dataset)
        # data_list = np.zeros([1, ], dtype='float64')
        data_list = np.array(dataset).tolist()
        return data_list
    except:
        print ("XS_names not found in hdf file.")
        return None


def get_XS_polyline_info (hf):
    
    try:
        dfXS_geo = hf['Geometry']['Cross Sections']['Polyline Info']
        dataset = dfXS_geo
        # print (dataset)
        # data_list = np.zeros([1, ], dtype='float64')
        data_list = np.array(dataset).tolist()
        return data_list
    
    except:
        print ("XS_polyline_info not found in hdf file.")
        return None

def get_XS_polyline_points (hf):
    
    try:
        dfXS_geo = hf['Geometry']['Cross Sections']['Polyline Points']
        dataset = dfXS_geo
        # print (dataset)
        # data_list = np.zeros([1, ], dtype='float64')
        data_list = np.array(dataset).tolist()
        return data_list
    
    except:
        print ("XS_polyline_points not found in hdf file.")
        return None

def get_XS_wse_results (hf):
    
    try:
        dfXS_results = hf['Results']['Unsteady']['Output']['Output Blocks'] \
            ['Base Output']['Unsteady Time Series']['Cross Sections']['Water Surface']
        dataset = dfXS_results
        # print (dataset)
        # data_list = np.zeros([1, ], dtype='float64')
        data_list = np.array(dataset).tolist()
        return data_list
    
    except:
        print ("XS_wse_results not found in hdf file.")
        return None

def clip_shapefile(inputDS, clipDS, outputDS, geom, coord_sys):

    ## Input
    driverName = "ESRI Shapefile"
    driver = ogr.GetDriverByName(driverName)
    inDataSource = driver.Open(inputDS, 0)
    inLayer = inDataSource.GetLayer()

    print(inLayer.GetFeatureCount())
    ## Clip
    inClipSource = driver.Open(clipDS, 0)
    inClipLayer = inClipSource.GetLayer()
    print(inClipLayer.GetFeatureCount())

    ## Clipped Shapefile... Maybe???
    outDataSource = driver.CreateDataSource(outputDS)

    if geom == 'polygon':
        outLayer = outDataSource.CreateLayer('FINAL', geom_type=ogr.wkbMultiPolygon)
    
    if geom == 'polyline':
        outLayer = outDataSource.CreateLayer('FINAL', geom_type=ogr.wkbMultiLineString)

    print("Writing Projection file w/ hardcoded coordinate system.")
    outputDS_path = os.path.dirname(outputDS)
    outputDS_base = os.path.split(os.path.splitext(outputDS)[0])[1]
    
    with open(os.path.join(outputDS_path, outputDS_base +'.prj'), 'w') as f:
        f.write(coord_sys)
        f.close()

    ogr.Layer.Clip(inLayer, inClipLayer, outLayer)
    print(outLayer.GetFeatureCount())
    inDataSource.Destroy()
    inClipSource.Destroy()
    outDataSource.Destroy()

