"""
This script is a more robust and abstract method
for joining time series data from different sources.
It still requires files to be joined between directories
to have the same name. However, it takes any number of directories
as parameters, input as an array of strings
"""

import pandas as pd
import os
from tqdm import tqdm

def rename_columns_in_directory(directory, old_column_name, new_column_name, new_directory=None):
    loop = tqdm(total=len(os.listdir(directory)), position=0, leave=False)
    for file in os.listdir(directory):
        try:
            if file.endswith(".csv"):
                path = os.path.join(directory, file)
                frame = pd.read_csv(path)
                frame = frame.rename(columns={old_column_name : new_column_name})
                if new_directory is not None:
                    output_path = os.path.join(new_directory, file)
                    frame.to_csv(output_path, index=False)
                else:
                    frame.to_csv(path, index=False)
                loop.update(1)
        except:
            print("Error processing file: " + file)
            loop.update(1)

def joiner(directories, output_folder):
    exception_directory = directories[0]
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # Iterate through the files in the first directory
    loop = tqdm(total=len(os.listdir(directories[0])), position=0, leave=False)
    for file in os.listdir(directories[0]):
        # Only process the csv files
        if file.endswith(".csv"):
            try:
                # Read the file
                path = os.path.join(directories[0], file)
                frame = pd.read_csv(path)
                frame = frame.set_index("Date")
                # Iterate through the other directories
                for directory in directories[1:]:
                    exception_directory = directory
                    # Read the file
                    path = os.path.join(directory, file)
                    temp_frame = pd.read_csv(path)
                    temp_frame = temp_frame.set_index("Date")
                    # Merge the frames on the date column
                    frame = pd.merge(frame, temp_frame, on='Date', how='left')
                # Write the joined frame to the output folder
                output_path = os.path.join(output_folder, file)
                frame = frame.dropna()
                frame = frame.rename(columns={'Daily Average LST [C]' : 'average temperature (C)'})
                frame = frame.reset_index()
                frame.to_csv(output_path, index=False)
            except Exception as e:
                print("Error processing file: " + exception_directory + "/" + file)
        loop.update(1)

def main():
    # rename_columns_in_directory("Precip_TS", "date", "Date", "New_Precip_TS")

    directories_to_join = ["Temp_TS_Filled",
                           "Precip_TS",
                           "ET_TS",
                           "PET_TS"]

    joiner(directories_to_join, "GAGES_TS")

if __name__ == "__main__":
    main()
