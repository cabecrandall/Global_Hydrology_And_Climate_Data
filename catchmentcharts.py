import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sea

import matchcatchments as matcher
# from scipy.optimize import curve_fit
from sklearn.gaussian_process import GaussianProcessRegressor
# from sklearn.gaussian_process.kernels import RBF
from sklearn.gaussian_process.kernels import ExpSineSquared
# from sklearn.gaussian_process.kernels import RationalQuadratic
import inflect
import os


class charts:
    metadata = pd.read_csv('archived_results/catchmentMetadata.csv')
    result = pd.read_csv('result.csv')
    flows = pd.DataFrame({})
    includeLatitudes = True

    def __init__(self, **kwargs):
        include_flow = kwargs.get('include_flow', False)
        if include_flow:
            self.flows = pd.read_csv('archived_results/allDailyFlowData.csv')
        self.prepareResult()

    def prepareResult(self):
        # basically, this tacks on the coordinate columns onto the result.
        # "new_lon.x","new_lat.x","�..","grdc_no"
        preparedResult = pd.merge(self.result, self.metadata, on="Catchment ID")
        preparedResult = preparedResult[["Catchment ID", "latitude", "longitude", "Flow/Temp Correlation",
                                         "Flow/Precip Correlation", "Flow/Evap Correlation", "Ecoregion_Name"]]
        # If you want a histogram that puts the correlation in bins based on correlation, separated by hemisphere,
        # use this function!
        # self.makeNorthSouthHistogram(preparedResult)

        # This function is a historic moment for me. It will correlate every correlation with every data point in the five column spread
        # self.infinite_scatters(preparedResult, type='non-linear', order = 5)

        # figuring out what the hecc to do with these dang precip plots:
        # self.correlation_examples(preparedResult, 'evap')
        self.correlation_examples(preparedResult, 'temp')
        # self.correlation_examples(preparedResult, 'precip')



    def correlation_examples(self, frame, type):
        # Just like the outliers, this is an adjustable framework for individual catchments, although
        # This function only prints out a small subset of catchments with correlations that are
        # well within the standard deviation of the distributions we have found in this study.
        column = 'bruh, what are you doing? pick a type'
        if type == 'precip':
            column = 'Flow/Precip Correlation'
        if type == 'evap':
            column = 'Flow/Evap Correlation'
        if type == 'temp':
            column = 'Flow/Temp Correlation'

        counter = 0
        # These are just in case you want to focus in on one hemisphere. You can replace "frame"
        # with one of these dataframes in the 'for' loop below!
        positive_latitudes = frame[frame['latitude'] > 0]
        negative_latitudes = frame[frame['latitude'] < 0]

        for index, row in frame.iterrows():
            # This if statement is key. It will determine how many plots are made. Unless you want code that's
            # going to murder a normal computer, make sure the index is kept under a certain number, since
            # The conditions below are designed to print plots for the vast majority of catchments.
            if counter >= 10:
                break
            value = row[column]
            ID = row['Catchment ID']
            place = row['Ecoregion_Name']
            if type == 'precip':
                if value is not None: # This part (the if's) are the part that you're wanting to be adjusting.
                    if value < 0.3 and value > -0.3:
                        new_frame = matcher.createCatchmentfile(str(ID), self.flows)
                        self.catchment_plotter(new_frame, type, str(ID), place, label='_regular_example_plots')
                        counter += 1
            if type == 'evap':
                if value is not None: # This part (the if's) are the part that you're wanting to be adjusting.
                    if value < 0.7 and value > -0.7:
                        new_frame = matcher.createCatchmentfile(str(ID), self.flows)
                        self.catchment_plotter(new_frame, type, str(ID), place, label='_regular_example_plots')
                        counter += 1
            if type == 'temp':
                if value is not None: # This part (the if's) are the part that you're wanting to be adjusting.
                    if value < 0.6 and value > -0.6:
                        new_frame = matcher.createCatchmentfile(str(ID), self.flows)
                        self.catchment_plotter(new_frame, type, str(ID), place, label='_regular_example_plots')
                        counter += 1


    def correlation_outliers(self, frame, type):
        # An adjustable framework for making charts of correlations in individual catchments!
        # The if parameters below are explained in the specifications of the project, under
        # "Requirements for outliers!"
        if type == 'precip':
            column = 'Flow/Precip Correlation'
        if type == 'evap':
            column = 'Flow/Evap Correlation'
        if type == 'temp':
            column = 'Flow/Temp Correlation'
        positive_latitudes = frame[frame['latitude'] > 0]
        negative_latitudes = frame[frame['latitude'] < 0]

        for index, row in frame.iterrows():
            value = row[column]
            ID = row['Catchment ID']
            place = row['Ecoregion_Name']
            if type == 'precip':
                if value is not None: # This part (the if's) are the part that you're wanting to be adjusting.
                    if value > 0.3 or value < -0.3:
                        new_frame = matcher.createCatchmentfile(str(ID), self.flows)
                        self.catchment_plotter(new_frame, type, str(ID), place)

            if type == 'evap':
                if value is not None: # This part (the if's) are the part that you're wanting to be adjusting.
                    if value > 0.7 or value < -0.7:
                        new_frame = matcher.createCatchmentfile(str(ID), self.flows)
                        self.catchment_plotter(new_frame, type, str(ID), place)
            if type == 'temp':
                if value is not None: # This part (the if's) are the part that you're wanting to be adjusting.
                    if value > 0.6 or value < -0.6:
                        new_frame = matcher.createCatchmentfile(str(ID), self.flows)
                        self.catchment_plotter(new_frame, type, str(ID), place)


    def catchment_plotter(self, frame, type, ID, place, **kwargs):
        label = kwargs.get('label', "_outlier_plots")
        label = type + label
        try:
            os.mkdir(label)
        except:
            pass
        directory = label + '/' + ID + "_flow_" + type + "_correlation.pdf"
        directory = directory.replace(' ', "_")
        type = self.translator(type)

        # Plots the stuff based on the arguments in the correlation_plotter function,
        # only if it is called.
        short_frame = frame[type].notna()
        frame = frame[short_frame]
        x = frame['Date']
        y1 = frame['flow']
        y2 = frame[type]

        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()

        # Plot the first line on the first y-axis
        line1 = ax1.plot_date(x, y1, 'b-', label='Flow')
        ax1.set_ylabel('Flow', color='b')
        ax1.tick_params('y', colors='b')

        # Plot the second line on the second y-axis
        line2 = ax2.plot_date(x, y2, 'g-', label=type)
        ax2.set_ylabel(type, color='g')
        ax2.tick_params('y', colors='g')

        # Set labels, title, and legends
        ax1.set_xlabel('Date')
        title = str(place) + ' ' + str(frame['flow'].corr(frame[type], method='spearman'))
        plt.title(title)
        plt.savefig(directory)
        plt.show()

        # TODO: For tomorrow, make sure you make some other folders with normal (0 correlation) catchments
        # to compare the ones you made today. Then, get to reading, big boyyyy!



    def translator(self, type):
        # just makes it easier to make arguments for correlation functions above
        if type == 'temp':
            #average temperature (C),precipitation,ET [kg/m^2/8day]
            type = 'average temperature (C)'
            return type
        if type == 'precip':
            type = 'precipitation'
            return type
        if type == 'evap':
            type = 'ET [kg/m^2/8day]'
            return type

    def makeNorthSouthHistogram(self, frame):
        # Split the data into positive and negative latitude rows
        positive_latitudes = frame[frame['latitude'] > 0]
        negative_latitudes = frame[frame['latitude'] < 0]
        # Temp/Flow Correlation,Temp/Precip Correlation,Temp/Evap Correlation
        # Create a histogram with two colored bars
        plt.hist([positive_latitudes['Flow/Temp Correlation'], negative_latitudes['Flow/Temp Correlation']],
                 bins=20, color=['blue', 'red'], label=['Northern Hemisphere', 'Southern Hemisphere'])

        # Set plot title and labels
        plt.title("Effects of Temperature on Flow, according to north-south orientation")
        plt.xlabel("Correlation")
        plt.ylabel("Frequency")
        plt.savefig("Flow_Temperature_Correlation.pdf")

        plt.show()

        plt.hist([positive_latitudes['Flow/Precip Correlation'], negative_latitudes['Flow/Precip Correlation']],
                 bins=20, color=['blue', 'red'], label=['Northern Hemisphere', 'Southern Hemisphere'])

        # Set plot title and labels
        plt.title("Effects of Precipitation on Flow, according to north-south orientation")
        plt.xlabel("Correlation")
        plt.ylabel("Frequency")
        plt.savefig("Flow_Precipitation_Correlation.pdf")

        plt.show()

        plt.hist([positive_latitudes['Flow/Evap Correlation'], negative_latitudes['Flow/Evap Correlation']],
                 bins=20, color=['blue', 'red'], label=['Northern Hemisphere', 'Southern Hemisphere'])

        # Set plot title and labels
        plt.title("Effects of Evapotranspiration on Flow, according to north-south orientation")
        plt.xlabel("Correlation")
        plt.ylabel("Frequency")
        plt.savefig("Flow_Evapotranspiration_Correlation.pdf")

        plt.show()

        # Make a scatter plot, with the latitude on the x-axis and the other thing on the y-axis
        # Also, a scatter plot comparing literally every line of data that I already have, while simultaneously adding
        # More data. Mainly comparing correlations with each other, or comparing correlation-latitude correelations
        # with other correlations, etc.

    def infinite_scatters(self, frame, **kwargs):
        type = kwargs.get('type', 'linear')
        order = kwargs.get('order', 1)
        # change this directory to the folder/path where you want scatter plots to go to, so that
        # you can test different types of plots and regressions! VVV

        # This bad boy is a fun one. It iteratively makes scatter plots between every column in a given result file.
        try:
            scatter = pd.read_csv("main_stats.csv")
        except:
            scatter = frame[["latitude", "longitude", "Flow/Temp Correlation",
                                         "Flow/Precip Correlation", "Flow/Evap Correlation"]]

        base_list = scatter.columns.to_list()
        # base_list.remove("Catchment ID")
        remaining_list = base_list
        # print lines to make sure these are iterating over the right columns
        # print(base_list)
        # print(remaining_list)
        # print()

        for i in base_list:
            for j in remaining_list:
                if i != j:
                    pdf_name, graph_name, column_name, directory = self.create_names(i, j, order)

                    if type == 'linear':
                        print(pdf_name, ": ", frame[i].corr(frame[j], method='spearman'))
                        print()
                        sea.lmplot(x=i, y=j, data=frame, fit_reg='True', line_kws={'color': 'red'})
                    if type == 'gaussian':
                        self.gaussian_process_regression(frame, i, j)
                    if type == 'non-linear':
                        # plot data
                        self.non_linear_regression(frame, i, j, order)

                    # Set plot title and labels

                    # plt.figure(figsize=(10,6))
                    # plt.title(graph_name)
                    name = directory + pdf_name
                    plt.xlabel(i)
                    plt.ylabel(j)
                    plt.autoscale()
                    plt.tight_layout()
                    plt.savefig(name)
                    plt.show()

            remaining_list.remove(i)

    def gaussian_process_regression(self, frame, i, j):
        print('bruh')
        frame = self.reduce_columns(frame, i, j)
        # Experimental Kernels, honestly i don't know how the frick these work.
        kernel = ExpSineSquared(length_scale=1, periodicity=1, length_scale_bounds=(1e-05, 5))
        #kernel = 1.0 * RBF(length_scale=1.0, length_scale_bounds=(1e-05, 100.0))
        X = frame[i].values.reshape(-1, 1)
        y = frame[j].values
        gpr = GaussianProcessRegressor(kernel=kernel, alpha=5)
        gpr.fit(X, y)
        x_pred = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)  # Generate 100 data points for prediction
        y_pred, y_std = gpr.predict(x_pred, return_std=True)  # Predict the output and get the standard deviation
        plt.scatter(X, y, color='blue', label='Data')
        plt.plot(x_pred, y_pred, color='red', label='Gaussian Process Regression')
        plt.legend()
        plt.fill_between(x_pred.flatten(), y_pred - y_std, y_pred + y_std, color='gray', alpha=0.2, label='Uncertainty')


    def non_linear_regression(self, frame, i, j, order):
        frame['Latitude Category'] = frame['latitude'].apply(lambda x: 'Northern Hemisphere' if x >= 0 else 'Southern Hemisphere')
        if self.includeLatitudes:
            sea.lmplot(x=i, y=j, data=frame, legend=False, hue='Latitude Category', fit_reg='True', order=order, ci=None)
        else:
            sea.lmplot(x=i, y=j, data=frame, fit_reg='True', line_kws={'color': 'red'}, order=order, ci=None)



    def reduce_columns(self, frame, i, j):
        better_frame = frame.dropna(subset=[i, j], how='any')
        return better_frame


    def create_names(self, i, j, order):
        engine = inflect.engine()
        pdf_name = i + '_and_' + j + '_scatterplot.pdf'
        pdf_name = pdf_name.replace('/', '_')
        pdf_name = pdf_name.replace(' ', '_')

        directory = engine.ordinal(order) + "_order_regressions/"
        directory = directory.replace(' ', '_')
        try:
            os.mkdir(directory)
        except:
            pass

        graph_name = 'Correlation Between ' + i + " and " + j
        column_name = i + " and " + j + " Correlation"

        return pdf_name, graph_name, column_name, directory
