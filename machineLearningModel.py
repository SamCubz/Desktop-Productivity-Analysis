from sklearn.linear_model import SGDRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
import pandas as pd


class trainModel:

    def __init__(self, filePath, limit):

        #reads in hte data
        df = pd.read_csv(filePath)
    
        #setting the highest tolerable inactivity time
        self.limit = limit

        #cleaning any empty up rows
        df.dropna(inplace = True)

        #splitting the training data into target and parameters
        x = df.loc[:, df.columns != "inactivityDuration"]
        y = df["inactivityDuration"]
        self.xTrain, self.xTest, self.yTrain, self.yTest = train_test_split(x, y, test_size = 0.25)

        #creating the pipeline to scale and then fit the model
        self.mainPipeline = Pipeline(
            steps = [
                ("scaler", StandardScaler()), #step 1,
                ("regressor", SGDRegressor(
                    #taking in all default values, as I will be using the gridsearch anyway
                ))
            ]
        )

        self.mainPipeline.fit(
            self.xTrain, self.yTrain #fitting the model
        )

        param_grid = {
            'regressor__penalty': ['l2', 'l1', 'elasticnet'],
            'regressor__alpha': [0.00001, 0.0001, 0.001],
            'regressor__learning_rate': ['constant', 'optimal', 'invscaling'],
            'regressor__eta0': [0.001, 0.01, 0.1],
        }

        self.gridSearch = GridSearchCV(estimator= self.mainPipeline, param_grid= param_grid, scoring = "neg_mean_squared_error")

        self.gridSearch.fit(self.xTrain, self.yTrain)

    def predictInactivity(self, df):
        df.dropna()

        #takes the averages of all the new rows
        meanOfNewRows = df.mean(axis = 1)

        #predicts the inactivity duration of the next one
        return self.limit < self.gridSearch.predict( meanOfNewRows.loc[:, meanOfNewRows.columns != "inactivityDuration"] )[0]




