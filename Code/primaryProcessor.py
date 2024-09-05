import pandas as pd
import numpy as np
import os

class Processing:

    def __init__(self, mouseDF, keyboardDF, sessionNumber, timeOfDay, sessionTime):
        self.sessionNumber = sessionNumber

        self.sessionTime = sessionTime

        self.timeOfDay = self.determineTimeOfDay(timeOfDay.time().hour)
        self.weekDay = timeOfDay.weekday()

        self.mouseDF = mouseDF
        self.keyboardDF = keyboardDF
        self.combinedDF = pd.DataFrame( columns= ["objectType","startTime", "endTime", "inactivityDuration"])
        self.mouseRolling = pd.DataFrame(columns= ["uniqueCounter"])
        self.keyboardRolling = pd.DataFrame(columns = ["uniqueCounterKeys"])

        self.uniqueKeyboardCounter = 1
        self.uniqueMouseCounter = 1

    def determineTimeOfDay(self, hourOfSession):
        if hourOfSession < 6:
            return 1
        elif hourOfSession < 12:
            return 2
        elif hourOfSession < 18:
            return 3
        else:
            return 4

    def processMouse(self, objectOfInterest):
        objectOfInterest.calculateVals()
        mathdict = {
                    "uniqueCounter" : self.uniqueMouseCounter,
                    "objectType" : "Mouse",
                    "MAverageSpeed" : objectOfInterest.averageSpeed,
                    "MmovementAccuracy" : objectOfInterest.movementAccuracy,
                    "MclickingAccuracy" : objectOfInterest.clickingAccuracy,
                    "DirectionChanges" : objectOfInterest.directionChanges,
                    "startTime" : objectOfInterest.mouseStartingTime, 
                    "endTime" : objectOfInterest.mouseEndingTime,
                    "sessionNumber" : self.sessionNumber,
                    "timeOfDay" : self.timeOfDay,
                    "weekDay" : self.weekDay
                    }
        self.uniqueMouseCounter += 1
        self.mouseDF = pd.concat([self.mouseDF, pd.DataFrame([mathdict])], axis = 0, ignore_index= True)

    def processKeyboard(self, objectOfInterest):
        objectOfInterest.calculateVals()
        mathdict = {
                    "uniqueCounterKeys" : self.uniqueKeyboardCounter,
                    "objectType" : "Cluster",
                    "kSpeed" : objectOfInterest.speedPerCluster,
                    "kAccuracy" : objectOfInterest.typingAccuracy,
                    "avgTime" : objectOfInterest.avgTime,
                    "ClusterLength" : objectOfInterest.numberOfKeys,
                    "startTime" : objectOfInterest.clusterStartTime, 
                    "endTime" : objectOfInterest.clusterEndTime,
                    "sessionNumber" : self.sessionNumber,
                    "timeOfDay" : self.timeOfDay,
                    "weekDay" : self.weekDay
                     }
        self.keyboardDF = pd.concat([self.keyboardDF, pd.DataFrame([mathdict])], axis = 0, ignore_index= True)
        self.uniqueKeyboardCounter += 1


    def calculateSlope(self, x, y):

        xMean = np.mean(x)
        yMean = np.mean(y)

        try:
            return (np.sum((x- xMean)*(y - yMean))) / np.sum((x-xMean)**2)
        except Exception as e:
            return np.nan

    def updateDataFrame(self, df):
        newDF = pd.DataFrame()
        for column in [column for column in df.columns if (column != "startTime")]:
            #so this accesses each column name in the set
            def apply_slope(rolling_window):
                # Calculate the slope using the current rolling window indices
                y_values = df.loc[rolling_window.index, column]
                return self.calculateSlope(rolling_window, y_values)
            
            # Apply the slope calculation to each rolling window
            newDF[f"{column}_Rate"] = df["startTime"].rolling(window=5, min_periods = 2).apply(
                apply_slope, raw=False
            )
        
        return newDF



    
    def mainFunction(self):


        #This combines them and orders them
        self.combinedDF = pd.concat([self.keyboardDF,self.mouseDF], ignore_index = True)
        

        self.combinedDF.sort_values(by = "startTime", inplace= True)

        #calculates all the rates of inactivity
        self.combinedDF["inactivityDuration"] = (self.combinedDF["startTime"].shift(-1) - self.combinedDF["endTime"]).clip(lower = 0)
        
        self.combinedDF.reset_index(drop = True, inplace = True)
        print(self.combinedDF[["objectType", "inactivityDuration"]])
        #creating the separate ones
        tempKeyboard = self.combinedDF[self.combinedDF["objectType"] == "Cluster"][["uniqueCounterKeys", "kSpeed", "kAccuracy", "avgTime", "startTime", "endTime", "ClusterLength", "inactivityDuration", "timeOfDay", "weekDay", "sessionNumber"]].copy()
        tempMouse = self.combinedDF[self.combinedDF["objectType"] == "Mouse"][["uniqueCounter", "startTime", "endTime", "MAverageSpeed", "MmovementAccuracy", "MclickingAccuracy", "DirectionChanges","inactivityDuration", "timeOfDay", "weekDay", "sessionNumber"]].copy()

        #getting the rates for storage lowkey
        newKeyboardRates = pd.concat([tempKeyboard[["uniqueCounterKeys", "startTime", "inactivityDuration", "timeOfDay", "weekDay", "sessionNumber"]].copy(),self.updateDataFrame(tempKeyboard[["startTime","kSpeed","kAccuracy", "avgTime","ClusterLength"]])], axis = 1)
        newMouseRates = pd.concat([tempMouse[["uniqueCounter", "startTime", "inactivityDuration", "timeOfDay", "weekDay","sessionNumber"]].copy(),self.updateDataFrame(tempMouse[["startTime","MAverageSpeed", "MmovementAccuracy", "MclickingAccuracy", "DirectionChanges"]])], axis = 1)

        #getting the keyboard values that have not been added
        self.new_keyboard_rows = newKeyboardRates[~newKeyboardRates["uniqueCounterKeys"].isin(self.keyboardRolling["uniqueCounterKeys"])]
        self.new_mouse_rows = newMouseRates[~newMouseRates["uniqueCounter"].isin(self.mouseRolling["uniqueCounter"])]


        self.keyboardRolling = pd.concat([self.keyboardRolling, self.new_keyboard_rows], ignore_index=True)
        self.mouseRolling = pd.concat([self.mouseRolling, self.new_mouse_rows], ignore_index=True)

    def storeData(self):

        #getting the time into something readable
        self.keyboardRolling["startTime"] = (self.keyboardRolling["startTime"] - self.sessionTime).round(2)
        self.mouseRolling["startTime"] = (self.mouseRolling["startTime"] - self.sessionTime).round(2)
        self.mouseDF["startTime"] = (self.mouseDF["startTime"] - self.sessionTime).round(2)
        self.keyboardDF["startTime"] = (self.keyboardDF["startTime"] - self.sessionTime).round(2)
        
        #getting the rates into a csv
        def df_to_csv(df, name):
            fileName = name + ".csv"
            if os.path.isfile(fileName):
                df.to_csv(path_or_buf = fileName, mode = "a", header = False, index = False)
            else:
                df.to_csv(path_or_buf = fileName, index = False)
        
        #So, now I want to load each of the csv's
        names = ["keyboardRates", "mouseRates", "mouseData", "keyboardData"]
        df_to_csv(self.keyboardRolling, names[0])
        df_to_csv(self.mouseRolling, names[1])
        df_to_csv(self.mouseDF, names[2])
        df_to_csv(self.keyboardDF, names[3]) 








       
    
