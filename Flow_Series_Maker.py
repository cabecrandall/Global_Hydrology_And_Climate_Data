import os
import pandas as pd
from tqdm import tqdm

'''
.. module:: flow_data_processor

   :platform: Any
   :synopsis: Module for processing flow data and generating metadata.

'''

def read_metadata_from_file(input_file, delimiter):
    '''
    .. function:: read_metadata_from_file(input_file, delimiter)

       Extracts metadata from a file.

       :param input_file: The path to the input file.
       :type input_file: str
       :param delimiter: The delimiter used in the file.
       :type delimiter: str
       :return: A dictionary containing metadata.
       :rtype: dict
    '''
    metadata = {}
    with open(input_file, 'r+', encoding='ascii', errors='ignore') as file:
        content = file.readlines()
        counter = 0
        for line in content:
            if line.startswith('#'):
                data = line.split()
                if counter == 9:
                    metadata['River'] = " ".join(data[2:])
                if counter == 10:
                    metadata['Station'] = " ".join(data[2:])
                if counter == 11:
                    metadata['Country'] = data[2]
                if counter == 12:
                    metadata['Latitude'] = float(data[3])
                if counter == 13:
                    metadata['Longitude'] = float(data[3])
                if counter == 14:
                    metadata['Catchment Area'] = float(data[4])
                if counter == 15:
                    metadata['Altitude'] = float(data[4])
                if line.startswith('# No. of years:'):
                    data = line.split()
                    metadata['Number of Years'] = float(data[4])
                counter += 1
    return metadata

def process_flow_data(input_file, delimiter, catchment_area):
    '''
    .. function:: process_flow_data(input_file, delimiter, catchment_area)

       Processes flow data from a file.

       :param input_file: The path to the input file.
       :type input_file: str
       :param delimiter: The delimiter used in the file.
       :type delimiter: str
       :param catchment_area: The catchment area for flow data conversion.
       :type catchment_area: float
       :return: Lists of dates, raw flow data, converted flow data, and specific discharge.
       :rtype: list, list, list, list
    '''
    date_list = []
    raw_flow_list = []
    with open(input_file, 'r+', encoding='ascii', errors='ignore') as file:
        content = file.readlines()
        for line in content:
            if not line.startswith('#') and not line.startswith('Y'):
                data = line.split(delimiter)
                date = data[0]
                try:
                    raw_flow = data[2].replace(' ', '').replace('\n', '')
                    raw_flow = float(raw_flow) if raw_flow != 'NaN' else None
                except Exception:
                    raw_flow = None
                date_list.append(date)
                raw_flow_list.append(raw_flow)
    if catchment_area is not None:
        L_d_list = [(raw * 1000 * 86400) if raw is not None else None for raw in raw_flow_list]
        L_d_km_list = [(L_d / catchment_area) if L_d is not None else None for L_d in L_d_list]
    else:
        L_d_list = L_d_km_list = [None] * len(date_list)
    return date_list, raw_flow_list, L_d_list, L_d_km_list

def process_flow_timeseries_directory(directory, delimiter, catchments_to_do):
    '''
    .. function:: process_flow_timeseries_directory(directory, delimiter, catchments_to_do)

       Processes flow timeseries data for multiple catchments.

       :param directory: The directory containing flow timeseries files.
       :type directory: str
       :param delimiter: The delimiter used in the files.
       :type delimiter: str
       :param catchments_to_do: The number of catchments to process.
       :type catchments_to_do: int
       :return: Metadata for catchments and flow data.
       :rtype: dict, DataFrame
    '''
    new_metadata = {"Catchment ID": [], "River": [], "Station": [], "Country": [], "Latitude": [], "Longitude": [],
                    "Catchment Area": [], "Altitude": [], 'Number of Years': []}

    flow_cubic_meters_ps = pd.DataFrame({"Date": []})

    catchments_done = 0
    loop = tqdm(total=catchments_to_do)

    for filename in os.listdir(directory):
        catchment_id = filename[0:7]
        input_file = os.path.join(directory, filename)
        metadata = read_metadata_from_file(input_file, delimiter)
        date_list, raw_flow_list, L_d_list, L_d_km_list = process_flow_data(input_file, delimiter, metadata.get('Catchment Area'))

        new_metadata['Catchment ID'].append(catchment_id)
        new_metadata['River'].append(metadata.get('River'))
        new_metadata['Station'].append(metadata.get('Station'))
        new_metadata['Country'].append(metadata.get('Country'))
        new_metadata['Latitude'].append(metadata.get('Latitude'))
        new_metadata['Longitude'].append(metadata.get('Longitude'))
        new_metadata['Catchment Area'].append(metadata.get('Catchment Area'))
        new_metadata['Altitude'].append(metadata.get('Altitude'))
        new_metadata['Number of Years'].append(metadata.get('Number of Years'))

        tempM3_S = pd.DataFrame({catchment_id: raw_flow_list})
        flow_cubic_meters_ps = pd.merge(flow_cubic_meters_ps, tempM3_S, left_index=True, right_index=True)

        catchments_done += 1
        loop.update(1)
        if catchments_done == catchments_to_do:
            break

    return new_metadata, flow_cubic_meters_ps

def main():
    '''
    .. function:: main()

       Entry point of the script. Calls other functions to process data and save results.

    '''
    directory = 'New_Raw_Flow_Timeseries'
    delimiter = ';'  # Replace with the appropriate delimiter used in your file
    catchments_to_do = 2215  # Amount of catchments in the directory

    new_metadata, flow_cubic_meters_ps = process_flow_timeseries_directory(directory, delimiter, catchments_to_do)

    # Save data to CSV files
    new_metadata_df = pd.DataFrame(new_metadata)
    new_metadata_df.to_csv("new_metadata.csv", index=False)

    flow_cubic_meters_ps.to_csv("allDailyFlowData_new.csv", index=False, quoting=False, escapechar='-')

if __name__ == '__main__':
    main()
