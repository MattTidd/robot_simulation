########## Import Libraries ##########
import pickle
import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt
import skfuzzy as fuzz

## Define Functions and Classes:

class Robot:
    # this is the class robot, wherein all robotic objects are made from. Robots consist of:
    # - an ID tag, for referencing
    # - a sensor type, either camera or measurement
    # - a mode of locomotion, which dictates their;
    # - movement weight, which is to symbolize the risk and ease at which a robot can move
    # - a battery level
    # - a load history, which is how many times they have gone to a task location
    # - their position within space

    # constructor to initialize attributes:
    def __init__(self, id, sensor, locomotion, battery, load, position):
        self.id = id
        self.sensor = sensor
        self.locomotion = locomotion

        if self.locomotion == "Drone":
            a = random.uniform(-0.10,0.10)
            self.weight = round(1.00 + a*random.random(),2)
        elif self.locomotion == "4-Wheeled":
            a = random.uniform(-0.10,0.10)
            self.weight = round(1.25 + a*random.random(),2)
        elif self.locomotion == "Differential Drive":
            a = random.uniform(-0.10,0.10)
            self.weight = round(1.50 + a*random.random(),2)
        elif self.locomotion == "2-Legged":
            a = random.uniform(-0.10,0.10)
            self.weight = round(1.75 + a*random.random(),2)

        self.battery = battery
        self.load = load
        self.position = position

    # for when user wants to randomize the attributes of the robots:
    def randomize_attributes(self):
        self.locomotion = random.choice(["Drone", "4-Wheeled", "Differential Drive", "2-Legged"])
        if self.locomotion == "Drone":
            a = random.uniform(-0.10,0.10)
            self.weight = round(1.00 + a*random.random(),2)
        elif self.locomotion == "4-Wheeled":
            a = random.uniform(-0.10,0.10)
            self.weight = round(1.25 + a*random.random(),2)
        elif self.locomotion == "Differential Drive":
            a = random.uniform(-0.10,0.10)
            self.weight = round(1.50 + a*random.random(),2)
        elif self.locomotion == "2-Legged":
            a = random.uniform(-0.10,0.10)
            self.weight = round(1.75 + a*random.random(),2)
        self.battery = round(random.uniform(0.3,1.0),2)

    # method of querying the class:
    def display_robot_info(self):
        return (f"Robot ID: {self.id}\n"
                f"Sensor Type: {self.sensor}\n"
                f"Mode of Locomotion: {self.locomotion}\n"
                f"Movement Weight: {self.weight}\n"
                f"Battery Level: {self.battery}\n"
                f"Load History: {self.load}\n"
                f"Current Position: {self.position} ")

def load_robots():
    with open('saved_data.pkl', 'rb') as file:
        loaded_data = pickle.load(file)

    ## Open the variables:
    body = loaded_data['body']
    border = loaded_data['border']
    sites = loaded_data['sites']
    task_location = loaded_data['task_location']

    ## Open and display the robots:
    robot_dict = loaded_data['robots']

    robots_data = [
        {'Robot ID': robot.id, 'Sensor Type': robot.sensor, 'Mode of Locomotion' : robot.locomotion, 'Movement Weight' : robot.weight, 'Battery Level' : robot.battery,
        'Load History' : robot.load, 'Travelled Distance' : robot.travelled_distance, 'Current Position' : robot.position}
        for robot in robot_dict.values()
    ]

    df = pd.DataFrame(robots_data)
    print(df.to_string(index=False, justify='center'))
    return body, border, sites, task_location

# def fis_design():

#################     Main   #####################

# load in the robots for the mission:
body, border, sites, task_location = load_robots()
























# STORAGE:
# robots_data = [
#     {'Robot ID': robot.id, 'Sensor Type': robot.sensor, 'Mode of Locomotion' : robot.locomotion, 'Movement Weight' : robot.weight, 'Battery Level' : robot.battery,
#      'Load History' : robot.load, 'Current Position' : robot.position}
#      for robot in robot_dict.values()
# ]

# df = pd.DataFrame(robots_data)
# print(df.to_string(index=False, justify='center'))
