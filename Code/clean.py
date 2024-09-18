import pandas as pd
import os
import time

class Processing:

    def __init__(self, mouseDF, keyboardDF, sessionNumber, timeOfDay, sessionTime, completeSessionStart):
        
        self.completeSessionStart = completeSessionStart
        
        self.sessionNumber = sessionNumber

        self.sessionTime = sessionTime

        self.timeOfDay = self.determineTimeOfDay(timeOfDay.time().hour)
        self.weekDay = timeOfDay.weekday()

        self.mouseDF = mouseDF
        self.keyboardDF = keyboardDF
        self.combinedDF = pd.DataFrame( )
        self.mouseRolling = pd.DataFrame(columns= ["uniqueCounter"])
        self.keyboardRolling = pd.DataFrame(columns = ["uniqueCounterKeys"])

        self.uniqueKeyboardCounter = 1
        self.uniqueMouseCounter = 1

        self.fixedActivityTime = self.determineActivityTime()

    def determineActivityTime(self):
        #the amount of fixed activities I have each day
        # Key: Day --- Value: Hours of Fixed Commitments
        activity = {
            0 : 13.5, 1 : 14, 2 : 14, 3 : 16, 4 : 14, 5 : 9.5, 6 : 10.5
        }
        return activity[self.weekDay]

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
                     }
        self.keyboardDF = pd.concat([self.keyboardDF, pd.DataFrame([mathdict])], axis = 0, ignore_index= True)
        self.uniqueKeyboardCounter += 1
    
    def mainFunction(self):

        print(self.keyboardDF.columns)
        print(self.mouseDF.columns)

        currentTime = time.time()

        #taking averages
        keyboardAverages = pd.DataFrame([self.keyboardDF[['kSpeed', 'kAccuracy', 'avgTime', 'ClusterLength']].mean()])
        mouseAvearges = pd.DataFrame([self.mouseDF[['MAverageSpeed','MmovementAccuracy', 'MclickingAccuracy', 'DirectionChanges']].mean()])
        
        #Other values to add
        otherValueDict = {
            "totalWorkingTime" : (currentTime - self.completeSessionStart),
            "sessionLength" : (currentTime - self.sessionTime),
            "sessionNumber" : self.sessionNumber,
            "timeOfDay" : self.timeOfDay,
            "weekDay" : self.weekDay,
            "activityTime" : self.fixedActivityTime
            
        }

        otherValues = pd.DataFrame([otherValueDict])

        #This combines them and orders them
        self.combinedDF = pd.concat([otherValues,keyboardAverages,mouseAvearges], axis = 1).round(2)
        self.combinedDF.reset_index(drop = True, inplace = True)


    def storeData(self):

        #getting the values into a csv
        def df_to_csv(df, name):
            fileName = name + ".csv"
            if os.path.isfile(fileName):
                df.to_csv(path_or_buf = fileName, mode = "a", header = False, index = False)
            else:
                df.to_csv(path_or_buf = fileName, index = False)
        
        #So, now I want to load each of the csv's
        df_to_csv(self.combinedDF, "combined")








       
    