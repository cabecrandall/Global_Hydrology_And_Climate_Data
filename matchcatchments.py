import pandas as pd
import os
from tqdm import tqdm
import indexcatchments
import matplotlib.pyplot as plt

import catchment as c

global metadata
metadata = pd.read_csv('archived_results/catchmentMetadata.csv')
global noLocations
# "keeperCats" is the array where all catchment ID's are stored
# Unit testing may be done here by placing desired catchment ID's in the list
# keeperCats = ['1159100', '3620000', '3621400', '3623100', '3624400', '3618711', '3618720', '3618731', '3618950']
keeperCats = []
noLocations = []
# Just making a blank dataframe that can be used more universally across the module:
data = {}
finalFrame = pd.DataFrame(data)

# the data_is_present function filters catchments in the flow frame that are not in the folders with watersheds that
# have information on temperature, precipitation and evapotransporation.
def data_is_present(frame):
    #if the file doesn't have the right amount of columns, it's thrown out
    if frame.shape[1] == 5:
        return True

def column_adder(frame):
    if frame.shape[1] != 5:
        dataDict = {"average temperature (C)": [], "precipitation": [], "ET [kg/m^2/8day]": []}
        extension = pd.DataFrame(dataDict)
        result = pd.concat([frame, extension], ignore_index=True)
        return result
    else:
        return frame

    # This bad boy has the same decision parameters as data_is_present, but it
    # adds columns instead of throwing the poor thing out



# The existence of this function is controversial, since we don't know if we need to shift the dates
# of catchment flow time series in the southern hemisphere or not...
# Whatever the case, this function is simple, it offsets the recorded dates of the flow data
# for every catchment in the southern hemisphere by four months.
def processDates(frame, column):
    global noLocations
    search_value = column
    try:
        catchment_row = metadata[metadata['Catchment ID'] == int(search_value)]
        latitude = catchment_row["latitude"].iloc[0]
        if latitude < 0:
            frame['Date'] = pd.to_datetime(frame['Date'])
            # plt.plot_date(frame['Date'], frame['flow'])
            # print(type(frame['Date'].iloc[0]))
            frame['Date'] = frame['Date'] - pd.DateOffset(months=4)
            # print(type(frame['Date'].iloc[0]))
            # plt.plot_date(frame['Date'], frame['flow'])
            # plt.show()
        return frame



    except:
        noLocations.append(column)
        return frame



    # Save a value from a different column in that row

def combineCatchmentData(frame, column):
    tempFrame = combiner(frame, column, 'Temp')
    twoThirdsFrame = combiner(tempFrame, column, 'Precip')
    finishedFrame = combiner(twoThirdsFrame, column, 'ET')
    finishedFrame = finishedFrame.rename(columns={'Daily Average LST [C]' : 'average temperature (C)'})
    # if data_is_present:
        # writeToCSV(finishedFrame, column)

    return finishedFrame

def combiner(frame, column, type):
    try:
        tempFolder = "Basin_" + type + "_TS_for_model"
        if type != 'ET':
            file = "basin_" + str(column) + ".csv"
        else:
            file = "ET_basin_" + str(column) + ".csv"
        path = os.path.join(tempFolder, file)
        tempFrame = pd.read_csv(path)
        frame['Date'] = pd.to_datetime(frame['Date'])
        tempFrame['Date'] = pd.to_datetime(tempFrame['Date'])
        combinedFrame = pd.merge(frame, tempFrame, on='Date', how='left')
        return combinedFrame
    except:
        return frame


def writeToCSV(frame, column):
    path = '/Users/calebcrandall/Documents/idealabs/hydrology/TestSeries/'
    file = "basin_" + str(column) + ".csv"
    frame.to_csv(os.path.join(path, file), index=False)

def createCatchmentfile(column, frame):
    newFrame = frame[['date', column]]
    finalFrame = newFrame.rename(columns={column : 'flow'})
    finalFrame = finalFrame.rename(columns={'date' : 'Date'})
    viableRows = finalFrame.notna().all(axis=1)
    #print(finalFrame[viableRows])
    finalFrame = finalFrame[viableRows]
    finalFrame = processDates(finalFrame, column)
    # ^^^ done before adding other columns, because only flow data needs correcting in theory
    return combineCatchmentData(finalFrame, column)

    # writeToCSV(finalFrame[viableRows], column)
    # finalFrame = newFrame.dropna(axis=1)
    # print(finalFrame)


def collectColumns(frame):
    for column in frame.columns:
        # the below 'if' statement allows us to collect all the catchment ID's from the flow sheet, since those
        # catchment ID's are the only numeric columns in that set
           if column[0].isnumeric():
            keeperCats.append(column)
        # if column == '1160685':
        #     break
    # this statement is an optional unit test, where you can put a limited subset of catchments starting from the beginning,
    # and placing the last catchment you want correlated in the "if" statement


def matchCatchments(frame):
    collectColumns(frame)
    # The above line MUST be used instead of the artifical ID set, keeperCats, for the actual algorithm
    loop = tqdm(total=len(keeperCats))
    for column in keeperCats:
        susFrame = createCatchmentfile(column, frame)
        #if data_is_present(susFrame):
        # The above line is an optional measure, to make the correlation sheet look more refined :)
        csvFrame = column_adder(susFrame)
        writeToCSV(csvFrame, column)
        catch = c.catchment(column, csvFrame)
        x = indexcatchments.indexcatchments()
        x.indexCatchment(catch)
        loop.update(1)


    #combineFlowAndTempData()
    # combineFlowAndPrecipData()