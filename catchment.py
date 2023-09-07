import pandas as pd




class catchment:
    name = "unnamed"
    data = {}
    catchframe = pd.DataFrame(data)

    # average gap size will be determined by finding the average of a set of gap lengths, and then resetting it
    gapLength = 0
    gapCount = 0
    lengths = []
    # I guess I could make temp, evap, and precip respective objects, but I think I'll be okay like this
    tempCount = 0
    sufficientTemp = False
    tempIsEmpty = True
    tempHasGaps = False
    tempGapCount = 0
    tempAvgGapSizeInDays = 0

    evapCount = 0
    sufficientEvap = False
    evapIsEmpty = True
    evapHasGaps = False
    evapGapCount = 0
    evapAvgGapSizeInDays = 0

    precipCount = 0
    sufficientPrecip = False
    precipIsEmpty = True
    precipHasGaps = False
    precipGapCount = 0
    precipAvgGapSizeInDays = 0

    def __init__(self, ID, catchmentframe):
        self.name = ID
        self.catchframe = catchmentframe
        self.analyze_catchment()

    def analyze_catchment(self):
        f = self.catchframe
        try:
            self.tempCount = f['average temperature (C)'].count()
            self.evapCount = f['ET [kg/m^2/8day]'].count()
            self.precipCount = f['precipitation'].count()
        except:
            pass
        self.process_counts()
        #self.printOptionalReport()

    def process_counts(self):
        if self.tempCount >= 365:
            self.sufficientTemp = True
        if self.tempCount != 0:
            self.tempIsEmpty = False
        self.tempAvgGapSizeInDays, self.tempGapCount, self.tempHasGaps = self.analyze_gaps('average temperature (C)')

        if self.evapCount >= 365:
            self.sufficientEvap = True
        if self.evapCount != 0:
            self.evapIsEmpty = False
        self.evapAvgGapSizeInDays, self.evapGapCount, self.evapHasGaps = self.analyze_gaps('ET [kg/m^2/8day]')

        if self.precipCount >= 365:
            self.sufficientPrecip = True
        if self.precipCount != 0:
            self.precipIsEmpty = False
        self.precipAvgGapSizeInDays, self.precipGapCount, self.precipHasGaps = self.analyze_gaps('precipitation')

        # Figuring out if correlations can be done at all on a catchment
        # (meaning they have data in one or more of the three cardinal statistics)

    def analyze_gaps(self, column):
        for element in self.catchframe[column]:
            if element != None:
                self.lengths.append(self.gapLength)
                self.gapLength = 0
                continue
            else:
                if self.gapLength == 0:
                    self.gapCount = self.gapCount + 1
                    self.gapLength = self.gapLength + 1
                else:
                    self.gapLength = self.gapLength + 1
        finalAverage = self.gapAverage()
        finalCount = self.gapCount
        if finalCount > 0:
            finalYesOrNo = True
        else:
            finalYesOrNo = False
        self.gapLength = 0
        self.gapCount = 0
        self.lengths = []
        return finalAverage, finalCount, finalYesOrNo


    def gapAverage(self):
        total = 0
        for length in self.lengths:
            total += length
        if self.gapCount == 0:
            return None
        return (total / self.gapCount)


    def printOptionalReport(self):
        print("temperature count: ", self.tempCount)
        print("precip count: ", self.precipCount)
        print('evap count: ', self.evapCount, '\n')

        print("amount of gaps in temperature info: ", self.tempGapCount)
        print("average length of gaps in temperature info: ", self.tempAvgGapSizeInDays, '\n')

        if(self.tempIsEmpty):
            print("Where's the temp at???")
        if(self.precipIsEmpty):
            print("Where's the precip at???")
        if (self.evapIsEmpty):
            print("Where's the evap at???\n")

        if (self.tempHasGaps):
            print("temp has gaps!")
        if (self.precipHasGaps):
            print("temp has gaps!")
        if (self.evapHasGaps):
            print("temp has gaps!\n")

        if(self.sufficientTemp):
            print("Enough Temp!")
        else:
            print("not enough temp awwww")

        if (self.sufficientEvap):
            print("Enough Evap!")
        else:
            print("not enough evap awwww")

        if (self.sufficientPrecip):
            print("Enough Precip!\n\n\n")
        else:
            print("not enough precip awwww\n\n\n")

