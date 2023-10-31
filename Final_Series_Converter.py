"""
This file converts the final combined series to one or both
universal units of Liters/Day or Liters/Km^2/Day.
"""
import os
import pandas as pd
from tqdm import tqdm
metadata = pd.read_csv('catchmentMetadata.csv')

def toLitersPerDay(directory, destination):
    loop = tqdm(total=len(os.listdir(directory)), position=0, leave=False)
    for file in os.listdir(directory):
        if file.endswith(".csv"):
            ID = file[-11:-4]
            catchment_area = metadata.loc[metadata['Catchment ID'] == int(ID), 'Catchment Area'].values
            if len(catchment_area) == 0:
                print("No catchment area found for ID: " + ID)
                continue
            else:
                catchment_area = catchment_area[0]
            path = os.path.join(directory, file)
            frame = pd.read_csv(path)
            frame['Date'] = pd.to_datetime(frame['Date'])
            # frame['Date'] = frame['Date'].dt.strftime('%m/%d/%Y')
            frame.set_index('Date', inplace=True)
            frame.iloc[:, 0] = frame.iloc[:, 0].mul(86400000)

            # optimized rain to liters per day
            frame.iloc[:, 2] = frame.iloc[:, 2].mul(catchment_area)
            frame.iloc[:, 2] = frame.iloc[:, 2].mul(1000000)

            # optimized ET to liters per day
            frame.iloc[:, 3] = frame.iloc[:, 3].mul(1000000)
            frame.iloc[:, 3] = frame.iloc[:, 3].mul(catchment_area)

            # optimized PET to liters per day
            frame.iloc[:, 4] = frame.iloc[:, 4].mul(1000000)
            frame.iloc[:, 4] = frame.iloc[:, 4].mul(catchment_area)

            frame.rename(columns={'ET [kg/m^2/day]': 'ET', 'PET [kg/m^2/day]': 'PET'}, inplace=True)

            frame.to_csv(os.path.join(destination, file), index=True)


        loop.update(1)


def toLitersPerDayPerSqKm(directory, destination):
    loop = tqdm(total=len(os.listdir(directory)), position=0, leave=False)
    for file in os.listdir(directory):
        if file.endswith(".csv"):
            ID = file[-11:-4]
            catchment_area = metadata.loc[metadata['Catchment ID'] == int(ID), 'Catchment Area'].values
            if len(catchment_area) == 0:
                print("No catchment area found for ID: " + ID)
                continue
            else:
                catchment_area = catchment_area[0]
            path = os.path.join(directory, file)
            frame = pd.read_csv(path)
            frame['Date'] = pd.to_datetime(frame['Date'])
            frame.set_index('Date', inplace=True)
            frame.iloc[:, 0] = frame.iloc[:, 0].mul(86400000)
            frame.iloc[:, 0] = frame.iloc[:, 0].floordiv(catchment_area)

            # optimized rain to liters per day per sq km
            frame.iloc[:, 2] = frame.iloc[:, 2].mul(1000000)

            # optimized ET to liters per day per sq km
            frame.iloc[:, 3] = frame.iloc[:, 3].mul(1000000)

            # optimized PET to liters per day per sq km
            frame.iloc[:, 4] = frame.iloc[:, 4].mul(1000000)

            frame.rename(columns={'ET [kg/m^2/day]': 'ET', 'PET [kg/m^2/day]': 'PET'}, inplace=True)
            frame.to_csv(os.path.join(destination, file), index=True)

        loop.update(1)

def main():
    # toLitersPerDay("FilledFinalSeries", "FilledFinalSeries_LitersPerDay")
    toLitersPerDayPerSqKm("FilledFinalSeries", "FilledFinalSeries_LitersPerDayPerSqKm")


if __name__ == '__main__':
    main()
    exit(0)



