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

def convert_8day_to_daily(folder, destination, date_col="Date", pet_prefix=""):
    if not os.path.exists(destination):
        os.makedirs(destination)
    loop = tqdm(total=len(os.listdir(folder)), position=0, leave=False)
    for file in os.listdir(folder):
        if file.endswith(".csv"):
            path = os.path.join(folder, file)
            frame = pd.read_csv(path)
            frame[date_col] = pd.to_datetime(frame[date_col])
            frame = frame.set_index(date_col)
            frame = frame.mul(0.1) # see user guide
            # Extend the frame to have a row for each day
            frame = frame.resample("D").asfreq()
            frame = frame.bfill()
            frame = frame.iloc[2:, :]
            frame['week_number'] = frame.index.isocalendar().week
            frame['week_number'] = frame['week_number'].mul(frame.index.isocalendar().year)
            # Divide groups of 8 identical values by 8,
            # and groups of 5 by 5 and 6 by 6.
            # This is done by grouping by the index
            # and dividing the groups by the length of the group
            frame = frame.groupby(['week_number']).transform(lambda x: x / len(x))
            frame = frame[[f'Region {pet_prefix}ET [kg/m^2/8day]']]
            frame = frame.rename(columns={f'Region {pet_prefix}ET [kg/m^2/8day]': f'{pet_prefix}ET [kg/m^2/day]'})
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


def main(ET_directory, PET_directory):
    convert_8day_to_daily(ET_directory, "ET_TS", date_col="Unnamed: 0")
    convert_8day_to_daily(PET_directory, "PET_TS", date_col="Unnamed: 0", pet_prefix="P")
    # rename_ET_to_PET("PET_TS")



if __name__ == "__main__":
    main("ET_TS_unfilled", "PET_TS_unfilled")
    exit(0)
