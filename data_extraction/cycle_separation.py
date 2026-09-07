import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import label

"""
Separates data into cycles and returns upwards input, upwards output, downwards input, and downwards
output for nth cycle

csv_file - input file 
num_cycles - total number of cycles 
n - which cycle is being isolated; indexed from 1 (first cycle is 1, second cycle is 2, etc.) 
foam load - the point at which the foam has been broken through; default is 36 by now
plot - boolean variable for whether or not to plot data
"""
def cycle_separation(csv_file, n, foam_load=36, num_cycles=5):
    # Opening and cleaning file
    file = open(csv_file, "r")
    data = np.genfromtxt(file, delimiter=',', skip_header=2, dtype=str)
    time = np.array([float(val.strip('"')) for val in data[:, 1]])
    xDisp = np.array([float(val.strip('"')) for val in data[:, 2]])
    yLoad = np.array([float(val.strip('"')) * 1000 for val in data[:, 3]])

    # Identify upward and downward cycles
    grad_disp = np.gradient(xDisp, time)
    upward_mask = grad_disp > 0
    downward_mask = grad_disp < 0

    # isolates each cycle into whether or not the mask is true or false
    # returns two values:
    # labeled_array which assigns a uniqie positive integer to every part where mask is true
    # and the number of unique features
    labeled_up_array, _ = label(upward_mask)
    labeled_down_array, _ = label(downward_mask)

    # print("Upward segments found:", num_up_features)
    # print("Downward segments found:", num_down_features)

    # filters everything above foam_load
    foam_load_mask = yLoad > foam_load

    # Upwards x and y inputs
    cycle_up_mask = labeled_up_array == n
    x_up = xDisp[cycle_up_mask & foam_load_mask]
    y_up = yLoad[cycle_up_mask & foam_load_mask]

    # Downwards x and y inputs
    cycle_down_mask = labeled_down_array == n
    x_down = xDisp[cycle_down_mask & foam_load_mask]
    y_down = yLoad[cycle_down_mask & foam_load_mask]
    
    return x_up, y_up, x_down, y_down
