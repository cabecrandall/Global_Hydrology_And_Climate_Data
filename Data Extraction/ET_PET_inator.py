"""
This file converts 8-day time series to daily time series
by dividing the 8-day value by 8 and filling in the
with the divided value for each day in the 8-day period.
However, the last period is only 5 days (or 6 on leap years),
so the last period is divided by 5 (or 6) and filled in
"""

import os
import pandas as pd

from tqdm import tqdm

def convert_8day_to_daily(folder, destination):
    loop = tqdm(total=len(os.listdir(folder)), position=0, leave=False)
    for file in os.listdir(folder):
        if file.endswith(".csv"):
            path = os.path.join(folder, file)
            frame = pd.read_csv(path)
            frame["Date"] = pd.to_datetime(frame["Date"])
            frame = frame.set_index("Date")
            # Extend the frame to have a row for each day
            frame = frame.resample("D").asfreq()
            frame = frame.ffill()
            frame['week_number'] = frame.index.isocalendar().week
            frame['week_number'] = frame['week_number'].mul(frame.index.isocalendar().year)
            # Divide groups of 8 identical values by 8,
            # and groups of 5 by 5 and 6 by 6.
            # This is done by grouping by the index
            # and dividing the groups by the length of the group
            frame = frame.groupby(['week_number']).transform(lambda x: x / len(x))
            frame = frame[['Mean']]
            frame = frame.rename(columns={'Mean': 'ET [kg/m^2/day]'})
            frame = frame.reset_index()
            frame.to_csv(os.path.join(destination, file), index=False)
        loop.update(1)


def rename_ET_to_PET(folder):
    loop = tqdm(total=len(os.listdir(folder)), position=0, leave=False)
    for file in os.listdir(folder):
        if file.endswith(".csv"):
            path = os.path.join(folder, file)
            frame = pd.read_csv(path)
            frame = frame.rename(columns={'ET [kg/m^2/day]': 'PET [kg/m^2/day]'})
            frame.to_csv(path, index=False)
        loop.update(1)
def main():
    # convert_8day_to_daily("Basin_ET_TS", "Basin_ET_TS_for_model")
    # convert_8day_to_daily("Basin_PET_TS", "Basin_PET_TS_for_model")
    rename_ET_to_PET("Basin_PET_TS_for_model")


if __name__ == "__main__":
    main()
    exit(0)
