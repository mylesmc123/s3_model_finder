# %%
from types import SimpleNamespace
import boto3
import re,os
import pandas as pd
import h5py
import ras_hdf_to_perimeter

with open(r"Z:\LWI\LWI S3 Key.txt") as secret_file:
    secret = secret_file.readlines()
secret_ID = secret[1].strip('\n')
secret_key = secret[3].strip('\n')

# %%
client = boto3.client('s3',
                   aws_access_key_id=secret_ID,
                   aws_secret_access_key = secret_key)

session = boto3.Session(aws_access_key_id=secret_ID,
                        aws_secret_access_key = secret_key)

s3 = session.resource('s3')

# %%
response = client.list_buckets()
bucket_names = [bucket['Name'] for bucket in response['Buckets']]
# Limiting to buckets I have access to.
bucket_names = [
 'lwi-region4',
 'lwi-region5',
 'lwi-region6',
 'lwi-region7',
 ]


# %%
# response = client.list_buckets()
# create a dictionary of hms and ras models by bucket name
models = {}
for bucket in bucket_names:
    print('\nSearching Bucket:', bucket)
    my_bucket = s3.Bucket(bucket)
    models[bucket] = {
        'hms': [],
        'ras': {
            'all_hdfs': [],
            'plan_hdfs': [],
            # 'models': {
            #     'directory': [],
            #     'plans': {
            #         'file': '',
            #         'name': '',
            #         'description': '',
            #         'ras_type': '',
            #     },
            # },
        },
    }
    for obj in my_bucket.objects.all():
        
        if obj.key.endswith('hms'):
            models[bucket]['hms'].append(obj.key)
        
        if obj.key.endswith('hdf'):
            # If 'HMS' in obj.key dont add to ras['all_hdfs']
            if 'hms' not in obj.key.lower():
                models[bucket]['ras']['all_hdfs'].append(obj.key)
                # If .p**.hdf add to ras['plan_hdfs']
                if re.search('p...hdf', obj.key):   
                        # print(obj.key.split('/')[-1])
                        models[bucket]['ras']['plan_hdfs'].append(obj.key)
            
# models


# %%

models_df = pd.DataFrame(models)
# models_df = models_df.transpose()
models_df

# pd.json_normalize(models).transpose()

# %%
import os
model_dirs = {}
for region in models:
    print(region)
    model_dirs[region] = {
       'dirs' : []
    }
    # For each plan hdf get the model name, description, and ras type (1D, 2D, etc.), and pull a geospatial extent from the hdf.
    # get  model directories
    for plan in models[region]['ras']['plan_hdfs']:
        # print(plan)
        head, tail = os.path.split(plan)
        # print(head)
        model_dirs[region]['dirs'].append(head)

model_dirs['lwi-region4']['dirs']



# %%
# Remove duplicates from list of model directories
for region in model_dirs:
    model_dirs[region]['dirs'] = list(set(model_dirs[region]['dirs']))
    print(region, len(model_dirs[region]['dirs']))

# %%
# for each model directory get first plan file.
last_plan_files = {}
for region in model_dirs:
    last_plan_files[region] = {}
    # print(region)
    for model_dir in model_dirs[region]['dirs']:
        last_plan_files[region][model_dir] = {}
        # print(model_dir)
        for plan_hdf in models[region]['ras']['plan_hdfs']:
            if model_dir in plan_hdf:
                last_plan_files[region][model_dir]['last_plan_file'] = plan_hdf
                # print(plan_hdf)
#                 model_dirs['first_plan_file'] = plan_hdf


# last_plan_files['lwi-region4']['deliverables/20230504_08080203_UC_RAS1D2DModelSetupP2/UC_UpperCalcasieu-2D']

# %%
# For each plan, open hdf and get model name, description, and ras type (1D, 2D, etc.), and pull a geospatial extent from the hdf.
for region in last_plan_files:
    for model_dir in last_plan_files[region]:
        for plan in last_plan_files[region][model_dir]:
            print(last_plan_files[region][model_dir][plan])
            
            # set download file name path and create directory if it doesnt exist
            head, tail = os.path.split(last_plan_files[region][model_dir][plan])
            hdf_dl_file_name = "temp.hdf"
            model_title = tail.split(".")[0]
            # if not os.path.exists(hdf_dl_file_name):
            #     os.makedirs(hdf_dl_file_name)

            # download hdf file
            key = last_plan_files[region][model_dir][plan]
            client.download_file(
                Bucket=region,
                Key=str(last_plan_files[region][model_dir][plan]),
                Filename=hdf_dl_file_name
            )

            # open hdf file
            with h5py.File(hdf_dl_file_name, "r") as f:
                print (f.keys())
                # Is 1D?
                if 'Cross Section Interpolation Surfaces' in f['Geometry'].keys() and not ('2D Flow Areas' in f['Geometry'].keys()):
                    run_type = '1D'
                # Is 2D?
                if '2D Flow Areas' in f['Geometry'].keys() and not ('Cross Section Interpolation Surfaces' in f['Geometry'].keys()):
                    run_type = '2D'
                # Is 1D/2D?
                if ('Cross Section Interpolation Surfaces' in f['Geometry'].keys()) and ('2D Flow Areas' in f['Geometry'].keys()):
                    run_type = '1D/2D'
                 
                plan_name = f['Plan Data']['Plan Information'].attrs['Plan Title'].decode('UTF-8')
                flow_name = f['Plan Data']['Plan Information'].attrs['Flow Title'].decode('UTF-8')
                flow_file = f['Plan Data']['Plan Information'].attrs['Flow Filename'].decode('UTF-8')
                geo_name = f['Plan Data']['Plan Information'].attrs['Geometry Title'].decode('UTF-8')
                geo_file = f['Plan Data']['Plan Information'].attrs['Geometry Filename'].decode('UTF-8')
                timestep = f['Plan Data']['Plan Information'].attrs['Computation Time Step Base'].decode('UTF-8')
                projection = f.attrs['Projection'].decode('UTF-8')
                software_version = f.attrs['File Version'].decode('UTF-8')
                units_system = f.attrs['Units System'].decode('UTF-8')

            # If model is 2D or 1D/2D run ras_hdf_to_perimeter
            if run_type != '1D':
                # Run ras_hdf_to_perimeter
                args_dict =  {
                        "model_title": model_title,
                        "file": hdf_dl_file_name,
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
                
                # return the geojson perimeter file name
                perimeter_geojson = ras_hdf_to_perimeter.make_perimeter(args)

            else:
                # TODO - Run ras_hdf_to_perimeter_1D
                print('1D model parsing not yet implemented.')
                
                

            # delete hdf file
            os.remove(hdf_dl_file_name)