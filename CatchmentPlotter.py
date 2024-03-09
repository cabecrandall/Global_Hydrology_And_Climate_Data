import seaborn as sb
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from Data_Processing import GAGES_Helper



def mergeShapesWithVariableColumn(shapes_file, data_file, variable_column, index):
    if variable_column in shapes_file.columns:
        return shapes_file
    else:
        data_to_merge = data_file[[index, variable_column]]
        return pd.merge(shapes_file, data_to_merge, how="left", on=index)






def plotMap(shapefiles_path, stats_file, variables_and_gradients, titles, meta_index='STAID', shapes_index='GAGE_ID'):

    sb.set(style="whitegrid", palette="pastel", color_codes=True)
    sb.mpl.rc("figure", figsize=(10,6))

    outline_df = gpd.read_file("Shapefiles/USA_Contiguous/USA_Contiguous_States.gpkg")
    shapes_df = gpd.read_file(shapefiles_path, bbox=outline_df, converters={shapes_index:str})
    meta_df = pd.read_csv(stats_file, converters={meta_index: str})

    shapes_df = shapes_df.rename(columns={shapes_index:meta_index})

    for variable in list(variables_and_gradients.keys()):
        shapes_df = mergeShapesWithVariableColumn(shapes_df, meta_df, variable, meta_index)

        vmin, vmax = 120, 220
        fig, axis = plt.subplots(figsize=(10, 6))

        # axis.axis('off')
        # axis.set_title(variable)

        # Create colorbar as a legend
        # sm = plt.cm.ScalarMappable(cmap='BuGn', norm = plt.Normalize(vmin=vmin, vmax=vmax))
        # empty array for the data range
        # sm._A = []
        # add the colorbar to the figure
        # fig.colorbar(sm)

        outline_df = outline_df.to_crs(shapes_df.crs)


        axis = outline_df.plot(color="white", edgecolor="black")
        shapes_df.plot(column=variable, cmap=variables_and_gradients[variable], linewidth = 0.01, ax = axis, edgecolor ='0.8', legend=True,
                       missing_kwds={
                           "color": "lightgrey",
                           "edgecolor": "black",
                           "hatch": "///",
                           "label": "Missing values",
                       }
                       )
        plt.axis('off')
        axis.set_title(titles[variable], fontname="Times New Roman", fontsize=20)


        plt.savefig(f"Figures/{variable}_map.png", bbox_inches='tight', dpi=200)


plotMap("Shapefiles/Big GAGES Layer/big_GAGES_layer.shp", "metadata.csv",
        {"AREA": 'plasma', "SNOW_PCT_PRECIP": "BuGn", "PET": "YlOrRd"},
        {"AREA": 'Catchment Area',
         "SNOW_PCT_PRECIP": "Percentage of Precipitation that is Snow",
         "PET": "PET"})

plotMap("Shapefiles/Big GAGES Layer/big_GAGES_layer.shp", "burn_data.csv",
        {"year": 'Purples', "percent_burned": "Oranges"},
        {"year": 'Year of Last Burn',
         "percent_burned": "Percent of Catchment Burned by Last Fire",
         },
        meta_index="GAGE_ID")
