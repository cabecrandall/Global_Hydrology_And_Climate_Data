import matchcatchments as matcher
import pandas as pd
import matplotlib.pyplot as plt
class indexcatchments:
    catchments = []
# TEMP_usable_catchments = []
# PRECIP_usable_catchments = []
# EVAP_usable_catchments = []

    catchments_with_temp_gaps = 0
    catchments_with_precip_gaps = 0
    catchments_with_evap_gaps = 0
    result = pd.DataFrame({'Catchment ID': [], 'Flow/Temp Correlation': [], 'Flow/Precip Correlation': [], 'Flow/Evap Correlation': []})


    def indexCatchment(self, catchment):
        self.catchments.append(catchment)


    def correlateAllCatchments(self):
        for ID in self.catchments:
            self.correlateCatchment(ID)
            self.countGaps(ID)

        self.removeCatchmentsWithoutLocation()
        self.result.to_csv('result.csv', index=False)
        self.printGaps()



    def correlateCatchment(self, ID):
        if (ID.sufficientTemp):
            tempCorrelation = ID.catchframe['flow'].corr(ID.catchframe['average temperature (C)'], method='spearman')
        else:
            tempCorrelation = None

        if (ID.sufficientPrecip):

            precipCorrelation = ID.catchframe['flow'].corr(ID.catchframe['precipitation'], method='spearman')

            # filtered_df = ID.catchframe[ID.catchframe['Date'].dt.year >= 2000]
            #
            # # Generate sample plots, as a unit test!
            # x = filtered_df['Date']
            # y1 = filtered_df['flow']
            # y2 = filtered_df['precipitation']
            #
            # fig, ax1 = plt.subplots()
            # ax2 = ax1.twinx()
            #
            # # Plot the first line on the first y-axis
            # line1 = ax1.plot_date(x, y1, 'b-', label='Flow')
            # ax1.set_ylabel('Flow', color='b')
            # ax1.tick_params('y', colors='b')
            #
            # # Plot the second line on the second y-axis
            # line2 = ax2.plot_date(x, y2, 'g-', label='Precipitation')
            # ax2.set_ylabel('Precipitation', color='g')
            # ax2.tick_params('y', colors='g')
            #
            # # Set labels, title, and legends
            # ax1.set_xlabel('Date')
            # plt.title(precipCorrelation)
            # print(ID.name)
            # plt.show()
        else:
            precipCorrelation = None

        if (ID.sufficientEvap):
            evapCorrelation = ID.catchframe['flow'].corr(ID.catchframe['ET [kg/m^2/8day]'], method='spearman')
        else:
            evapCorrelation = None

        self.attachResult(ID.name, tempCorrelation, precipCorrelation, evapCorrelation)
        #the plan:
    #     Write three functions, and one preliminary one to initialize the results.csv
    # also, this function still does not account for processing gaps. That is still up for my decision
    def attachResult(self, name, temp_correlation, precip_correlation, evap_correlation):

        # Create a five-element tuple
        new_row = (name, temp_correlation, precip_correlation, evap_correlation)

        # Convert the tuple to a DataFrame with one row
        tempFrame = pd.DataFrame([new_row], columns=self.result.columns)

        # Append the new DataFrame to the original DataFrame
        self.result = pd.concat([self.result, tempFrame], ignore_index=True)

    def countGaps(self, ID):
        if ID.tempHasGaps:
            self.catchments_with_temp_gaps += 1
        if ID.precipHasGaps:
            self.catchments_with_precip_gaps += 1
        if ID.evapHasGaps:
            self.catchments_with_evap_gaps += 1

    def printGaps(self):
        print("The number of catchments with gaps in temperature data is ", self.catchments_with_temp_gaps)
        print("The number of catchments with gaps in precipitation data is ", self.catchments_with_precip_gaps)
        print("The number of catchments with gaps in evapotranspiration data is ", self.catchments_with_evap_gaps)

    def removeCatchmentsWithoutLocation(self):
        print(matcher.noLocations)
        self.result = self.result[~self.result['Catchment ID'].isin(matcher.noLocations)]





