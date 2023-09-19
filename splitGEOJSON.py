import geopandas as gpd
import pandas as pd
import math
import os
from tqdm import tqdm

"""
This file does exactly what the title says. It analyzes and splits up a large GEOJSON into equal parts, all with sizes
large enough to be input into the AppEEARS interface in order to extract and process ET and PET time series. 
"""

def extract_shapes(inputFile):
    gdf = gpd.read_file(inputFile)
    size = os.path.getsize(inputFile)
    gdf = gdf.drop_duplicates(subset='grdc_no')
    # Lack of experience contributes to a rudimentary solution here,
    # but in short, this function splits the file into groups based
    # on how many equally sized groups need to be made to output into
    # files of 15 MB each (the file size limit for AppEEARS)
    # Somebody has probably made this, who knows

    # The division by one million converts B to MB.
    # The first divisor made groups that were too large,
    # so the divisor was increased by one. They were still
    # too large, so the divisor was increased by two. It
    # failed AGAIN, so the divisor was increased by four.
    # This function could be improved by focusing on making
    # total catchment areas equal in each file, instead of an equal
    # amount of indices.
    divisor = math.ceil((size / 1000000) / 15) + 4
    groupsize = math.ceil(gdf.shape[0] / divisor)
    index = 0
    num = 1
    while index <= gdf.shape[0]:

        if index + groupsize > gdf.shape[0]:
            new_gdf = gdf[index:-1]
            file_name = 'basin_shapes_' + str(num) + '.geojson'
            path = os.path.join('catchment_shapes', file_name)
            new_gdf.to_file(path, driver='GeoJSON')
            index += groupsize
        else:
            # This takes equal chunks of catchments and stitches them together.
            new_gdf = gdf[index:index+groupsize]
            file_name = 'basin_shapes_' + str(num) + '.geojson'
            path = os.path.join('catchment_shapes', file_name)
            new_gdf.to_file(path, driver='GeoJSON')
            index += groupsize
            num += 1


def total_split(inputFile):


    gdf = gpd.read_file(inputFile)
    gdf = gdf.drop_duplicates(subset='grdc_no')
    count = gdf.shape[0]
    loop = tqdm(total=count)
    for index in range(count):
        data = gdf[index]
        ID = str(data["grdc_no"])
        path = os.path.join('catchment_shapes', f'basin_{ID}_shape.geojson')
        data = gpd.GeoSeries(data)
        data.to_file(path, driver='GeoJSON')

def main():
    # extract_shapes('all_flow_basin_shapes.geojson')
    total_split('all_flow_basin_shapes.geojson')

if __name__ == '__main__':
    main()

