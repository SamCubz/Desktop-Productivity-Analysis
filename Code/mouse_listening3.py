from pynput import mouse
import time
import numpy as np
import math
import queue
import copy

class MouseListening:

    class mouseMove:

        def __init__(self, mouseStartingCoordinate,  mouseStartingTime, totalSpeed, totalDistance , numberOfMoves, numberOfClicks, MouseEndingCoordinates, mouseEndingTime, directionChanges):

            self.mouseStartingCoordinate = mouseStartingCoordinate
            self.mouseStartingTime = mouseStartingTime

            self.MouseEndingCoordinates = MouseEndingCoordinates
            self.mouseEndingTime = mouseEndingTime

            self.totalSpeed = totalSpeed
            self.totalDistance = totalDistance
            self.numberOfMoves = numberOfMoves
            self.numberOfClicks = numberOfClicks

            self.directionChanges = directionChanges

            #valuse we want calculated
            self.averageSpeed = None
            self.movementAccuracy = None
            self.clickingAccuracy = None

        def calculateVals(self):

            
            #calculating the average speed
            if self.numberOfMoves > 0:
                self.averageSpeed = self.totalSpeed / self.numberOfMoves
            else:
                self.averageSpeed = np.nan

            #calculating the movement accuracy
            if self.totalDistance > 0:
                """Sometimes these are not subscriptable"""
                idealDistance = math.sqrt( (self.mouseStartingCoordinate[0] - self.MouseEndingCoordinates[0]) ** 2 + (self.mouseStartingCoordinate[1] - self.MouseEndingCoordinates[1]) **2)
                self.movementAccuracy = idealDistance / self.totalDistance
                self.directionChanges = self.directionChanges / self.totalDistance
            else:
                self.movementAccuracy = None
                self.directionChanges = None

            #calculating the clicking acuracy
            if self.numberOfClicks > 0:
                    self.clickingAccuracy = 1 / self.numberOfClicks
            else:
                    self.clickingAccuracy = 0

    def __init__(self, dataQueue):

        #general action variables
        self.previousActionTime = None
        self.previousActionCoor = None
        self.startingCoordinates = None
        self.startingTime = None

        #movement variables
        self.totalDistance = 0
        self.totalSpeed = 0
        self.directionChanges = 0
        self.direction = None
        self.numberOfMoves = 0
        self.previousMovementTime = None

        #clicking variables
        self.numberOfClicks = 0
        self.previousClickTime = None
        self.previousClickCoords = None
        self.doubleClick = False
        
        #margins
        self.timeOutMargin = 1
        self.doubleClickMargin = 0.5

        #creating the queue
        self.mouseHolder = dataQueue

        #Listener
        self.listener = mouse.Listener(on_move= self.onMove, on_click = self.onClick)


    def start(self):
        self.listener.start()

    def createMouseObject(self):
        self.mouseHolder.put(
            self.mouseMove(
                mouseStartingCoordinate= self.startingCoordinates,
                mouseStartingTime= self.startingTime,
                totalSpeed= self.totalSpeed,
                totalDistance=self.totalDistance,
                numberOfMoves= self.numberOfMoves,
                numberOfClicks= self.numberOfClicks,
                MouseEndingCoordinates=self.previousActionCoor,
                mouseEndingTime= self.previousActionTime,
                directionChanges= self.directionChanges
            )
        )
        #resetting the variables
        self.startingCoordinates = None
        self.startingTime = None
        self.totalSpeed = 0
        self.totalDistance = 0
        self.numberOfMoves = 0
        self.numberOfClicks = 0
        self.directionChanges = 0
        self.direction = None

    def calculateDirectionChanges(self, x, y):
        xChange = x - self.previousActionCoor[0]
        ychange = y - self.previousActionCoor[1]
        if self.direction:
            if (xChange < 0 and self.direction[0] > 0) or (xChange > 0 and self.direction[0] < 0):
                self.directionChanges += 1
            if (ychange < 0 and self.direction[1] > 0) or (ychange > 0 and self.direction[1] < 0):
                self.directionChanges += 1 

        self.direction = [0,0]
        if xChange > 0:
            self.direction[0]  = 1
        else:
            self.direction[0] = -1
        if ychange > 0:
            self.direction[1] = 1
        else:
                self.direction[1] = -1

    def onMove(self, x, y):
       currentTime = time.time()
       if self.previousActionTime: #not the first movement
           #testing compared to the margin
           timeDifference = currentTime - self.previousActionTime
           if self.previousMovementTime:
                movementTimeDifference = currentTime - self.previousMovementTime
           else:
               movementTimeDifference = None
           #calculating the distance traveled
           distance = math.sqrt( (self.previousActionCoor[0] - x)**2 + (self.previousActionCoor[1] - y) ** 2 )
           #calculating the direction changes
           self.calculateDirectionChanges(x,y)
           if timeDifference > 0:
                if timeDifference > self.timeOutMargin:
                    self.createMouseObject()
                if movementTimeDifference: self.totalSpeed += distance / movementTimeDifference
           self.totalDistance += distance
    
       else: #the first movement
           pass
       
       if not self.startingCoordinates:
            self.startingCoordinates = (x,y)
            self.startingTime = currentTime
       
       #setting the previous movements
       self.numberOfMoves += 1
       self.previousMovementTime = currentTime
       self.previousActionTime = currentTime
       self.previousActionCoor = (x,y)


    def onClick(self,x,y, button, pressed):
        #getting the timing or whatever
        currentTime = time.time()
        if pressed:
            #seeing if the movement needs to be started
            if self.previousActionTime:
                if self.previousClickTime:
                    clickTimeDifference = currentTime - self.previousClickTime
                else:
                    clickTimeDifference = None
                totalTimeDifference = currentTime - self.previousActionTime

                #checking if it's timed out
                if totalTimeDifference > self.timeOutMargin:
                    self.createMouseObject()
                if clickTimeDifference and clickTimeDifference < self.doubleClickMargin and self.previousClickCoords and self.previousClickCoords == (x,y) and not self.doubleClick:
                    #this means it's a double click lowkey
                    self.doubleClick = True
                    self.numberOfClicks -= 1
                else:
                    self.doubleClick = False
                
            if not self.startingCoordinates:
                self.startingCoordinates = (x,y)
                self.startingTime = currentTime

            self.numberOfClicks += 1
            self.previousActionTime = currentTime
            self.previousActionCoor = (x,y)
            self.previousClickCoords = (x,y)
            self.previousClickTime = currentTime

        
    def timeOut(self):
        if self.previousActionTime:
            timedifference = time.time() - self.previousActionTime
            if timedifference > self.timeOutMargin:
                self.createMouseObject()
    
    def stop(self):
        self.timeOut()
        self.listener.stop()


if __name__ == "__main__":

    listener2 = MouseListening(queue.Queue())

    listener2.start()

    time.sleep(10)

    listener2.stop()

    if not listener2.mouseHolder.empty():
            while not listener2.mouseHolder.empty():
                i = listener2.mouseHolder.get()
                i.calculateVals()
                print("Starting and Ending Coordinates:", i.mouseStartingCoordinate, i.MouseEndingCoordinates)
                print("Speed:", i.averageSpeed, "Movement Accuracy:", i.movementAccuracy, "Number Of Clicks:", i.numberOfClicks)
                print("Total Distance:", i.totalDistance, "Number of Direction Changes:", i.directionChanges)

