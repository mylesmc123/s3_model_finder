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

hdf_file = r"Z:\py\s3_model_finder\s3_hdf_files\East_Galveston_Bay.p08.hdf"
forecast = hdf_file.split("\\")[-1].split(".")[0]
with h5py.File(hdf_file, 'r') as hf:
    projection = hf.attrs['Projection']

args_dict =  {
        "file": hdf_file,
        "postprocessingdirectory": "./output",
        "forecast": forecast,
        "wkt": projection,  
    }

# Simplespace is used to convert a dictionary to the same type as sysArgs would have.
args = SimpleNamespace(**args_dict)

home_dir = os.path.join(args.postprocessingdirectory,args.forecast)
tempDir = os.path.join(home_dir,"tempfiles")
postp_area = os.path.join(args.postprocessingdirectory, "postp_area.shp")

if not os.path.exists(home_dir):
    os.makedirs(home_dir)

ras_output_extract_wse_to_shp.tempDirSweep(tempDir)
hf = h5py.File(args.file, 'r')
list_of_2DAreas = ras_output_extract_wse_to_shp.get2DAreaNames(hf)
timesteps = ras_output_extract_wse_to_shp.get_timesteps(hf)
# all_data = np.empty((0, timesteps + 6), ) # Includes an extra wse column for maximum row value
all_data = np.empty((0, 5), ) # IDoesnt include wse columns

#Initialize shapefile of all 2D flow cells
poly_wse_shp = os.path.join(tempDir, 'ras_wse.shp')
w = shapefile.Writer(poly_wse_shp)

# ***********Begin writing to polygon shapefile using rows of cell index pts
# w = shapefile.Writer('test_polygon_all_data')   <-------- Currently  initialize outside of 2DArea loop
# Start writing to Shapefile
# Writing field names and types
# "C": Characters, text.
# "N": Numbers, with or without decimals.
# "F": Floats(same as "N").
# "L": Logical, for boolean True / False values.
# "D": Dates.
# "M": Memo
w.field('Area2D', 'C')
w.field('Cell_Index', 'N')
w.field('Easting', 'N', decimal=2)
w.field('Northing', 'N', decimal=2)
w.field('min_elev', 'N', decimal=2)

#Creating Results fields, same number as timesteps
i = 0
while i < timesteps:
    w.field('wse_' + str(i), 'N', decimal=2)
    i += 1
# Shapefile is closed after 2DArea loop

#Add a wse for maximum water surface at end
w.field('wse_max', 'N', decimal=2)


#Loop through all 2D flow areas in HDF file and extract geometry pts and results
for curr_2DArea in list_of_2DAreas:
    print("Current 2D Area is: %s" % curr_2DArea)

    xy_pts = np.array(ras_output_extract_wse_to_shp.get2DArea_cellcenter_pts(curr_2DArea, hf))
    min_elev = np.array(ras_output_extract_wse_to_shp.get2DCells_min_elev(curr_2DArea, hf)).round(decimals=2)
    transpose_min_elev = min_elev.T

    # wse_data = np.array(ras_output_extract_wse_to_shp.get2DArea_wse_data(curr_2DArea, hf))
    # transpose_wse = wse_data.T.round(decimals=2)

    # Find WSE values that are equal to cell min elev, set to NaN, all others set to 1
    # repeats_cell_min_elev = np.tile(min_elev, (timesteps,1)).T
    # cell_depths = transpose_wse - repeats_cell_min_elev
    # cell_depths[cell_depths > 0] = 1
    # cell_depths[cell_depths == 0] = 0

    #Remove zero depth values
    # filtered_transpose_wse = cell_depths * transpose_wse
    # filtered_transpose_wse[filtered_transpose_wse==0] = -9999
    # filtered_transpose_wse.round(decimals=2)
    # max_of_row = np.max(filtered_transpose_wse, axis=1)

    cell_index = np.arange(xy_pts.shape[0])
    curr_2DArea_index = [curr_2DArea.decode('UTF-8')]* (xy_pts.shape[0])

    #Adding columns to results array
    all_data_for_curr_2DArea = np.column_stack((curr_2DArea_index, cell_index, xy_pts, min_elev))
    # all_data_for_curr_2DArea = np.concatenate((all_data_for_curr_2DArea, filtered_transpose_wse), axis=1)
    # all_data_for_curr_2DArea = np.column_stack((all_data_for_curr_2DArea, max_of_row))

    #Save into the overall dataset
    all_data = np.append(all_data, all_data_for_curr_2DArea, axis=0)

    # Assemble 2D Cell Polygons
    cell_face_info = ras_output_extract_wse_to_shp.get_Cells_Face_Info(hf, curr_2DArea)
    cell_face_xy_pts = ras_output_extract_wse_to_shp.get_FacePoints_Coordinates(hf, curr_2DArea)
    cell_face_index_pts = ras_output_extract_wse_to_shp.get_Cells_FacePoints_Index(hf, curr_2DArea)

    #Assemble info about perimeter faces and facepoints
    cell_facept_is_perimeter = ras_output_extract_wse_to_shp.is_FacePoint_perimeter(hf, curr_2DArea)
    face_facept_index = ras_output_extract_wse_to_shp.get_faces_FacePoint_Index(hf, curr_2DArea)
    face_perimeter_info = ras_output_extract_wse_to_shp.get_faces_Perimeter_Info(hf, curr_2DArea)
    face_perimeter_values = ras_output_extract_wse_to_shp.get_faces_Perimeter_Values(hf, curr_2DArea)
    face_orientation_info = ras_output_extract_wse_to_shp.get_face_orientation_info(hf, curr_2DArea)
    face_orientation_values = ras_output_extract_wse_to_shp.get_face_orientation_values(hf, curr_2DArea)

    #Assemble current polygons
    cell_ids = []
    index_size = len(cell_face_index_pts[0])
    curr_2DArea_Polygon_xy_pts = []
    cell_id = 0
    cell_ids = []
    print ('Assemble current 2D Area polygons..')
    for row in tqdm(cell_face_index_pts):
        #find if facepoints are perimeter
        print('find if facepoints are on the perimeter')
        perimeter_facepts = []
        for facept in tqdm(row):
            if facept != -1:
                if cell_facept_is_perimeter[facept] == -1:
                    perimeter_facepts.append(facept)
        #print(perimeter_facepts)

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

            #If the current facept is on the perimeter, add the perimeter points
            if curr_facept in tqdm(perimeter_facepts):
                
                if next_facept in perimeter_facepts:
                    face_index=0
                    
                    for face in face_facept_index:
                        if curr_facept == face_facept_index[face_index][0]:
                            potential_face = face_index
                            
                            if next_facept == face_facept_index[potential_face][1]:
                                next_is_first = False
                                curr_face_index = face_index
                                # print("found face")
                                break
                        
                        if next_facept == face_facept_index[face_index][0]:
                            potential_face = face_index
                            
                            if curr_facept == face_facept_index[potential_face][1]:
                                next_is_first = True
                                curr_face_index = face_index
                                # print("found face")
                                break

                        face_index +=1


                    perimeter_st_pt = face_perimeter_info[curr_face_index][0]
                    num_perimeter_pts = face_perimeter_info[curr_face_index][1]
                    perimeter_end_pt = perimeter_st_pt + num_perimeter_pts - 1
                    perimeter_pt_index = perimeter_st_pt

                    extra_perimeter_xy_pts = []

                    # print("...adding perimeter pts, for face %s" % curr_face_index )
                    while perimeter_pt_index <= perimeter_end_pt:
                        # polygon.append(face_perimeter_values[perimeter_pt_index])
                        extra_perimeter_xy_pts.append(face_perimeter_values[perimeter_pt_index])
                        perimeter_pt_index += 1

                    if next_is_first:
                        extra_perimeter_xy_pts = extra_perimeter_xy_pts[::-1]

                    polygon.extend(extra_perimeter_xy_pts)
                #polygon.append(cell_face_xy_pts[next_facept])

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
    
    for row_id, poly_row in enumerate(curr_2DArea_Polygon_xy_pts):
        
        if len(poly_row) > 2:
            w.poly([poly_row[::-1]]) #clockwise flip
            #w.record(INT=nr, LOWPREC=nr, MEDPREC=nr, HIGH)
            #w.record(Area2D=str_curr_2DArea,Cell_Index=cell_id, Easting=all_data_for_curr_2DArea[cell_id][])
            #w.record('Area2D', str_curr_2DArea)
            #w.record('Cell Index', cell_id)
            records = np.array(all_data_for_curr_2DArea[cell_ids[row_id]]).tolist()
            w.record(*records)

#Close 2DArea polygon shapefile
print("Closing shapefile with all 2D Area polygons.")
w.close()

print("Writing Projection file w/ hardcoded coordinate system.")
with open(os.path.join(tempDir,'ras_wse.prj'), 'w') as f:
    f.write(args.wkt)
    f.close()