import os
import json


ET_ts_path = 'Basin_ET_TS_for_model'
ET_ts_exported = []

for file in os.listdir(ET_ts_path):
  file_path = os.path.join(ET_ts_path,file)
  ET_ts_exported.append(file_path[-11:-4])

with open('archived_results/TS_for_PET.txt', 'w') as location:
  for string in ET_ts_exported:
    location.write(string)
    location.write('\n')

print(len(ET_ts_exported))