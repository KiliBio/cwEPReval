#!/usr/bin/python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.ticker import FuncFormatter
import sys

"""
Usage: 

Csv-file required in the format:

X Y1 Y2 Y3 Y4 Y5 etc.

X = Field (in mT)
Yn = EPR Signal (A.U.)    

Usage:

python3 [this script] [csv-file] [average frequency of radiowave used during the experiment, in GHz]  

"""

font = {'family' : 'normal',
        'weight' : 'normal',
        'size'   : 14}

plt.rc('font', **font)

dist_colors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4',
          '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff',
          '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1',
          '#000075', '#808080']

rainbow = ['#e71d43', '#ff0000', '#ff3700', '#ff6e00', '#ffa500', '#ffc300',
           '#ffe100', '#ffff00', '#aad500', '#55aa00', '#008000', '#005555',
           '#002baa', '#0000ff', '#1900d5', '#3200ac', '#4b0082', '#812ba6',
           '#b857ca', '#d03a87']

csv_file = sys.argv[1]

try:
    frequency_GHz = float(sys.argv[2])  # Try to get frequency from command line argument
except IndexError:
    frequency_GHz = 9.48314  # Default frequency in GHz if not provided

frequency_Hz = frequency_GHz * 1e9  # Convert GHz to Hertz
planck_h = 6.62607015*10**(-34) # Unit Joule/Hertz
bohr = 9.274009994*10**(-24) # Unit Joule/Tesla

# definition of the lambda function to convert field(mT) to g-value and vice versa 
f = lambda gValue: (planck_h * frequency_Hz  * 1e-3) / (bohr * gValue)
g_val = lambda x: (planck_h * frequency_Hz) / (bohr * x * 1e-3)

# Read CSV data using Pandas
data = pd.read_csv(csv_file, header=None)

# Prepare the data
names = (data.iloc[0, 1:])
magnetic_field_mT = pd.to_numeric(data.iloc[:, 0], errors='coerce')
signal = data.drop(columns=data.columns[0])

# figure configuration
fig, ax1 = plt.subplots()

ax1.set_prop_cycle(color=rainbow)

# create axis number 2 which shares the same y (data)-axis 
ax2 = ax1.twiny()
ax1.get_shared_x_axes().join(ax1,ax2)

ax1.plot(magnetic_field_mT, signal, label=names)

ax2.xaxis.set_major_formatter(FuncFormatter(lambda magnetic_field_mT,pos: f"{g_val(magnetic_field_mT):.3f}"))

ax1.set_xlabel('Field (mT)', fontsize=15)
ax1.set_ylabel('Signal-Intensity (A.U.)', fontsize=15)
ax2.set_xlabel('g-value', fontsize=15)
# Turn off tick labels
ax1.set_yticklabels([])

plt.tick_params(axis='both', direction='in', length=5, width=1, colors='black')
plt.grid('both', color='grey', linestyle='-', linewidth=0.5, alpha=0.5)

ax1.tick_params(direction="in")
ax1.tick_params(which='both', width=1)
ax1.tick_params(which='major', length=5)
ax1.tick_params(which='minor', length=2.5)

ax2.tick_params(direction="in")
ax2.tick_params(which='both', width=1)
ax2.tick_params(which='major', length=5)
ax2.tick_params(which='minor', length=2.5)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
lines = lines1 + lines2
labels = labels1 + labels2
ax1.legend(lines, labels, loc='upper right', fontsize=10)

plt.show()
