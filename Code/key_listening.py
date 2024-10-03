from pynput import keyboard
import time
import numpy as np
import queue

class KeyboardListener:

    class cluster:
        def __init__(self, numberOfKeys,  clusterStartTime, clusterEndTime, numberBackspacesOrDeletes):
            self.numberOfKeys = numberOfKeys
            self.clusterStartTime = clusterStartTime
            self.clusterEndTime = clusterEndTime
            self.numberBackspacesOrDeletes = numberBackspacesOrDeletes

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
            self.avgTime = clusterLength / self.numberOfKeys




    def __init__(self, dataQueue):


        #the variables in ewach cluster object
        self.numberOfKeys = 0
        self.clusterStartTime = None
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
                    clusterStartTime= self.clusterStartTime,
                    clusterEndTime= self.clusterEndTime,
                    numberBackspacesOrDeletes= self.numberBackspacesOrDeletes,
                )
            )

        self.numberOfKeys = 0
        self.clusterStartTime = None
        self.clusterEndTime = None
        self.numberBackspacesOrDeletes = 0

     
    def getInput(self, key):

        self.currentKeyPress = time.time()

        #checking to see if there have been other key presses before this
        if self.clusterStartTime:
            timeDifference = self.currentKeyPress - self.previousKeyPress
            
            if timeDifference > self.clusterTimeMargin:
                #this means that it is NOT part of the cluster
                self.makeCluster()

        if not self.clusterStartTime:
            self.clusterStartTime = self.currentKeyPress

        self.previousKeyPress = self.currentKeyPress
        self.numberOfKeys += 1
        if key == keyboard.Key.delete or key == keyboard.Key.backspace:
            self.numberBackspacesOrDeletes += 1
            
    def timeOut(self):
        if self.previousKeyPress:
            currentTime = time.time()
            timeDifference = currentTime - self.previousKeyPress
            if timeDifference > self.clusterTimeMargin:
                self.makeCluster()

    def start(self):
        self.listener.start()
    
    def stop(self):
        
        self.timeOut()
        self.listener.stop()

if __name__ == "__main__":

    listener2 = KeyboardListener(queue.Queue())

    listener2.start()

    time.sleep(10)

    listener2.stop()

    if not listener2.clusterList.empty():
            while not listener2.clusterList.empty():
                i = listener2.clusterList.get()
                i.calculateVals()
                print("Typing Speed", i.speedPerCluster, "Number of Keys", i.numberOfKeys, "Average Time", i.avgTime, "Typing accuracy:", i.typingAccuracy)



    
