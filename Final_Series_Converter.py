"""
This file converts the final combined series to one or both
universal units of Liters/Day or Liters/Km^2/Day.
"""
import os
import pandas as pd
from tqdm import tqdm





def longest_numeric_substring(string):
    longest = 0
    current = 0
    for char in string:
        if char.isnumeric():
            current += 1
        else:
            if current > longest:
                longest = current
            current = 0
    return longest

def toLitersPerDay(directory, destination, metadata, metadata_id_column, metadata_area_column,
                   ignore_columns=[]):
    loop = tqdm(total=len(os.listdir(directory)), position=0, leave=False)
    for file in os.listdir(directory):
        if file.endswith(".csv"):
            ID = longest_numeric_substring(file)
            catchment_area = metadata.loc[metadata[metadata_id_column] == ID, metadata_area_column].values
            if len(catchment_area) == 0 or not catchment_area[0] > 0:
                print("No catchment area found for ID: " + str(ID))
                continue
            else:
                catchment_area = catchment_area[0]
            path = os.path.join(directory, file)
            frame = pd.read_csv(path)
            frame['Date'] = pd.to_datetime(frame['Date'])
            # frame['Date'] = frame['Date'].dt.strftime('%m/%d/%Y')
            LITERS_PER_CUBIC_METER = 1000
            SECONDS_PER_DAY = 86400

            frame.set_index('Date', inplace=True)

            if "flow" not in ignore_columns:
                frame.iloc[:, 0] = frame.iloc[:, 0].mul(LITERS_PER_CUBIC_METER * SECONDS_PER_DAY) # flow to liters per day

            KILOMETERS_PER_MILIMETER = 1e-6
            LITERS_PER_CUBIC_KILOMETER = 1e12

            if "precipitation" not in ignore_columns:
                precip_conversion_factor = (KILOMETERS_PER_MILIMETER * LITERS_PER_CUBIC_KILOMETER)
                # optimized rain to liters per day
                frame["precipitation"] = frame["precipitation"].mul(catchment_area)
                frame["precipitation"] = frame["precipitation"].mul(precip_conversion_factor)

            KILOGRAM_TO_LITERS = 1
            SQUARE_METERS_PER_SQUARE_KILOMETER = 1e6

            if "ET" not in ignore_columns:
                # optimized ET to liters per day
                frame["ET [kg/m^2/day]"] = frame["ET [kg/m^2/day]"].mul(SQUARE_METERS_PER_SQUARE_KILOMETER * KILOGRAM_TO_LITERS)
                frame["ET [kg/m^2/day]"] = frame["ET [kg/m^2/day]"].mul(catchment_area)

            if "PET" not in ignore_columns:
                # optimized PET to liters per day
                frame["PET [kg/m^2/day]"] = frame["PET [kg/m^2/day]"].mul(SQUARE_METERS_PER_SQUARE_KILOMETER * KILOGRAM_TO_LITERS)
                frame["PET [kg/m^2/day]"] = frame["PET [kg/m^2/day]"].mul(catchment_area)

            frame.rename(columns={'ET [kg/m^2/day]': 'ET', 'PET [kg/m^2/day]': 'PET'}, inplace=True)

            frame.to_csv(os.path.join(destination, file), index=True)


        loop.update(1)


def toLitersPerDayPerSqKm(directory, destination, metadata, metadata_id_column, metadata_area_column,
                          ignore_columns=[]):
    loop = tqdm(total=len(os.listdir(directory)), position=0, leave=False)
    for file in os.listdir(directory):
        if file.endswith(".csv"):
            ID = longest_numeric_substring(file)
            catchment_area = metadata.loc[metadata[metadata_id_column] == ID, metadata_area_column].values
            if len(catchment_area) == 0 or not catchment_area[0] > 0:
                print("No catchment area found for ID: " + str(ID))
                continue
            else:
                catchment_area = catchment_area[0]
            path = os.path.join(directory, file)
            frame = pd.read_csv(path)
            frame['Date'] = pd.to_datetime(frame['Date'])
            frame.set_index('Date', inplace=True)

            # optimized flow to liters per day per sq km
            if "flow" not in ignore_columns:
                frame.iloc[:, 0] = frame.iloc[:, 0].mul(86400000)
                frame.iloc[:, 0] = frame.iloc[:, 0].floordiv(catchment_area)

            if "precipitation" not in ignore_columns:
                # optimized rain to liters per day per sq km
                frame.iloc[:, 2] = frame.iloc[:, 2].mul(1000000)

            if "ET" not in ignore_columns:
                # optimized ET to liters per day per sq km
                frame.iloc[:, 3] = frame.iloc[:, 3].mul(1000000)

            if "PET" not in ignore_columns:
                # optimized PET to liters per day per sq km
                frame.iloc[:, 4] = frame.iloc[:, 4].mul(1000000)

            frame.rename(columns={'ET [kg/m^2/day]': 'ET', 'PET [kg/m^2/day]': 'PET'}, inplace=True)
            frame.to_csv(os.path.join(destination, file), index=True)

        loop.update(1)

def Unit_Conversion_Verifier(directory):
    loop = tqdm(total=len(os.listdir(directory)), position=0, leave=False)
    deficits = pd.DataFrame(columns=['Catchment ID', 'Deficit Percentage'])
    for file in os.listdir(directory):
        if file.endswith(".csv"):
            path = os.path.join(directory, file)
            frame = pd.read_csv(path)
            frame['Date'] = pd.to_datetime(frame['Date'])
            frame.set_index('Date', inplace=True)
            precip_mean = frame.iloc[:, 2].mean()
            ET_mean = frame.iloc[:, 3].mean()
            flow_mean = frame.iloc[:, 0].mean()
            deficit = precip_mean - ET_mean - flow_mean
            deficit_percentage = deficit / precip_mean
            ID = file[-11:-4] # maybe longest numeric substring in future
            deficits = deficits.append({'Catchment ID': ID, 'Deficit Percentage': deficit_percentage * 100}, ignore_index=True)
        loop.update(1)
    deficits.to_csv('Deficit_Percentages.csv', index=False)

# def main():
#     toLitersPerDay("FilledFinalSeries", "FilledFinalSeries_LitersPerDay")
#     toLitersPerDayPerSqKm("FilledFinalSeries", "FilledFinalSeries_LitersPerDayPerSqKm")
    # Unit_Conversion_Verifier("FilledFinalSeries_LitersPerDayPerSqKm")

def convert(directory, metadata_path, metadata_id_column, metadata_area_column):
    metadata = pd.read_csv(metadata_path)
    verify_column_type(metadata, metadata_id_column, str)
    toLitersPerDay(directory, directory + "_LitersPerDay", metadata, metadata_id_column,
                   metadata_area_column, ignore_columns=["flow"])
    toLitersPerDayPerSqKm(directory, directory + "_LitersPerDayPerSqKm", metadata, metadata_id_column,
                          metadata_area_column, ignore_columns=["flow"])

if __name__ == '__main__':
    # Unit_Conversion_Verifier("FilledFinalSeries_LitersPerDayPerSqKm")
    convert("GAGES_TS", "GAGES_Metadata.csv", "GAGE_ID", "AREA")
    exit(0)



