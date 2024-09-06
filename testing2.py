########## Import Libraries ##########

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import cv2
import os
import sys
import tkinter as tk
import subprocess
import random

########## Define Functions and Classes #########

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

        if self.locomotion == "Aerial":
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
        self.locomotion = random.choice(["Aerial", "4-Wheeled", "Differential Drive", "2-Legged"])
        if self.locomotion == "Aerial":
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
    
def generate_image(width, height):
    # generate a blank png for use in mapping:
    blank_image = np.ones((height, width, 3), dtype=np.uint8) * 205

    # write the image to variable that will return a flag for true or false
    a = cv2.imwrite('blank_image.png', blank_image)

    # verify that the image was actually created:
    if a == True:
        print('Image saved successfully')
    else:
        print('Image saving failed')

def read_map(map_name):
    # this function reads a given map and determine the white space and the border:

    # check if the provided string exists in the current working directory:
    map_str = str(map_name)
    file_path = os.path.join(os.getcwd(),map_str)

    if not os.path.isfile(file_path):
        sys.exit('No such file exists')
    else:
        image = (cv2.imread(map_str,0))

    # white space detection:
    body = np.flip(np.column_stack(np.where(np.flipud(image) >= 254)),axis = 1)

    # border detection:
    border = np.flip(np.column_stack(np.where(np.flipud(image) == 0)), axis =1)

    # return value:
    return body, border

def spawner(sites):
    # this function randomly selects points from the sites, and returns them:
    x,y = random.choice(sites)
    task = np.array([x,y])
    return task

def spawnable_space(body,border,buffer):
    # this function determines spawnable space using the white space and the border

    # define border points as set for speed:
    border_set = set(map(tuple,border))

    # pre-allocate list:
    spawnable = []

    # start iteration through each map point:
    for point in body:
        x,y = point          # assign the x and y of body
        is_spawnable = True  # spawnable flag

        # check for border points in x and y direction:
        for dx in range(-buffer, buffer + 1):
            for dy in range(-buffer, buffer + 1):
                neighbour = (x + dx, y + dy)

                # if exists in the border set, invert flag and break
                if neighbour in border_set:
                    is_spawnable = False
                    break

            # if flag inverted, break
            if not is_spawnable:
                break

        # else if the point is spawnable, keep it:
        if is_spawnable:
            spawnable.append(point)

    # return spawnable array
    return spawnable

def spawnable_sites(spawnable,buffer):
        # The function call generates a grid of evenly spaced points between the minimum and maxiumum range of both the x and y data,
        # and this grid is then compared against the set of all spawnable area and the points that coincide within both are kept. 
        # This allows for an array of all possible evenly spaced points, which are separated by 20cm in both the x and y directions.

        # spawnable_list, then list to set:
        spawnable_list = [tuple(point) for point in spawnable]
        spawnable_set = set(spawnable_list)

        # min and max x and y values for the grid:
        xmin, xmax = min(spawnable[:,0]), max(spawnable[:,0])
        ymin, ymax = min(spawnable[:,1]), max(spawnable[:,1])

        # grid spacing:
        x_spaced = np.arange(xmin, xmax+1, buffer)
        y_spaced = np.arange(ymin, ymax+1, buffer)

        # trim the grid, return sites:
        grid = [(x,y) for x in x_spaced for y in y_spaced]
        sites = np.array([point for point in grid if point in spawnable_set])
        return sites

def get_position(w_frac,h_frac):
    root = tk.Tk()                              # start root window
    screen_width = root.winfo_screenwidth()     # grab screen width
    screen_height = root.winfo_screenheight()   # grab screen height
    root.destroy()                              # close root window

    fig_width = int(screen_width * w_frac)      # width of figure
    fig_height = int(screen_height * h_frac)    # height of figure

    left = (screen_width - fig_width) / 2       # distance on left
    top = (screen_height - fig_height) / 2      # distance on top

    return fig_width, fig_height, left, top     # return values

def fig_display(fig, width, height, placement, sites):

    # create an instance of the window, set the name, size, and placement:
    window = tk.Tk()
    window.title('Interactive Map of the Environment')
    window.geometry(f'{width}x{height}+{placement[0]}+{placement[1]}')

    # place figure onto the window:
    canvas = tkagg.FigureCanvasTkAgg(fig, master = window)

    # create subplot: 
    ax = fig.add_subplot(111)
    task_marker = None

    def spawn_task():
        nonlocal task_marker
        x,y = random.choice(sites)
        task_marker = ax.plot(x, y, 'ro', markersize = 15, label = 'Task')[0]
        update_display(robots)

    def terminate_figure_button():
        subprocess.run(["powershell","clear"])
        print('Figure Terminated!')
        window.destroy()
        os._exit(0)

    def randomize_position_button():
        for id, robot in robots.items():
            robot.__setattr__('position', spawner(sites))
        update_display(robots)
        update_sidebar()

    def generate_random_robots_button():
        
        global robots
        m = random.randrange(2,6)
        x = random.randrange(1,m)
        y = m-x
        robots = {}

        for total_robots in range(1, m+1):
            robot_name = f"robot{total_robots}"
            # camera robots first, then measurement robots:
            if total_robots <= x:
                robots[robot_name] = Robot(
                    id = total_robots,
                    sensor = "Camera",
                    locomotion = random.choice(["Aerial", "4-Wheeled", "Differential Drive", "2-Legged"]),
                    battery = round(random.uniform(0.3,1.0),2),
                    load = 0,
                    position = spawner(sites)
                )
            else:
                robots[robot_name] = Robot(
                    id = total_robots,
                    sensor = "Measurement",
                    locomotion = random.choice(["Aerial", "4-Wheeled", "Differential Drive", "2-Legged"]),
                    battery = round(random.uniform(0.3,1.0),2),
                    load = 0,
                    position = spawner(sites)
                )
        update_display(robots)
        update_sidebar()
        return robots

    def update_display(robots):
        ax.clear()
        ax.set_xlim(auto = True)
        ax.set_ylim(auto = True)
        ax.scatter(body[:,0],body[:,1], c = 'white')
        ax.scatter(border[:,0],border[:,1], c = 'black')
        ax.scatter(spawnable[:,0],spawnable[:,1], color =[183/255, 219/255, 206/255])
        plt.ion()

        if task_marker:
            ax.plot(task_marker.get_xdata(), task_marker.get_ydata(), 'ro', markersize = 15, label='Task')

        i = 1
        for id, robot, in robots.items():
            x,y = robot.__getattribute__("position")
            ax.scatter(x,y, label = f'Robot {i}')
            i += 1
        
        ax.legend(loc = 'lower right')

        canvas.draw()
    
    def update_sidebar():
        for widget in sidebar_frame.winfo_children():
            widget.destroy()

        label_width = 30 # in characters
        
        for id, robot in robots.items():
            attributes = (f"Robot ID: {robot.id}\n"
                           f"Sensor: {robot.sensor}\n"
                           f"Mode of Locomotion: {robot.locomotion}\n"
                           f"Position: {robot.position}\n"
                           f"Battery: {robot.battery}\n"
                           f"Load History: {robot.load}")
            
            robot_label = tk.Label(sidebar_frame, text=attributes, width=label_width, anchor='w', justify='left', padx=5, pady=2)
            robot_label.pack(anchor='w', padx=5, pady=2)

    # set the toolbar:
    toolbar_frame = tk.Frame(window)
    toolbar_frame.pack(side=tk.TOP, fill=tk.X)
    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
    toolbar.update()

    # create a frame for buttons:
    button_frame = tk.Frame(window)
    button_frame.pack(side = tk.TOP, anchor = "center", pady = 5)

    # add a button to spawn tasks
    spawn_button = tk.Button(button_frame, text="Spawn New Task", command=spawn_task)
    spawn_button.pack(side=tk.LEFT, padx = 5)

    # add a button to randomize robot locations
    randomize_location_button = tk.Button(button_frame, text = "Randomize Robot Locations", command = randomize_position_button)
    randomize_location_button.pack(side=tk.LEFT, padx = 5)

    # add a button to regenerate robots:
    randomize_robots_button = tk.Button(button_frame, text = "Regenerate Robots", command = generate_random_robots_button)
    randomize_robots_button.pack(side = tk.LEFT, padx = 5)

    # sidebar frame:
    sidebar_frame = tk.Frame(window, width = 750, bg = "lightgrey")
    sidebar_frame.pack(side = tk.LEFT, fill = tk.Y, padx = 10, pady = 5)
    
    # place the button:
    button = tk.Button(window, text = 'Close Window', command = terminate_figure_button)
    button.pack(side=tk.BOTTOM, pady=5)

    # padding:
    canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand = True)

    # main gui function:
    spawn_task()
    update_sidebar()
    window.mainloop()
   
#################     Main   #####################

### define values: ###

buffer = 4  # spacing used to scale back spawnable space from the border
resolution = 0.05
w_frac = 0.60
h_frac = 0.80

### function calls to set up map: ###

# Step 1 - read map:
body, border = read_map('edited_map.png')

# Step 2 - determine spawnable space:
spawnable = np.array(spawnable_space(body,border,buffer))

# Step 3 - determine spawnable sites:
sites = spawnable_sites(spawnable, 4)

# Step 4 - randomly spawn a task:
task = (spawner(sites))

### spawn robots: ###

m = random.randrange(2,6)
x = random.randrange(1,m)
y = m-x
robots = {}

for num in range(1, m+1):
        robot_name = f"robot{num}"
        # camera robots first, then measurement robots:
        if num <= x:
            robots[robot_name] = Robot(
                id = num,
                sensor = "Camera",
                locomotion = random.choice(["Aerial", "4-Wheeled", "Differential Drive", "2-Legged"]),
                battery = round(random.uniform(0.3,1.0),2),
                load = 0,
                position = spawner(sites)
            )
        else:
            robots[robot_name] = Robot(
                id = num,
                sensor = "Measurement",
                locomotion = random.choice(["Aerial", "4-Wheeled", "Differential Drive", "2-Legged"]),
                battery = round(random.uniform(0.3,1.0),2),
                load = 0,
                position = spawner(sites)
            )

### visualization through GUI: ###

# get size of figure and generate figure:  
fig_width, fig_height, left, top = get_position(w_frac, h_frac)
fig = plt.figure()
fig.set_size_inches(fig_width / 100, fig_height / 100)

fig_display(fig, fig_width, fig_height, (int(left), int(top)), sites)

# storage:

# ----------------------------------------------------------------------------

# # convert to meters:

# def pixel2meter(body, border, spawnable, sites, resolution):
#     a, b, c, d = body*resolution, border*resolution, spawnable*resolution, sites*resolution
#     return a, b, c, d

# ----------------------------------------------------------------------------