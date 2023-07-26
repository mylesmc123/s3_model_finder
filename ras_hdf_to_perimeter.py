import glob
import os
import shutil

import numpy as np
import h5py
import shapefile
import time
import argparse
from types import SimpleNamespace
import ras_output_extract_wse_to_shp
from tqdm import tqdm
import geopandas as gpd

def make_perimeter(args):
    home_dir = os.path.join(args.postprocessingdirectory)
    tempDir = os.path.join(home_dir,"tempfiles")
    postp_area = os.path.join(args.postprocessingdirectory, "postp_area.shp")

    if not os.path.exists(home_dir):
        os.makedirs(home_dir)

    ras_output_extract_wse_to_shp.tempDirSweep(tempDir)
    with h5py.File(args.file, 'r') as hf:
        list_of_2DAreas = ras_output_extract_wse_to_shp.get2DAreaNames(hf)
        # timesteps = ras_output_extract_wse_to_shp.get_timesteps(hf)
        # all_data = np.empty((0, timesteps + 6), ) # Includes an extra wse column for maximum row value
        all_data = np.empty((0, 5), ) # Doesnt include wse columns

        #Initialize shapefile of all 2D flow cells
        poly_wse_shp = os.path.join(tempDir, 'ras_wse.shp')
        w = shapefile.Writer(poly_wse_shp)
        w.field('Area2D', 'C')
        w.field('Cell_Index', 'N')
        w.field('Easting', 'N', decimal=2)
        w.field('Northing', 'N', decimal=2)
        w.field('min_elev', 'N', decimal=2)

        #Loop through all 2D flow areas in HDF file and extract geometry pts and results
        for curr_2DArea in list_of_2DAreas:
            print("Current 2D Area is: %s" % curr_2DArea)

            xy_pts = np.array(ras_output_extract_wse_to_shp.get2DArea_cellcenter_pts(curr_2DArea, hf))
            min_elev = np.array(ras_output_extract_wse_to_shp.get2DCells_min_elev(curr_2DArea, hf)).round(decimals=2)
            # transpose_min_elev = min_elev.T

            cell_index = np.arange(xy_pts.shape[0])
            curr_2DArea_index = [curr_2DArea.decode('UTF-8')]* (xy_pts.shape[0])

            #Adding columns to results array
            all_data_for_curr_2DArea = np.column_stack((curr_2DArea_index, cell_index, xy_pts, min_elev))

            #Save into the overall dataset
            all_data = np.append(all_data, all_data_for_curr_2DArea, axis=0)

            # Assemble 2D Cell Polygons
            # cell_face_info = ras_output_extract_wse_to_shp.get_Cells_Face_Info(hf, curr_2DArea)
            cell_face_xy_pts = ras_output_extract_wse_to_shp.get_FacePoints_Coordinates(hf, curr_2DArea)
            cell_face_index_pts = ras_output_extract_wse_to_shp.get_Cells_FacePoints_Index(hf, curr_2DArea)

            #Assemble info about perimeter faces and facepoints
            cell_facept_is_perimeter = ras_output_extract_wse_to_shp.is_FacePoint_perimeter(hf, curr_2DArea)
            # face_facept_index = ras_output_extract_wse_to_shp.get_faces_FacePoint_Index(hf, curr_2DArea)
            # face_perimeter_info = ras_output_extract_wse_to_shp.get_faces_Perimeter_Info(hf, curr_2DArea)
            # face_perimeter_values = ras_output_extract_wse_to_shp.get_faces_Perimeter_Values(hf, curr_2DArea)
            # face_orientation_info = ras_output_extract_wse_to_shp.get_face_orientation_info(hf, curr_2DArea)
            # face_orientation_values = ras_output_extract_wse_to_shp.get_face_orientation_values(hf, curr_2DArea)

        #Assemble current polygons
        cell_ids = []
        index_size = len(cell_face_index_pts[0])
        curr_2DArea_Polygon_xy_pts = []
        cell_id = 0
        cell_ids = []
        
        print ('Assemble current 2D Area polygons..')
        for row in tqdm(cell_face_index_pts):
            #find if facepoints are perimeter
            perimeter_facepts = []
            for facept in row:
                if facept != -1:
                    if cell_facept_is_perimeter[facept] == -1:
                        perimeter_facepts.append(facept)

            #Declare empty polygon list for 2D cell
            polygon = []
            i = 0
            while i < index_size:
                curr_facept = row[i]
                
                if curr_facept != -1:
                    polygon.append(cell_face_xy_pts[curr_facept])

                if i < (index_size -1) :
                    next_facept = row[i+1]

                if i == (index_size -1):
                    next_facept = row[0]
                i += 1

            #Append the first face pt coordinate
            polygon.append(cell_face_xy_pts[row[0]])

            #Append to the total 2D Area set if more than 2 points (there are some lateral weirs represented like this)
            if sum(1 for n in row if n != -1)>=3:
                curr_2DArea_Polygon_xy_pts.append(polygon)
                #Keep track of cell_ids that make it into the polygon set
                cell_ids.append(cell_id)

            cell_id += 1

        #--------------Saving polygons and records to shapefile-------------
        print ("writing %s polygons to shapefile..." %curr_2DArea.decode('UTF-8'))
        str_curr_2DArea = curr_2DArea.decode('UTF-8')
        
        for row_id, poly_row in enumerate(tqdm(curr_2DArea_Polygon_xy_pts)):
            
            if len(poly_row) > 2:
                w.poly([poly_row[::-1]]) #clockwise flip
                records = np.array(all_data_for_curr_2DArea[cell_ids[row_id]]).tolist()
                w.record(*records)

    #Close 2DArea polygon shapefile
    print("Closing shapefile with all 2D Area polygons.")
    w.close()

    print("Writing Projection file w/ hardcoded coordinate system.")
    with open(os.path.join(tempDir,'ras_wse.prj'), 'w') as f:
        f.write(args.wkt)
        f.close()

    # Open the shapefile as a geodataframe, dissolve the polygons, reproject to EPS4326, add data, and save as a geojson.
    output_geojson = os.path.join(home_dir, f'{args.model_title}.geojson')

    try:
        gdf = gpd.read_file(poly_wse_shp).dissolve(by="Area2D").to_crs(epsg=4326).drop(columns=["Cell_Index", "min_elev", "Easting", "Northing"])
        # Add columns for model_title, region, run_type, timestep, software_version, units_system
        gdf["Model Title"] = args.model_title
        gdf["Region"] = args.region
        gdf["Run Type"] = args.run_type
        gdf["Timestep"] = args.timestep
        gdf["Software Version"] = args.software_version
        gdf["Units System"] = args.units_system
        gdf["S3 Model Location"] = args.s3_model_location

        gdf.to_file(output_geojson, driver='GeoJSON')
    
    except:
        print("Could not convert shapefile to geojson. Invalid Geometry")
        # Copy poly_wse_shp shapefiles with glob in the tempfiles dir to invalid folder and rename to model_title
        for shp in glob.glob(f'tempDir/*'):
            shutil.copy(shp, os.path.join(home_dir, "invalid_geometry", f'{args.model_title}_{shp}'))
        gdf = "invalid_geometry"

    # Delete the temp directory
    try:
        shutil.rmtree(tempDir)
    except:
        print(f"Could not delete {tempDir}")
        

    return gdf
    
if __name__ == "__main__":
        
    hdf_file = r"Z:\py\s3_model_finder\s3_hdf_files\WC.p08.hdf"
    s3_model_location = "deliverables/20230404_TO3_Hydrology_Model_Stage2/HUC8_08090302_HEC-RAS_V631_20230404/Model/HUC8_08090302_HEC-RAS_V631_20230404/"
    region = "lwi-region4"

    model_title = hdf_file.split("\\")[-1].split(".")[0]
    with h5py.File(hdf_file, 'r') as f:

        plan_name = f['Plan Data']['Plan Information'].attrs['Plan Title'].decode('UTF-8')
        flow_name = f['Plan Data']['Plan Information'].attrs['Flow Title'].decode('UTF-8')
        flow_file = f['Plan Data']['Plan Information'].attrs['Flow Filename'].decode('UTF-8')
        geo_name = f['Plan Data']['Plan Information'].attrs['Geometry Title'].decode('UTF-8')
        geo_file = f['Plan Data']['Plan Information'].attrs['Geometry Filename'].decode('UTF-8')
        timestep = f['Plan Data']['Plan Information'].attrs['Computation Time Step Base'].decode('UTF-8')
        projection = f.attrs['Projection'].decode('UTF-8')
        software_version = f.attrs['File Version'].decode('UTF-8')
        units_system = f.attrs['Units System'].decode('UTF-8')

    run_type = '2D'
    
    args_dict =  {
                    "model_title": model_title,
                    "file": hdf_file,
                    "s3_model_location": s3_model_location,
                    "postprocessingdirectory": "./output/perimeter",
                    "forecast": model_title,
                    "wkt": projection,
                    "timestep": timestep,
                    "run_type": run_type,
                    "region": region,
                    "software_version": software_version,
                    "units_system": units_system,
                    }      

    # Simplespace is used to convert a dictionary to the same type as sysArgs would have.
    args = SimpleNamespace(**args_dict)
    
    make_perimeter(args)