# Desktop Wizard Productivity Analysis

# Goal
I know a lot of people in college who have attention problems, including myself. I wanted to make a program that could really help people to understand how they work best.

**Desktop Wizard Productivity Analysis** is a Python-based application designed to monitor and analyze user productivity by collecting data from keyboard and mouse interactions. The program processes this data to predict periods of inactivity and recommend optimal break times, thereby helping to optimize the work-rest cycle.

## Future Plans
- Scaling the data storage capabilities
- Implementing a wizard assistant to make the user interface more interactive
- Streamline data collection

## Features

- **Real-Time Data Collection**: Uses concurrent threading to capture real-time keyboard and mouse activity. Collects data such as keypress speed, mouse movement accuracy, and time between actions.
- **Feature Engineering**: Analyzes productivity using parameters like average mouse speed, typing accuracy, keys per minute, and time between clusters of actions.
- **Data Processing**: Stores keyboard and mouse activity data in pandas DataFrames, which are then combined for further analysis.
- **Inactivity Prediction**: Predicts inactivity periods using time gaps between consecutive keyboard and mouse events.
- **Rolling Calculations**: The program dynamically calculates rolling averages and metrics using the last few data points, monitoring user productivity in real time.

# All Parameters
## Mouse Regular Parameters
- Inactivity Duration
- Speed
- Movement Accuracy
- Clicking Accuracy
- Direction Changes

## Keyboard Regular Parameters
- Inactivity Duration
- Speed
- Accuracy
- Time
- Cluster Length

##Bugs
Currently working out how to integrate machinelearning.py fully into the application. There are some errors.
