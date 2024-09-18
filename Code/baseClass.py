from key_listening import KeyboardListener
from mouse_listening3 import MouseListening
import threading
import pandas as pd
import numpy as np
import tkinter as tk
import queue
from PIL import Image, ImageTk
from clean import Processing
import time
from datetime import datetime

class Base:

    def __init__(self, root):
        self.root = root
        self.inSession = [True]

        #attributes that'll be added to the thing
        self.sessionStart = time.time()
        self.sessionNumber = 0

        #in progress
        self.combinedDF = pd.DataFrame( columns = ["Session Number", "Session Length", "DayOfWeek"] )

    def checkActivity(self, event = None):
        if self.sessionNumber > 0:
            if self.inSession[0]:
                self.inSession[0] = False
                self.endDataCollection()
                print("Session Stopped")
            else:
                self.inSession[0] = True
                self.sessionNumber += 1
                print("Session Started")
                self.startDataCollection()
        else:
            self.sessionNumber += 1
            print("Started Data Collection")
            self.startDataCollection()

    def startDataCollection(self):

        #the queue to add the data in
        self.mouseDataQueue = queue.Queue()
        self.keyboardDataQueue = queue.Queue()

        #the listeners
        self.MouseListener = MouseListening(self.mouseDataQueue)
        self.keyboardListener = KeyboardListener(self.keyboardDataQueue)

        self.mouseDF = pd.DataFrame( columns= ['objectType',"uniqueCounter", "startTime", "endTime", "MAverageSpeed", "MmovementAccuracy", "MclickingAccuracy", "DirectionChanges","inactivityDuration", "timeOfDay", "weekDay", "sessionNumber"])
        self.keyboardDF = pd.DataFrame( columns= ['objectType',"uniqueCounterKeys", "kSpeed", "kAccuracy", "avgTime", "startTime", "endTime", "ClusterLength", "inactivityDuration", "timeOfDay", "weekDay", "sessionNumber"])  

        timeOfDay = datetime.now()

        self.processing = Processing(self.mouseDF, self.keyboardDF,  self.sessionNumber, timeOfDay, sessionTime= time.time(), completeSessionStart= self.sessionStart)


        self.MouseThread = threading.Thread(target = self.MouseListener.start)
        self.KeyboardThread = threading.Thread(target = self.keyboardListener.start)

        self.MouseThread.start()
        self.KeyboardThread.start()


    def endDataCollection(self):
        
        self.gettingData()
        self.MouseListener.stop()
        self.keyboardListener.stop()
        
        self.processing.mainFunction()
        self.processing.storeData()


    def gettingData(self):

        self.MouseListener.timeOut()
        self.keyboardListener.timeOut()

        if not self.mouseDataQueue.empty():
            while not self.mouseDataQueue.empty():
                self.processing.processMouse(objectOfInterest= self.mouseDataQueue.get())

        if not self.keyboardDataQueue.empty():
            while not self.keyboardDataQueue.empty():
                self.processing.processKeyboard(objectOfInterest= self.keyboardDataQueue.get())


if __name__ == "__main__":
    root = tk.Tk()

    #setting all the attributes
    root.overrideredirect(True)
    image_path = "Chatbot/Wizard.png"
    image = Image.open(image_path).convert("RGBA").resize((100,100))
    photo_image = ImageTk.PhotoImage(image)
    canvas = tk.Canvas(root, width = root.winfo_screenwidth(), height = root.winfo_screenheight(), bg = "pink", highlightthickness= 0)
    root.attributes("-alpha", 1.0,'-topmost',True, "-transparentcolor", "pink")
    canvas.pack()
    x, y = root.winfo_screenwidth() - 100, root.winfo_screenheight() - 100
    image_id = canvas.create_image(x, y, anchor=tk.NW, image=photo_image)
    app = Base(root)
    root.bind('<Button-2>', app.checkActivity)
    root.mainloop()