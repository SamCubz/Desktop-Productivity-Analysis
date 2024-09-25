import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDRegressor
import pickle
import os

class trainLinearModel:

    def __init__(self, mouseFilePath, keyboardFilepath, mouseModelPath, keyboardModelPath):

        #For loading the dataframes
        self.mouseFilePath = mouseFilePath
        self.keyboardFilePath = keyboardFilepath
        self.keyboardDF = pd.DataFrame()
        self.mouseDF = pd.DataFrame()

        self.mouseModelPath = mouseModelPath
        self.keyboardModelPath = keyboardModelPath

        self.bestMouse = None
        self.bestKeyboard = None
        
        self.bestMousePerformance = None
        self.bestKeyboardPerformance = None

    def loadCSVData(self):
        """Getting the CSV data"""

        #loading the CSV's
        self.keyboardDF = pd.read_csv(self.keyboardFilePath)
        self.mouseDF = pd.read_csv(self.mouseFilePath)

        #dropping the null rows
        self.keyboardDF.dropna(inplace = True)
        self.mouseDF.dropna(inplace = True)

        #Getting the data in the correct type
        self.keyboardDF = self.keyboardDF.astype("float")
        self.mouseDF = self.mouseDF.astype("float")

    def fullyTrain(self):
        
        #resetting the dataframes
        self.loadCSVData()

        #organizing the data
        xMouse = self.mouseDF.loc[:, self.mouseDF.columns != "inactivityDuration"]
        xKeyboard = self.keyboardDF.loc[:, self.keyboardDF.columns != "inactivityDuration"]

        yMouse = self.mouseDF["inactivityDuration"]
        yKeyboard = self.keyboardDF["inactivityDuration"]

        #splitting the data into training and testing
        XMtrain, XMtest, YMtrain, YMtest = train_test_split(xMouse, yMouse, test_size= 0.25, random_state= 14)
        XKtrain, XKtest, YKtrain, YKtest = train_test_split(xKeyboard, yKeyboard, train_size=0.25, random_state= 14)

        #establishing pipelines 
        mousePipeline = Pipeline([
                                ("scaler", StandardScaler()),
                                ("regressor", SGDRegressor())
                                ])

        keyboardPipeline = Pipeline([
                                ("scaler", StandardScaler()),
                                ("regressor", SGDRegressor())
                                ])

        #parameters to change
        param_grid = {
            'regressor__penalty': ['l2', 'l1', 'elasticnet'],
            'regressor__alpha': [0.00001, 0.0001, 0.001],
            'regressor__learning_rate': ['constant', 'optimal', 'invscaling'],
            'regressor__eta0': [0.001, 0.01, 0.1],
        }

        #create gridsearch objects
        mouseGrid = GridSearchCV(
                                estimator = mousePipeline,
                                param_grid= param_grid,
                                scoring = "neg_mean_squared_error"
                                )
        
        keyboardGrid = GridSearchCV(
                                estimator = keyboardPipeline,
                                param_grid= param_grid,
                                scoring = "neg_mean_squared_error"
                                )


        mouseGrid.fit(XMtrain, YMtrain)
        keyboardGrid.fit(XKtrain, YKtrain)

        #Getting the best predictor for mouse, and the score
        self.bestMouse = mouseGrid.best_estimator_
        self.bestMousePerformance = self.bestMouse.score(XMtest, YMtest)

        #Getting the best predictor for the keyboard, and the score
        self.bestKeyboard = keyboardGrid.best_estimator_
        self.bestKeyboardPerformance = self.bestKeyboard.score(XKtest, YKtest)

        #Fitting the models
        self.bestMouse.fit(xMouse, yMouse)
        self.bestKeyboard.fit(xKeyboard, yKeyboard)

    def partiallyTrain(self, newMouseData, newKeyboardData):

        #organizing the data
        xMouse = newMouseData.loc[:, newMouseData.columns != "inactivityDuration"]
        xKeyboard = newKeyboardData.loc[:, newKeyboardData.columns != "inactivityDuration"]

        yMouse = newMouseData["inactivityDuration"]
        yKeyboard = newKeyboardData["inactivityDuration"]

        #determining hte learning rates, then decrease them
        mouseLearningRate = self.bestMouse.get_params()['regressor__eta0']
        keyboardLearningRate = self.bestKeyboard.get_params()["regressor__eta0"]

        self.bestMouse.set_params(eta0 = mouseLearningRate * 0.90)
        self.bestKeyboard.set_params(eta0 = keyboardLearningRate * 0.90)

        #partially fit the model
        self.bestMouse.partial_fit(xMouse, yMouse)
        self.bestKeyboard.partial_fit(xKeyboard, yKeyboard)


    def modelToStorage(self):
        
        #put away models
        with open(self.mouseModelPath, "wb") as f:
            pickle.dump(self.bestMouse, f)

        with open(self.keyboardModelPath, "wb") as f:
            pickle.dump(self.bestKeyboard, f)

    def modelFromStorage(self):
        
        #pull out models
        with open(self.mouseModelPath, "rb") as f:
            self.bestMouse = pickle.load(f)
        
        with open(self.keyboardModelPath, "rb") as f:
            self.bestKeyboard = pickle.load(f)

    def estimateInactivityFromMouse(self, mouseData):

        #return the average of the predictions
        return self.bestMouse.predict(mouseData)
    
    def estimateInactivityFromKeyboard(self, keyboarddata):
        
        #return the average of the predictions
        return self.bestKeyboard.predict(keyboarddata)
    
    def startSession(self):
        
        #checking for the filepaths
        try: #this is loading the model, otherwise there is no model
            self.modelFromStorage()
        except Exception as e:
            print("Model does not exist!")
            try: #now just training a model
                self.fullyTrain()
            except:
                print("No data to be read!")

    def endSession(self):
        try:
            self.modelToStorage()
        except Exception as e:
            print("Error loading the model")
