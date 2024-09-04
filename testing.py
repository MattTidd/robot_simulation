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

########## Define Functions ##########

# generate a blank png for use in mapping:

def generate_image(width, height):

    blank_image = np.ones((height, width, 3), dtype=np.uint8) * 205
    a = cv2.imwrite('blank_image.png', blank_image)

    # verify that the image was actually created:

    if a == True:
        print('Image saved successfully')
    else:
        print('Image saving failed')

# read a given map and determine the white space and the border:

def read_map(map_name):

    # check if the provided string exists in the current working directory:

    map_str = str(map_name)
    file_path = os.path.join(os.getcwd(),map_str)

    if not os.path.isfile(file_path):
        sys.exit('No such file exists')
    else:
        image = (cv2.imread(map_str,0))

    # white space detection:

    body = np.flip(np.column_stack(np.where(np.flipud(image) >= 254)),axis = 1)

    # canny edge detection:

    border = np.flip(np.column_stack(np.where(np.flipud(image) == 0)), axis =1)

    return body, border

# determine spawnable space using the white space and the border:

def spawnable_space(body,border,buffer):

    border_set = set(map(tuple,border))

    # pre-allocate list:

    spawnable = []

    # start iteration through each map point:

    for point in body:
        x,y = point
        is_spawnable = True

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

    return spawnable

# determine the equally spaced spawnable sites for robots/tasks:

def spawnable_sites(spawnable,buffer):
    spawnable_list = [tuple(point) for point in spawnable]
    spawnable_set = set(spawnable_list)

    xmin, xmax = min(spawnable[:,0]), max(spawnable[:,0])
    ymin, ymax = min(spawnable[:,1]), max(spawnable[:,1])

    x_spaced = np.arange(xmin, xmax+1, buffer)
    y_spaced = np.arange(ymin, ymax+1, buffer)

    grid = [(x,y) for x in x_spaced for y in y_spaced]
    sites = np.array([point for point in grid if point in spawnable_set])

    return sites

# get screen size:

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

# controlled display function:

def fig_display(fig, width, height, placement):

    # define button press function:
    def on_button_press():
        subprocess.run(["powershell","clear"])
        print('Figure Terminated!')
        window.destroy()
        os._exit(0)

    # create an instance of the window, set the name, size, and placement:
    window = tk.Tk()
    window.title('Interactive Map of the Environment')
    window.geometry(f'{width}x{height}+{placement[0]}+{placement[1]}')

    # place figure onto the window:
    canvas = tkagg.FigureCanvasTkAgg(fig, master = window)
    canvas.draw()

    # set the toolbar:
    toolbar_frame = tk.Frame(window)
    toolbar_frame.pack(side=tk.TOP, fill=tk.X)
    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
    toolbar.update()

    # place the button:
    button = tk.Button(window, text = 'Close Window', command = on_button_press)
    button.pack(side=tk.BOTTOM, pady=5)

    # padding:
    canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand = True)

    # main gui function:
    window.mainloop()

########## Main ##########

# I want to load the maps generated within ROS as pngs, and extract the XY coordinates of the operable white space
# and plot this space as the environment for spawning tasks and robots

buffer = 4
resolution = 0.05
w_frac = 0.60
h_frac = 0.80

body, border = read_map('blob2_map.png')
spawnable = np.array(spawnable_space(body,border,buffer))

# The above code reads a given map and determines the location of the border, as well as the white space contained within
# said border. It then loosely scales back the white space approximately 0.2m from the border, and determines the spawnable space 
# wherein robots can spawn without being too close to the wall.

# The next step is to analyze the spawnable space and break it up into equally separated spawn sites, wherein robots can spawn
# without overlapping with one another. This is handled by the following function:

sites = spawnable_sites(spawnable, 4)

# The function call generates a grid of evenly spaced points between the minimum and maxiumum range of both the x and y data,
# and this grid is then compared against the set of all spawnable area and the points that coincide within both are kept. 
# This allows for an array of all possible evenly spaced points, which are separated by 20cm in both the x and y directions.

# I am now going to work on create a class of robots, which can have randomly spawned locations from this array of possible sites.
# I want to represent the robots on the map as circles of radius 5-10 cm, which will then appear on the map. Similarly, the task will appear
# within a random location as well. 

fig_width, fig_height, left, top = get_position(w_frac, h_frac)

fig, ax  = plt.subplots()
fig.set_size_inches(fig_width / 100, fig_height / 100)
ax.set_facecolor(str(205/255))
ax.set_xlim(auto = True)
ax.set_ylim(auto = True)
ax.scatter(body[:,0],body[:,1], c = 'white')
ax.scatter(border[:,0],border[:,1], c = 'black')
ax.scatter(spawnable[:,0],spawnable[:,1], color =[0.65, 0.80, 1.0])
ax.scatter(sites[:,0], sites[:,1], c = 'red')
plt.ion()

fig_display(fig, fig_width, fig_height, (int(left), int(top)))

