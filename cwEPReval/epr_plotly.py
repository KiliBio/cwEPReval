#!/usr/bin/env python3
"""
Last edited: 16.01.2022
Plotting EPR from Bruker

Starting to implement changes one after the other!
"""

import csv
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import sys

def getdata(file):
    df = pd.read_csv(file, delim_whitespace=True)
    df.drop(columns=df.columns[-2:],axis=1,inplace=True)
    df.rename({'index':'Index','Field':'Field', '[G]':'Intensity'}, axis='columns', inplace=True)
    print(df)
    return(df)

def EPRplotter(df, title):
    """
    x = "Field"
    y = "Intensity"
    """
    x_min, x_max = df["Field"].min(), df["Field"].max()

    #y_min = df.loc[:,"Intensity"].min(axis=1).min(axis=0)-5
    #y_max = df.loc[:,"Intensity"].max(axis=1).max(axis=0)+5

    ax = setup_EPR_plot_frame(title, x_min, x_max)
    single_plot(ax, df["Field"], df["Intensity"])
    plt.show()

def single_plot(ax, x_data, y_data):
    """
    plots only one data1 (df.column) against data2 (df.column) in the ax dataframe
    """
    out = ax.plot(x_data, y_data)
    return out

def Gauss2Tesla(gauss):
    tesla = gauss*10**(-4)
    return tesla

def calculateGvalue(magn):
    """
    calculates the G value from the frequency of the microwave radiation
    (in Hertz) and the magnetic field strength (in Tesla)
    """
    freq = 9.48 * 1000
    planck = 6.62*10**(-34) # Unit J*s
    bohr = 9.2740154*10**(-24) # Unit J/T
    #constant = 0.7144 # planck constant * planck magnetic
    #gvalue = constant * (freq / magn)

    gvalue = (planck * freq) / (bohr * magn)
    return gvalue

def Gvalue2magneticfield(Gvalue):
    """
    calculates the G value from the frequency of the microwave radiation
    (in Hertz) and the magnetic field strength (in Tesla)
    """
    freq = 9.48 * 1000
    planck = 6.62*10**(-34) # Unit J*s
    bohr = 9.2740154*10**(-24) # Unit J/T

    magn = (planck * freq) / (bohr * Gvalue)
    return magn

#print(calculateGvalue(9.63*10**(9), 0.3433))

def setup_EPR_plot_frame(title, x_min, x_max):
    """
    Formats a figure environment that allows plotting of XRD data.
    REQUIRES "calculateGvalue" and "dspace2theta" functions to allow for a secondary axis.
    """
    #print("setup_EPR_plot_frame")
    fig, ax = plt.subplots(constrained_layout=True)
    # Set the axis limits
    ax.set_xlim(x_min, x_max)
    #ax.set_ylim(y_min, y_max)

    # Set the label names on the X and Y axis
    ax.set_xlabel(r'Magnetic field G$_0$ [mT]')
    ax.set_ylabel('EPR signal intensity')
    ax.set_title(title)

    # defining a secondary axis
    secax = ax.secondary_xaxis('top', functions=(calculateGvalue, Gvalue2magneticfield))
    secax.set_xlabel(r'g-value')
    secax.set_xlim(calculateGvalue(Gauss2Tesla(ax.get_xlim()[0])), calculateGvalue(Gauss2Tesla(ax.get_xlim()[1])))

    # Edit the major and minor ticks of the x and y axis
    ax.xaxis.set_tick_params(which='major', size=6, width=1.5, direction='in')
    ax.xaxis.set_tick_params(which='minor', size=3, width=1.5, direction='in')
    ax.yaxis.set_tick_params(which='major', size=6, width=1.5, direction='in', right='on')
    ax.yaxis.set_tick_params(which='minor', size=3, width=1.5, direction='in', right='on')

    # Edit the tick parameters of the secondary x-axis
    secax.xaxis.set_tick_params(which='major', size=6, width=1.5, direction='in')
    secax.xaxis.set_tick_params(which='minor', size=3, width=0.75, direction='in')
    #secax.set_xticks([1.5, 1.66, 1.83, 2.0, 2.16, 2.33, 2.5])

    ax.grid(axis="both", which="major", color='grey', linestyle='-.', linewidth=0.2)
    return ax

if __name__ == '__main__':
    print("EPRplotter")
    file = sys.argv[1]
    dataframe = getdata(file)
    EPRplotter(dataframe, file.split(".")[0])
