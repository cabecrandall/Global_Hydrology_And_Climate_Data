"""
Module to filter final time series down to only the rows
that have data in every column. Nice and simple!
"""
import os
import pandas as pd
from tqdm import tqdm


def filter_series(folder, destination):
    total_files = len(os.listdir(folder))
    empty_files = 0
    if not os.path.exists(destination):
        os.makedirs(destination)
    loop = tqdm(total=len(os.listdir(folder)), position=0, leave=False)
    for file in os.listdir(folder):
        if file.endswith(".csv"):
            path = os.path.join(folder, file)
            frame = pd.read_csv(path)
            frame = frame.dropna()
            if len(frame) > 0:
                frame.to_csv(os.path.join(destination, file), index=False)
            else:
                empty_files += 1
        loop.update(1)

    print(f'{total_files - empty_files} out of {total_files} had data!')


def main():
    filter_series("Flow_TS", "New_Flow_TS")


if __name__ == "__main__":
    main()
    exit(0)

