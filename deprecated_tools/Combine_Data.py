"""
This file puts both the flow time series and the catchment
metadata files from Travis and from me into two large files.
"""

import pandas as pd
import os
from tqdm import tqdm

def main():
    # This is the metadata file from Travis
    metadata = pd.read_csv('shortened_travis_metadata.csv')
    print("Metadata read")

    # This is the metadata file from me
    my_metadata = pd.read_csv('catchmentMetadata.csv')
    print("My metadata read")

    # This is the flow time series file from Travis
    flow = pd.read_csv('allDailyFlowData_travis.csv')
    print("Travis flow read")

    # This is the flow time series file from me
    my_flow = pd.read_csv('allDailyFlowData.csv')
    print("My flow read")

    new_metadata = my_metadata.merge(metadata, how='outer', on='Catchment ID')
    new_metadata.to_csv('combined_metadata.csv')
    print("Metadata combined")

    new_flow = flow.merge(my_flow, how='outer')
    new_flow.to_csv('combined_flow.csv')
    print("Flow combined")


if __name__ == '__main__':
    main()