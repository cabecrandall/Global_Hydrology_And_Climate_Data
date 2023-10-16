import pandas as pd
from tqdm import tqdm

'''
Deprecated module for converting flow data to units needed for runoff studies (L/Day and L/Day/km^2)
'''
flow_data = pd.read_csv('allDailyFlowData_new.csv')
metadata = pd.read_csv('archived_results/catchmentMetadata.csv')
flow_data_L_D = pd.read_csv('allDailyFlowInLitersPerDay.csv')

# This was done because of a clerical error on my part. it should not be
# necessary, but if it is, just un-comment it! It converts the date column
# into a valid format.
flow_data['Date'] = flow_data['Date'].str.replace('--', '-')

# The raw flow data is in cubic meters per second, but in the interest of the study,
# it must be converted to Liters per day, done here.
# For reference, there are 1000 liters in a cubic meter and 86400 seconds in a day,
# hence the conversion.
loop = tqdm(total=(flow_data.shape[1] - 1))
flow_data_L_D = flow_data
for column in flow_data_L_D:
    if column != 'Date':
        flow_data_L_D[column] = flow_data_L_D[column].mul(86400000)
        loop.update(1)
flow_data_L_D.to_csv('allDailyFlowInLitersPerDay.csv')

loop = tqdm(total=(flow_data_L_D.shape[1] - 1))
# Now, I need to fetch the catchment size from the metadata
for column in flow_data_L_D.columns:
    if column != "Date":
        catchment_area = metadata.loc[metadata['Catchment ID'] == column, 'Catchment Area'].values[0]
        flow_data_L_D[column] = flow_data_L_D[column].div(catchment_area)
        loop.update(1)

flow_data_L_D.to_csv('allDailyFlowInLitersPerDayPerSqKm.csv', index=False)

# flow_data.to_csv('allDailyFlowData_new_v2.csv', index=False)
