"""
Cannot be run, these functions specific to GAGES
hydrology data may be imported to another module to help
with common inconsistencies in processing the data.
"""

import pandas as pd
import os


"""
takes any df (including GAGES metadata for our purposes) and converts
their default units of square meters to square kilometers.
"""
def column_square_meters_to_square_kilometers(directory, column_name, new_directory=None):
    for file in os.listdir(directory):
        if file.endswith(".csv"):
            path = os.path.join(directory, file)
            frame = pd.read_csv(path)
            frame[column_name] = frame[column_name].div(1e6)
            if new_directory is not None:
                output_path = os.path.join(new_directory, file)
                frame.to_csv(output_path, index=False)
            else:
                frame.to_csv(path, index=False)


def add_leading_zeroes(directory_or_file, column_name, new_directory_or_file=None):
    if os.path.isfile(directory_or_file):
        frame = pd.read_csv(directory_or_file, dtype={column_name: str})
        frame[column_name] = frame[column_name].apply(lambda x: '0' + x if len(x) < 8 else x)
        if new_directory_or_file is not None:
            frame.to_csv(new_directory_or_file, index=False)
        else:
            frame.to_csv(directory_or_file, index=False)
    else:
        directory = directory_or_file
        new_directory = new_directory_or_file
        for file in os.listdir(directory):
            if file.endswith(".csv"):
                path = os.path.join(directory, file)
                frame = pd.read_csv(path)
                frame[column_name] = frame[column_name].apply(lambda x: '{0:0>2}'.format(x))
                if new_directory is not None:
                    output_path = os.path.join(new_directory, file)
                    frame.to_csv(output_path, index=False)
                else:
                    frame.to_csv(path, index=False)
