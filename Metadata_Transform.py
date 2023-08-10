import pandas as pd
import numpy as np

global metadata
global new_metadata
global missingBoth

# This function exists as a one-time use to update the catchmentMetadata file used in the study to include all of the
# coordinates for every catchment area, which is currently missing from catchmentMetadata. new_metadata is a related
# spreadsheet collected from the GRDC's website.
def updateMetadata():
    global metadata
    global new_metadata
    count = 0
    print("uh")
    metadata = pd.read_csv("archived_results/catchmentMetadata.csv")
    new_metadata = pd.read_csv("archived_results/new_metadata.csv")
    missingCoords = metadata[metadata['latitude'].isnull()]
    # stripped_metadata = metadata[['Catchment ID', 'latitude', 'longitude']]
    # metacolumns = stripped_metadata.columns
    correctCoords = new_metadata[['Catchment ID', 'latitude', 'longitude']]



    find_lost_sheep()
    delete_lost_sheep()
    format_newsheet(metadata, correctCoords)
    #analyze_locations(missingCoords)


def delete_lost_sheep():
    global metadata
    global missingBoth
    #An optional measure, good for the purposes of the study. Eliminates catchments with no coordinates in either sheet
    hasSomething = ~missingBoth
    metadata = metadata[hasSomething]

def format_newsheet(old_data, new_data):
    # merge whatever two sheets you desire, but I did the whole metadata
    # combined with just the coordinates of the new metadata
    metadata = pd.merge(old_data, new_data, on='Catchment ID')
    # fill the blanks in the original columns with entries from the other
    # coordinate column
    metadata['latitude_x'] = metadata['latitude_x'].replace('', np.nan).fillna(metadata['latitude_y'])
    metadata = metadata.rename(columns={'latitude_x': 'latitude'})
    del metadata['latitude_y']
    # now for longitude:
    metadata['longitude_x'] = metadata['longitude_x'].replace('', np.nan).fillna(metadata['longitude_y'])
    metadata = metadata.rename(columns={'longitude_x': 'longitude'})
    del metadata['longitude_y']


    metadata.to_csv('newCatchmentMetadata.csv', index=False)


def analyze_locations(frame):
    # This function creates a spreadsheet that combines the catchment ID's from both spreadsheets
    # in a readable manner that will allow us to see how they were modified.
    global metadata
    global new_metadata
    # frame.to_csv('missing_coordinates.csv', index=False) - One time use line to analyze characteristics of
    # rows without coordinates. The hypothesis is that all catchments with no coordinates have no ecosystem information.
    locations = pd.merge(frame[['Catchment ID', 'Continent', 'ECO_NAME']],
                         new_metadata[['Catchment ID', 'river', 'station', 'country']], on='Catchment ID', how='outer')
    locations.to_csv('missing_locations.csv', index=False)


def find_lost_sheep():
    global missingBoth
    global metadata
    global new_metadata
    # This function will tell us all catchments in catchmentMetadata that have no coordinates from the old spreadsheet
    # AND no coordinates from the new spreadsheet. It uses newCatchmentMetadata for now. If we can fill in these
    # bad boys, we can move on forever!
    # frame = pd.read_csv("newCatchmentMetadata.csv")
    firstmissing = metadata['latitude'].isnull()
    secondmissing = new_metadata['latitude'].isnull()
    missingBoth = firstmissing & secondmissing
    # frame = metadata[missingBoth]

    # frame.sort_values(by='Catchment ID', ascending=True, inplace=True)
    # frame.to_csv("lost_sheep.csv", index=False)




    # for value in metadata['Catchment ID']:
    #     try:
    #         # value = str(int(value))
    #
    #         print(correctCoords.loc[value])
    #     except:
    #         print("failed!")


    # metadata['Catchment ID'] = metadata['Catchment ID'].astype(str)
    # correctCoords['Catchment ID'] = correctCoords['Catchment ID'].astype(str)
    # metadata = pd.merge(metadata, correctCoords, on='Catchment ID', how='left')



    # metadata = pd.merge(correctCoords, metadata, on="Catchment ID", how='right')
    # metadata['Catchment ID'].to_string()
    # metadata.to_csv('newCatchmentMetadata.csv', index=False)


    #metadata = metadata.sort_values('Catchment ID')
    # goodCoords = new_metadata[['latitude', 'longitude']]
    # metadata.update(goodCoords)
