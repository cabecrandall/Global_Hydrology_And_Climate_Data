import os
import pandas as pd
from tqdm import tqdm

# Specify the input ASCII file path and the delimiter used in the file
# This code is not designed to detect which files have the right format, therefore the directory
# below must ONLY have files that can be processed into flow timeseries.
directory = 'New_Raw_Flow_Timeseries'
delimiter = ';'  # Replace with the appropriate delimiter used in your file
new_metadata = {"Catchment ID": [], "River": [], "Station": [], "Country": [], "Latitude": [], "Longitude": [],
                "Catchment Area": [], "Altitude": [], 'Number of Years': []}  # Define Dictionary for a metadata file!
#flow_liters = pd.DataFrame({"Date": []})  # first flow spreadsheet!
#flow_liters_km = pd.DataFrame({"Date": []})  # second flow spreadsheet!
flow_cubic_meters_ps = pd.DataFrame({"Date": []})  # Raw flow spreadsheet!

# This preliminary section is used to track the progress of the extraction using TQDM.
# It is important to keep in mind the amount of catchments to be extracted! Insert that number into
# "catchments_to_do".
catchments_done = 0
catchments_to_do = 2215  # Amount of catchments in the directory
loop = tqdm(total=catchments_to_do)

# Every file will be processed using the following nested loop method.
for filename in os.listdir(directory):
    river = None
    station = None
    country = None
    latitude = None
    longitude = None
    catchment_area = None
    altitude = None
    num_of_years = None
    # ABOVE: Define temporary variables to store in metadata after individual extraction
    # Variables below are used to process flow!
    date = None
    raw_flow = None
    L_d = None
    L_d_km = None
    # BELOW: define the file path to open for the extraction
    input_file = os.path.join(directory, filename)
    # Specify the output CSV file path
    catchment_id = filename[0:7]
    output_file = 'Flow_TS_for_model/Flow_basin_' + filename[0:7] + '.csv'

    # Open a temporary dataframe, and also three lists that will quickly be incorporated into the dataframes
    #tempL_D = pd.DataFrame(columns=['Date', catchment_id])
    #tempL_D_Km = pd.DataFrame(columns=['Date', catchment_id])
    tempM3_S = pd.DataFrame(columns=['Date', catchment_id])

    listDates = []
    #listL_D = []
    #listL_D_Km = []
    listM3_S = []

    # Open the input file
    with open(input_file, 'r+', encoding='ascii', errors='ignore') as file:
        # Read the file content
        content = file.readlines()
        counter = 0
        # This inner for loop is meant to process every single line of the current file in the first for loop.
        for line in content:
            # Since the first section of each GRDC catchment header has a static format, the data read from the file
            # is split into lists, with one list per line. The "if" ladder here sorts the data into the correct variables
            # based on where it lies on the line. Trial and error sells, but who's buying? Strings are converted into
            # integers where needed.
            if line.startswith('#'):
                data = line.split()
            if counter == 9:
                river = data[2:]
                river = " ".join(river)
            if counter == 10:
                station = data[2:]
                station = " ".join(station)
            if counter == 11:
                country = data[2]
            if counter == 12:
                latitude = data[3]
                latitude = float(latitude)
            if counter == 13:
                longitude = data[3]
                longitude = float(longitude)
            if counter == 14:
                catchment_area = data[4]
                catchment_area = float(catchment_area)
            if counter == 15:
                altitude = data[4]
                altitude = float(altitude)

            # one more variable for the metadata, often placed irregularly, so the format is different:
            if line.startswith('# No. of years:'):
                data = line.split()
                num_of_years = data[4]
                num_of_years = float(num_of_years)

            # flow data collection starts. Same framework as the metadata collection, aided by the static format of the
            # GRDC files. Delimiter is a semicolon in current GRDC versions.
            if not line.startswith('#') and not line.startswith('Y'):
                data = line.split(delimiter)
                date = data[0]
                try:
                    raw_flow = data[2]

                    # whitespace and newlines removed manually.
                    raw_flow = raw_flow.replace(' ', '')
                    raw_flow = raw_flow.replace('\n', '')
                    raw_flow = float(raw_flow)
                    if raw_flow < -900.0:
                        raw_flow = None
                    if raw_flow is not None:
                        # The raw flow data is in cubic meters per second, but in the interest of the study,
                        # it must be converted to Liters per day, done here.
                        # For reference, there are 1000 liters in a cubic meter and 86400 seconds in a day,
                        # hence the conversion.
                        L_d = (raw_flow * 1000 * 86400)
                        # for the second dataset, we obtain specific discharge by dividing L/day
                        # by the area of the catchment in km^2.
                        L_d_km = L_d / catchment_area
                    else:
                        L_d = None
                        L_d_km = None
                except Exception:
                    raw_flow = None
                    L_d = None
                    L_d_km = None

                #listL_D.append(L_d)
                #listL_D_Km.append(L_d_km)
                listM3_S.append(raw_flow)
                listDates.append(date)
                # TODO: Here's the next plan: I make a temp dataframe, and then join it with the big boys!

            # a representative index iterator of the line being worked on
            counter += 1

        ############################ END INNER FOR LOOP ###############################

        # This is done at the end of the processing for each file, as it organizes the metadata for each catchment
        new_metadata['Catchment ID'].append(catchment_id)
        new_metadata['River'].append(river)
        new_metadata['Station'].append(station)
        new_metadata['Country'].append(country)
        new_metadata['Latitude'].append(latitude)
        new_metadata['Longitude'].append(longitude)
        new_metadata['Catchment Area'].append(catchment_area)
        new_metadata['Altitude'].append(altitude)
        new_metadata['Number of Years'].append(num_of_years)

        # Now, the lists that have the timeseries data are made into dataframes.
        # Next, they are outer-joined to the main frames defined before the "for" loop.
        #tempL_D['Date'], tempL_D[catchment_id] = listDates, listL_D
        #tempL_D_Km['Date'], tempL_D_Km[catchment_id] = listDates, listL_D_Km
        tempM3_S['Date'], tempM3_S[catchment_id] = listDates, listM3_S

        #flow_liters = pd.merge(flow_liters, tempL_D, on='Date', how='outer')
        #flow_liters_km = pd.merge(flow_liters_km, tempL_D_Km, on='Date', how='outer')
        flow_cubic_meters_ps = pd.merge(flow_cubic_meters_ps, tempM3_S, on='Date', how='outer')

        # this final section of the loop tracks the amount of catchments processed,
        # and ends the loop based on the initial parameters. By default, the loop ends
        # when all catchments in the original directory were processed.
        catchments_done += 1
        loop.update(1)
        if catchments_done == catchments_to_do:
            break

    # The metadata dictionary is converted into a dataframe
# metaDataDf = pd.DataFrame.from_dict(new_metadata)

# All dataframes are exported to the home directory to live happily ever after!
# metaDataDf.to_csv("new_metadata.csv", index=False)
#flow_liters.to_csv("allDailyFlowInLitersPerDay.csv", index=False)
#flow_liters_km.to_csv("allDailyFlowInLitersPerDayPerSqKm.csv", index=False)
flow_cubic_meters_ps.to_csv("allDailyFlowData_new.csv", index=False, quoting=False, escapechar='-')
