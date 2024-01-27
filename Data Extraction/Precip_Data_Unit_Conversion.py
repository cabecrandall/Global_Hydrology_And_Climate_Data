import pandas as pd
import os
from tqdm import tqdm
directory = 'Basin_Precip_TS_for_model'
metadata = pd.read_csv('archived_results/catchmentMetadata.csv')



def main():
    num = 0
    loop = tqdm(total=4490) # number manually extracted using my handy mac's Finder
    catchments_without_match = []
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        catchment_id = file_path[-11:-4]

        # Get the row with the catchment area from the metadata thingy
        try:
            catchment_area = metadata.loc[metadata['Catchment ID'] == int(catchment_id), 'Catchment Area'].values[0]
            # TODO: model catchment is ID 4127200
            print(catchment_area)
            df = pd.read_csv(file_path)
            KILOMETERS_PER_MILIMETER = 1e-6
            LITERS_PER_CUBIC_KILOMETER = 1e12

            mega_constant = (KILOMETERS_PER_MILIMETER * LITERS_PER_CUBIC_KILOMETER)
            mega_constant = mega_constant * catchment_area
            print(mega_constant)


            df['precipitation'] = df['precipitation'].mul(mega_constant)
            output_path = "Precip_Totals_Per_Catchment/" + file
            df.to_csv(output_path, index=False)

            df['precipitation'] = df['precipitation'].div()

            print(df)
        # if num == 1:
        #     break

        except Exception:
            pass




if __name__ == '__main__':
    main()

