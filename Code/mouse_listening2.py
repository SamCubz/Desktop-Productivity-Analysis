from pynput import mouse
import time
import numpy as np
import math
import copy

class MouseListening:

    class mouseMove:

        def __init__(self, mouseStartingCoordinate, previousMouseEndingTime, mouseStartingTime, totalSpeed, totalDistance , numberOfMoves, numberOfClicks, MouseEndingCoordinates, mouseEndingTime, directionChanges):
            
            self.previousMouseEndingTime = previousMouseEndingTime

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

        #tells the main program to keep these session running

        #creating the direction changes
        self.directionChanges = 0
        self.direction = None

        #Every Variable In MouseMove Class
        self.previousMouseEndingTime = None
        self.mouseStartingTime = None
        self.mouseEndingTime = None
        
        self.mouseStartingCoordinate = None
        self.MouseEndingCoordinates = None

        self.totalSpeed = 0
        self.totalDistance = 0
        self.numberOfMoves = 0
        self.numberOfClicks = 0

        #variables that roll over in the onMove category
        self.previousTime = None
        self.previousPosition = None

        #variabels that roll over in the onClick method
        self.previousClickTime = None
        self.currentClickTime = None
        self.previousClickPosition = None
        self.doubleClicked = False


        #margins
        self.regularMargin = 1
        self.doubleClickMargin = 0.5

        #important queue of data
        self.mouseHolder = dataQueue
        self.currentMouseObject = None

        #Listener
        self.listener = mouse.Listener(on_move= self.onMove, on_click = self.onClick)

    def start(self):
        self.listener.start()

    def newMouseObject(self, update,click, x, y):
        #determining what the end time is
        if click:
            self.mouseEndingTime = self.currentClickTime
        else:
            self.mouseEndingTime = self.previousTime
        
        if self.currentMouseObject:
            if not update:
                #this means that we need to create a new object
                self.mouseHolder.put(copy.deepcopy(self.currentMouseObject))
                self.currentMouseObject = self.mouseMove(
                    previousMouseEndingTime=self.previousMouseEndingTime,
                    mouseStartingTime=self.mouseStartingTime,
                    mouseEndingTime=self.mouseEndingTime,

                    mouseStartingCoordinate=self.mouseStartingCoordinate,
                    MouseEndingCoordinates=(x,y),

                    numberOfMoves=self.numberOfMoves,
                    numberOfClicks=self.numberOfClicks,
                    totalDistance=self.totalDistance,
                    totalSpeed=self.totalSpeed,
                    directionChanges= self.directionChanges
                )
            else:
                #this means that we need to update the current object
                self.currentMouseObject.totalSpeed += self.totalSpeed
                self.currentMouseObject.totalDistance += self.totalDistance
                self.currentMouseObject.numberOfMoves += self.numberOfMoves
                self.currentMouseObject.numberOfClicks += self.numberOfClicks
                self.currentMouseObject.MouseEndingCoordinates = (x,y)
                self.currentMouseObject.mouseEndingTime= self.previousClickTime
        else:
            #this means that there is no curent mouse object being updated
            self.currentMouseObject = self.mouseMove(
                    previousMouseEndingTime=self.previousMouseEndingTime,
                    mouseStartingTime=self.mouseStartingTime,
                    mouseEndingTime=self.mouseEndingTime,

                    mouseStartingCoordinate=self.mouseStartingCoordinate,
                    MouseEndingCoordinates=(x,y),

                    numberOfMoves=self.numberOfMoves,
                    numberOfClicks=self.numberOfClicks,
                    totalDistance=self.totalDistance,
                    totalSpeed=self.totalSpeed,
                    directionChanges= self.directionChanges

                )
        self.mouseStartingCoordinate= None
        self.previousMouseEndingTime= self.mouseEndingTime
        self.mouseStartingTime= None
        self.totalSpeed= 0
        self.totalDistance= 0
        self.numberOfMoves= 0
        self.numberOfClicks= 0
        self.directionChanges = 0
        self.direction = None
        self.MouseEndingCoordinates= None
        self.mouseEndingTime= None    

    def onMove(self, x, y):
        currentTime = time.time()
        if self.mouseStartingCoordinate: #not the first movement
            timeDifference = currentTime - self.previousTime
            
            xChange = x - self.previousPosition[0]
            ychange = y - self.previousPosition[1]
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
            

            distance = math.sqrt( (self.previousPosition[0] - x)**2 + (self.previousPosition[1] - y) ** 2 )
            if timeDifference > 0: #determining if it's been too long since the previous
                if timeDifference > self.regularMargin:
                    self.newMouseObject(update = False,click = False, x = x, y = y)
                self.totalSpeed += distance / timeDifference
            self.totalDistance += distance
        else:
            self.mouseStartingCoordinate = (x,y)
            self.mouseStartingTime = currentTime
            self.numberOfMoves += 1
        self.numberOfMoves += 1
        self.previousPosition = (x,y)
        self.previousTime = currentTime


    def onClick(self,x,y, button, pressed):
        if pressed:
            self.numberOfClicks += 1
            self.currentClickTime = time.time()
            if self.mouseStartingTime:
                if self.previousClickTime:
                    timeBetweenClicks = self.currentClickTime - self.previousClickTime
                    if timeBetweenClicks < self.doubleClickMargin and self.totalDistance == 0 and not self.doubleClicked:
                        #double click
                        self.numberOfClicks -= 1
                        self.doubleClicked = True
                        self.newMouseObject(update= True, click = True, x = x, y = y)
                    elif timeBetweenClicks < self.regularMargin:
                        #regular error
                        self.newMouseObject(update = True, click = True, x = x, y = y)
                        self.doubleClicked = False
                    else:
                        #new click
                        self.newMouseObject(update = False,click = True, x = x, y = y)
                        self.doubleClicked = False
                else:
                    #first click
                    self.newMouseObject(update = False, click = True,x = x, y = y)
            else:
                #this means that the mouse has not been moved
                """Update Logic Later"""
                pass
            self.previousClickTime = self.currentClickTime
            self.previousClickPosition = (x,y)    


    
    def stop(self):
        self.listener.stop()


           
if __name__ == "__main__":


    listener2 = MouseListening()

    listener2.start()

    for i in listener2.mouseList:
        i.calculateVals()
        print(i.distance)


