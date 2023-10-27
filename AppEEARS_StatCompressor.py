"""
This is a one-time-use tool to extract only the
necessary data from the AppEEARS MOD16A2GF output csv's.
Specifically, each file will be converted to two
time series, one for ET and one for PET.
"""

import os
import pandas as pd
from tqdm import tqdm

def compress_ET_PET_Stats(folder, ET_output_folder, PET_output_folder):
    # Create the output folders if they don't exist
    if not os.path.exists(ET_output_folder):
        os.makedirs(ET_output_folder)
    if not os.path.exists(PET_output_folder):
        os.makedirs(PET_output_folder)
    loop = tqdm(total=len(os.listdir(folder)), position=0, leave=False)
    # Iterate through the files in the folder
    for file in os.listdir(folder):
        # Only process the csv files

        if file.endswith(".csv"):
            try:
                # Read the file
                path = os.path.join(folder, file)
                frame = pd.read_csv(path)
                # Extract the ET and PET columns
                ET_frame = frame[frame["Dataset"] == "ET_500m"]
                PET_frame = frame[frame["Dataset"] == "PET_500m"]
                ET_frame = ET_frame[["Date", "Mean"]]
                PET_frame = PET_frame[["Date", "Mean"]]

                # Write the ET and PET columns to their respective output folders
                ET_path = os.path.join(ET_output_folder, "basin_" + file)
                PET_path = os.path.join(PET_output_folder, "basin_" + file)
                ET_frame.to_csv(ET_path, index=False)
                PET_frame.to_csv(PET_path, index=False)
            except:
                print("Error processing file: " + file)
        loop.update(1)

def main():
    compress_ET_PET_Stats("MOD16A2GF_ET_PET", "Basin_ET_TS", "Basin_PET_TS")

if __name__ == "__main__":
    main()