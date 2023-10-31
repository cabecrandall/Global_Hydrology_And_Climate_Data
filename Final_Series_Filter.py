"""
Module to filter final time series down to only the rows
that have data in every column. Nice and simple!
"""
import os
import pandas as pd
from tqdm import tqdm


def filter_final_series(folder, destination):
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
                print("No data for file: " + file)
        loop.update(1)


def main():
    filter_final_series("FilledFinalSeries_unfiltered", "FilledFinalSeries")


if __name__ == "__main__":
    main()
    exit(0)

