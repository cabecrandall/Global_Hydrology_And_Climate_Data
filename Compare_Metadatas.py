import os
import pandas as pd
metadata = pd.read_csv('catchmentMetadata.csv')
old_metadata = pd.read_csv('shortened_travis_metadata.csv')
# These two metadatas can be compared, and this module will screen them
# for similarities and differences across timescales.
precip_directory = "Basin_Precip_TS_for_model"
temp_directory = "Basin_Temp_TS_for_model"
ET_directory = "Basin_ET_TS_for_model"
PET_directory = "Basin_PET_TS_for_model"

def has_parentheses(input_string):
    return '(' in input_string or ')' in input_string

def countOverlaps(directory):
    num_overlaps = 0
        # the countOverlaps method exists to analyze the similarity of the
        # new flow data set with the original precipitation dataset by figuring
        # out how many catchment ID's overlap between the two sets. It can be commented
        # out during normal operation, as it only exists to supplement
        # the methodology.
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if has_parentheses(file_path):
            continue
        catchment_id = file_path[-11:-4]
        try:
            if int(catchment_id) in metadata['Catchment ID'].values:
                num_overlaps += 1
        except:
            Exception(Exception)
    return num_overlaps


def metadata_analysis():
    # The first purpose of this function will be to compare the areas of identical catchments
    # by outputting a .csv file including all the area figures from both documents.
    # WARNING: content in this function will not be compatible with metadata files not specifically used in this experiment.
    metadata_areas = metadata[['Catchment ID', 'Catchment Area']]
    old_metadata_areas = old_metadata[['Catchment ID', 'area_sqkm', 'garea_sqkm']]
    combinedFrame = pd.merge(metadata_areas, old_metadata_areas, on='Catchment ID', how='left')
    combinedFrame.to_csv('catchmentAreaVersions.csv', index=False)

def compare_metadatas():
    not_the_sames = []
    # the first step will be to fish out any possible ID's that may be identical catchments, but just with changed
    # ID's. This will be done by collecting the difference from the old metadata for each new catchment's coordinates,
    # and then selecting the old catchment with the most similar coordinates to the new catchment.
    # Both the difference in longitude and latitude will be calculated, and the largest minimum value will be output and analyzed.
    # For the first attempt, we will try to find any catchments between the two spreadsheets that have different
    # ID's AND less than 0.1 degree of difference in both latitude and longitude.
    for ID in metadata['Catchment ID']:
        latitude = metadata.loc[metadata['Catchment ID'] == int(ID), 'Latitude'].values[0]
        longitude = metadata.loc[metadata['Catchment ID'] == int(ID), 'Longitude'].values[0]

        old_metadata['latdiff'] = abs(old_metadata['latitude'] - latitude)
        old_metadata['longdiff'] = abs(old_metadata['longitude'] - longitude)

        mask = old_metadata[old_metadata['longdiff'] < 0.01]
        mask = mask[mask['latdiff'] < 0.01]

        print(len(mask))

        if len(mask) == 0:
            continue
        if len(mask) > 1:
            mask = mask[mask['latdiff'] == mask['latdiff'].min()]
            print(mask)
        if len(mask) == 1:
            print(mask['Catchment ID'].values)
            oldID = mask['Catchment ID'].values
            oldID = oldID[0]
            if oldID == ID:
                print("it's the same!")
            else:
                print("it's not the same!")
                not_the_sames.append(ID)


        # latmin = old_metadata['latdiff'].min()
        # longmin = old_metadata['longdiff'].min()
        # largest = max(latmin, longmin)
    print(f'{not_the_sames} aren\'t the same!')


    # new_metadata.to_csv("newCatchmentMetadata.csv", index=False)



# CODE TO RUN
def main():
    # print(f"The current Precipitation dataset has {countOverlaps(precip_directory)} overlapping catchments with the new flow dataset")
    # print(f"The current Temperature dataset has {countOverlaps(temp_directory)} overlapping catchments with the new flow dataset")
    # print(f"The current ET dataset has {countOverlaps(ET_directory)} overlapping catchments with the new flow dataset")
    # print(f"The current PET dataset has {countOverlaps(PET_directory)} overlapping catchments with the new flow dataset")

    # metadata_analysis()

    compare_metadatas()




if __name__ == '__main__':
    main()
