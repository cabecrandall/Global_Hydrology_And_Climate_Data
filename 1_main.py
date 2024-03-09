import pandas as pd
# import indexcatchments
# import catchmentcharts
# import matchcatchments as matcher
from Data_Processing import Series_Filter, Timeseries_Joiner
from Data_Processing import Final_Series_Converter

# quick class instance setup
# i = indexcatchments.indexcatchments()
# chart = catchmentcharts.charts

def makeFlowSeries():
    from Data_Processing import Flow_Series_Maker
    Flow_Series_Maker.main()

def main(make_flow_series=False, generate_charts=False, flowdir=None, tempdir=None, precipdir=None, ETdir=None, PETdir=None, dest_dir=None, filter_final=False):
    """
    The following files are required to run the extraction and compilation of catchment data:
        NOTE: The following files should have catchment IDs,
     - A directory with GRDC catchment flow downloads (raw) OR a .csv file with all desired GRDC catchment time series.
     - A directory with average daily Temperature time series (Celsius) for catchments that match GRDC data (if the match isn't perfect, it will
        not affect the outcome of the compilation beyond data gaps for that catchment).
     - A directory with average daily Precipitation time series (mm) for a series of catchemnts. See temperature instructions above.
     - A directory with average daily ET time series (kg/m^2). For assistance with obtaining this data, please see Appendix A.
     - A directory with average daily PET time series (kg/m^2). For assistance with obtaining this data, please see Appendix A.

     Please add these directories as arguments to the main function of this module.


        **OTHER TIPS**
     - Ensure that pandas has been installed as a library in your environment.
     - TQDM as a means of progress reporting is also required.

    """

    dir_dict = {"flow": flowdir, "temp": tempdir, "precip": precipdir, "ET": ETdir, "PET": PETdir, "dest": dest_dir}
    if make_flow_series:
        import Flow_Series_Maker
        Flow_Series_Maker.main()
    # flow = pd.read_csv(flowdir)
    Timeseries_Joiner.main(dir_dict.values(), "GAGES_TS")
    Final_Series_Converter.convert(dest_dir, "metadata.csv", "STAID", 'DRAIN_SQKM')


if __name__ == "__main__":
    main(tempdir="Temp_Series_filled",
         precipdir="Precip_Series",
         ETdir="ET_Series",
         PETdir="PET_Series",
         dest_dir="FinalSeries")
