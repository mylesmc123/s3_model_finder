import glob
import json

def output_layers_list(geojson_folder_path, outputfilename):
    # get geojson files in geojson folder
    file_list = glob.glob(geojson_folder_path + '*.geojson')
    # convert file list to json
    json_string = json.dumps(file_list, indent=4)
    print (json_string)
    # write to file
    with open(outputfilename, 'w') as f:
        f.write(json_string)

if __name__ == '__main__':
    geojson_folder_path = './output/perimeter/'
    outputfilename = './output/perimeter_list.json'
    output_layers_list(geojson_folder_path, outputfilename)
