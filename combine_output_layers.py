# %%
import os
import json
import glob

# %%
# for each geojson in ./output/perimeter, combine them into a single geojson file as a single featureCollection.
geojsons = glob.glob('./output/perimeter/*.geojson')
print('geojsons:', geojsons)
# %%
# create a featureCollection
featureCollection = {
    'type': 'FeatureCollection',
    'features': []
}
# %%
# for each geojson, open and append to featureCollection
for geojson in geojsons:
    with open(geojson) as f:
        data = json.load(f)
        featureCollection['features'].append(data['features'][0])

#%%
# get todays date
from datetime import date
today = date.today()
# ddMMMYYYY
today = today.strftime("%d%b%Y")
print("Today's date:", today)
        
# %%
# write featureCollection to file
with open(f'./output/perimeters_combined_{today}.geojson', 'w') as f:
    json.dump(featureCollection, f)

