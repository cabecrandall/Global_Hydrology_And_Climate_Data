import pandas as pd
import indexcatchments
# import catchmentcharts
import Metadata_Transform
import matchcatchments as matcher

# quick class instance setup
i = indexcatchments.indexcatchments()
# chart = catchmentcharts.charts

def makeFlowSeries():
    import Flow_Series_Maker
    Flow_Series_Maker.main()

def main(make_flow_series=False, generate_charts=False):
    """
    The following files are required to run the extraction and compilation of catchment data:
        NOTE: The following files should have catchment IDs,
     - A directory with GRDC catchment flow downloads (raw) OR a .csv file with all desired GRDC catchment time series.
     - A directory with average daily Temperature time series (Celsius) for catchments that match GRDC data (if the match isn't perfect, it will
        not affect the outcome of the compilation beyond data gaps for that catchment). Please name this directory Basin_Temp_TS_for_model.
     - A directory with average daily Precipitation time series (mm) for a series of catchemnts. See temperature instructions above. Please
        name this directory Basin_Precip_TS_for_model.
     - A directory with average daily ET time series (kg/m^2). For assistance with obtaining this data, please see Appendix A.
        Please name this directory Basin_ET_TS_for_model.
     - A directory with average daily PET time series (kg/m^2). For assistance with obtaining this data, please see Appendix A.
        Please name this directory Basin_PET_TS_for_model.

        **OTHER TIPS**
     - Ensure that pandas has been installed as a library in your environment.
     - TQDM as a means of progress reporting is also required.

    """
    if make_flow_series:
        import Flow_Series_Maker
        Flow_Series_Maker.main()
    flow = pd.read_csv("allDailyFlowData_newflow.csv")
    matcher.matchCatchments(flow)





    # metadf  = pd.read_csv("catchmentMetadata.csv")

    # This command below slows the program down by around 10 seconds, so remove it if you're not doing a
    # massive correlation. VVV
    # flowdf = pd.read_csv("allDailyFlowData.csv")


    # MAIN CORRELATION AND VISUALIZATION TOOLS, ACTIVATE AND DEACTIVATE AS NEEDED
    # matcher.matchCatchments(flowdf) Creates catchment files.
    # i.correlateAllCatchments() Does lots of things w
    # chart(include_flow=True) Will be better defined once we find figures that we will uuse for the study!

    #ONE TIME USES:
    # Metadata_Transform.updateMetadata()

    #print(matcher.keeperCats)


    # you could do: you have a dataframe for each catchment,
    #the better way: this column represents the correlation between catchment and something, and the rows are each catchment
    #maybe break it into years, do a separate row


if __name__ == "__main__":
    main()
