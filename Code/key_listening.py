from pynput import keyboard
import time
import numpy as np
import queue

class KeyboardListener:

    class cluster:
        def __init__(self, numberOfKeys, previousClusterEndTime, clusterStartTime, clusterEndTime, numberBackspacesOrDeletes, totalTime):
            self.numberOfKeys = numberOfKeys
            self.previousClusterEndTime = previousClusterEndTime
            self.clusterStartTime = clusterStartTime
            self.clusterEndTime = clusterEndTime
            self.numberBackspacesOrDeletes = numberBackspacesOrDeletes
            self.totalTime = totalTime

            #the values of interest
            self.speedPerCluster = None
            self.typingAccuracy = None
            self.avgTime = None

        def calculateVals(self):
            
            #speed
            clusterLength = self.clusterEndTime - self.clusterStartTime
            if clusterLength > 0:
                self.speedPerCluster = self.numberOfKeys / clusterLength
            else:
                self.speedPerCluster = np.nan

            #accuracy of typing
            self.typingAccuracy = (self.numberOfKeys - self.numberBackspacesOrDeletes) / self.numberOfKeys

            #average time
            self.avgTime = self.totalTime / self.numberOfKeys




    def __init__(self, dataQueue):


        #the variables in ewach cluster object
        self.numberOfKeys = 0
        self.totalTime = 0
        self.clusterStartTime = None
        self.previousClusterEndTime = None
        self.clusterEndTime = None
        self.numberBackspacesOrDeletes = 0

        #other necessary changing values
        self.previousKeyPress = None
        self.currentKeyPress = None

        #the constants
        self.clusterTimeMargin = 1
        self.clusterList = dataQueue
        self.listener = keyboard.Listener(on_press=self.getInput)

    def makeCluster(self):

        self.clusterEndTime = self.previousKeyPress
        
        self.clusterList.put(
            self.cluster(
                numberOfKeys = self.numberOfKeys,
                previousClusterEndTime = self.previousClusterEndTime,
                clusterStartTime= self.clusterStartTime,
                clusterEndTime= self.clusterEndTime,
                numberBackspacesOrDeletes= self.numberBackspacesOrDeletes,
                totalTime= self.totalTime
            )
        )

        self.numberOfKeys = 0
        self.totalTime = 0
        self.previousClusterEndTime = self.clusterEndTime
        self.clusterStartTime = None
        self.clusterEndTime = None
        self.numberBackspacesOrDeletes = 0

     
    def getInput(self, key):

        self.currentKeyPress = time.time()

        #checking to see if there have been other key presses before this
        if self.previousKeyPress:
            timeDifference = self.currentKeyPress - self.previousKeyPress
            
            if timeDifference > self.clusterTimeMargin:
                #this means that it is NOT part of the cluster
                self.makeCluster()
            else:
                self.totalTime += timeDifference

        if not self.clusterStartTime:
            self.clusterStartTime = self.currentKeyPress

        self.previousKeyPress = self.currentKeyPress
        self.numberOfKeys += 1
        if key == keyboard.Key.delete or key == keyboard.Key.backspace:
            self.numberBackspacesOrDeletes += 1
            


    def start(self):
        self.listener.start()
    
    def stop(self):
        
        self.makeCluster()
        self.listener.stop()


if __name__ == "__main__":


    listener2 = KeyboardListener()

    listener2.start()

    

    

    
