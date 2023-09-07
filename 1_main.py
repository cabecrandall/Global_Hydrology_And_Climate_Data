import pandas as pd
import indexcatchments
import catchmentcharts
import Metadata_Transform
import matchcatchments as matcher

# quick class instance setups because I'm trash at python
i = indexcatchments.indexcatchments()
chart = catchmentcharts.charts

# USER GUIDE:

# To start, a base directory with raw GRDC flow data is processed using this module:
# import Flow_Series_Maker

# Make sure to set the working directory (however you can do that) the hydrology folder, or
# whatever folder these modules are contained in.
#metadf  = pd.read_csv("catchmentMetadata.csv")

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