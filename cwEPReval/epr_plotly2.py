#!/usr/bin/env python3
"""
Last edited: 10.01.2022
Plotting EPR from Bruker

TODO:
- plot multiple files
- G-value secondary axis is not optimal? especially for full scan files
- allow the insertion of g value lines

Better appending to the end of the file?
https://stackoverflow.com/questions/39288210/how-to-plot-data-from-multiple-files-in-a-loop
"""

import csv
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pylab import cm
import sys
import os
from datetime import datetime
cwd = os.getcwd()

import peakutils
from peakutils.plot import plot as pplot

# sets parameters for the plotting such as font and graph resolution(dpi)
mpl.rcParams['font.family'] = 'Chandas'
plt.rcParams['font.size'] = 9
plt.rcParams['axes.linewidth'] = 1.25
plt.rcParams['figure.figsize'] = (7.0, 4.0)
#plt.rcParams['figure.figsize'] = [8, 3]
plt.rcParams['figure.dpi'] = 150 # 200 e.g. is really fine, but slower

# defines 10 colors inside the rainbow reset spectra
colors = cm.get_cmap('rainbow', 10)


def getdata(file):
    """
    Retrieves the data from the ASCii
    """
    df = pd.read_csv(file, delim_whitespace=True)
    df.drop(columns=df.columns[-2:],axis=1,inplace=True)
    df.rename({'index':'Index','Field':'Field', '[G]':'Intensity'}, axis='columns', inplace=True)
    print("Data from file retrieved.")
    print(df)
    return(df)

def dataEPR2csv(df, filename):
    """
    get a nice csv file of the data to be plotted also in Origin and stuff
    """
    df2 = df.copy()

    df2.rename({'index':'Index','Field':'Field(G)', '[G]':'Intensity'}, axis='columns', inplace=True)
    df2["Field(T)"] = Gauss2Tesla(df2["Field(G)"])
    df2["g-value"] = calculateGvalue(df2["Field(T)"])

    df2.to_csv("{path}/CSV_{filename}.csv".format(path=cwd, filename=filename),
    columns=("Field(T)","g-value","Intensity"),
    index=False)
    print("CSV for {filename} was written.".format(filename=filename))

def EPRplotter(df, title, **kwargs):
    """
    x = "Field"
    y = "Intensity"
    """
    g_lines = kwargs.get('lines', None)

    x_min_T, x_max_T = Gauss2Tesla(df["Field"]).min(), Gauss2Tesla(df["Field"]).max()
    #x_min_G, x_max_G = df["Field"].min(), df["Field"].max()
    #print("Minimal Field value: {g} Gauss, {t:.2} Tesla".format(g=x_min_G, t=x_min_T))
    #print("Maximal Field value: {g} Gauss, {t:.2} Tesla".format(g=x_max_G, t=x_max_T))
    #y_min = df.loc[:,"Intensity"].min(axis=1).min(axis=0)-5
    #y_max = df.loc[:,"Intensity"].max(axis=1).max(axis=0)+5
    if g_lines:
        ax = setup_EPR_plot_frame(title, x_min_T, x_max_T, g_lines)
    else:
        ax = setup_EPR_plot_frame(title, x_min_T, x_max_T)

    single_plot(ax, Gauss2Tesla(df["Field"]), df["Intensity"])
    #get_peaks(ax, df, "Field", "Intensity", 3, 0.5, 10)

def multi_EPRplotter(df_dict):
    """
    x = "Field"
    y = "Intensity"
    """
    g_lines = kwargs.get('lines', None)

    x_min_T, x_max_T = 10000, 0

    for key in df_dict.keys():
        x_min_new, x_max_new = Gauss2Tesla(df_dict[key]["Field"]).min(), Gauss2Tesla(df_dict[key]["Field"]).max()
        if x_min_new <= x_min_T:
            x_min_T = x_min_new
        if x_max_new >= x_max_T:
            x_max_T = x_max_T

    ax = setup_EPR_plot_frame("Multiplot", x_min_T, x_max_T)

    multi_plot(ax, df_dict)


def setup_EPR_plot_frame(title, x_min, x_max, **kwargs):
    """
    Formats a figure environment that allows plotting of XRD data.
    REQUIRES "calculateGvalue" and "dspace2theta" functions to allow for a secondary axis.
    """
    g_lines = kwargs.get('lines', None)
    #print("setup_EPR_plot_frame")
    fig, ax = plt.subplots(constrained_layout=True)
    # Set the axis limits
    ax.set_xlim(x_min, x_max)
    #ax.set_ylim(y_min, y_max)

    # Set the label names on the X and Y axis
    ax.set_xlabel(r'Magnetic field G$_0$ [Tesla]', fontsize=12)
    ax.set_ylabel('EPR signal intensity', fontsize=12)
    ax.set_title(title)

    # defining a secondary axis
    secax = ax.secondary_xaxis('top', functions=(calculateGvalue, Gvalue2magneticfield))
    secax.set_xlabel(r'g-scale', fontsize=12)
    print("Minimal G-Value", calculateGvalue(ax.get_xlim()[0]))
    print("Maximal G-Value", calculateGvalue(ax.get_xlim()[1]))
    #secax.set_xlim(calculateGvalue(Gauss2Tesla(ax.get_xlim()[0])), calculateGvalue(Gauss2Tesla(ax.get_xlim()[1])))

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

    # if lines list is specified, additional characterized lines are plotted to allow identification
    if g_lines:
        ax = add_g_lines(ax, g_lines)

    return ax

def add_g_lines(ax, line_values):
    """
    Needs work!
    This function plots g value lines into the pyplot.
    """
    # if single string
    if isinstance(line_values, str) and line_values in lines_dict.keys():
        for line in lines_dict[line_values]:
            angle = dspace2theta(line)
            intensity = lines_dict[line_values][line]
            ax.axvline(x=angle, ymin=0, ymax=intensity, color='red', linestyle='-.', linewidth=0.5)

    #if list is passed
    elif isinstance(line_values, list):
        angles, intensities = [], []
        lines_colors = cm.get_cmap('Reds', len(line_values))
        for i, mine in enumerate(line_values):
            if mine in lines_dict.keys():
                for line in lines_dict[mine]:
                    angles.append(dspace2theta(line))
                    intensities.append(lines_dict[mine][line])

        for col, angint in enumerate(zip(angles, intensities)):
            ax.axvline(x=angint[0], ymin=0, ymax=angint[1], color='red', linestyle='-.', linewidth=0.5)
    else:
        print("Please enter either a list or a line_valuesname(str) as input for the lines argument")
    return ax

def single_plot(ax, x_data, y_data):
    """
    plots only one data1 (df.column) against data2 (df.column) in the ax dataframe
    """
    out = ax.plot(x_data, y_data)
    return out

def multi_plot(ax, df_dict, **kwargs):
    """
    Plots the data of dataframes.
    """
    for i, key in enumerate(df_dict):
        out = ax.plot(Gauss2Tesla(df_dict[key]["Field"]), df_dict[key]["Intensity"], label=key, color=colors(i))
    return out

def Gauss2Tesla(gauss):
    tesla = gauss*10**(-4)
    return tesla

def calculateGvalue(magn):
    """
    calculates the G value from the frequency of the microwave radiation
    (in Hertz) and the magnetic field strength (in Tesla)
    """
    # 9.48 GHz to Hertz
    freq = 9.48 * 10**9 # Hertz
    planck = 6.62607015*10**(-34) # Unit Joule/Hertz
    bohr = 9.274009994*10**(-24) # Unit Joule/Tesla
    #constant = 0.7144 # planck constant * planck magnetic
    #gvalue = constant * (freq / magn)

    gvalue = (planck * freq) / (bohr * magn)
    return gvalue

def Gvalue2magneticfield(Gvalue):
    """
    calculates the G value from the frequency of the microwave radiation
    (in Hertz) and the magnetic field strength (in Tesla)
    """
    freq = 9.48 * 10**9 # Hertz
    planck = 6.62607015*10**(-34) # Unit Joule/Hertz
    bohr = 9.274009994*10**(-24) # Unit Joule/Tesla

    magn = (planck * freq) / (bohr * Gvalue)
    return magn

def get_peaks(ax, dataframe, x_data, y_data, threshold, mini_dist, my_width, **kwargs):
    """
    Function calculates peaks graphically using peakutil. Parameters:
    ax - to plot in
    dataframe - (str) pd.df contains all the data
    x_data - (str) X-axis column name in dataframe
    y_data - (str) the main column name that contains the data
    out - (str) outfile-folder
    threshold - detectable peak relative to the highest peak
    mini_dist - minimum distance between the peaks
    optional parameters:
    absolute - TODO: allow for absolute threshold
    indexes = peakutils.indexes(np.array(imp_data['bckg&bl_rm']), thres_abs=True, thres=47, min_dist=4)
    """
    indexes = peakutils.indexes(np.array(dataframe[y_data]), thres=threshold, min_dist=mini_dist)
    pplot(np.array(dataframe[x_data]), np.array(dataframe[y_data]), indexes)
    peaks_x = peakutils.interpolate(np.array(dataframe[x_data]), np.array(dataframe[y_data]), ind=indexes, width=my_width)
    print("Peak_position at: {}".format(["{:.4f}".format(i) for i in peaks_x]))
    intensity_list = []
    for angle in peaks_x:
        df_sort = dataframe.iloc[(dataframe['angles']-angle).abs().argsort()[:2]]
        intensity = np.mean(df_sort[y_data].tolist())
        intensity_list.append(intensity)

    #data4df = {"angles (deg)": peaks_x, "intensity": intensity_list}
    #peak_data = pd.DataFrame(data4df)
    #peak_data['rel_inten (%)'] = peak_data['intensity']/(max(intensity_list))*100
    #peak_data['d-spacing (A)'] = theta2dspace(peak_data['angles (deg)'])
    #peak_data.to_csv(out+'/peaks.csv', index=False, sep=',', float_format="%.3f")
    #peak_protocol = open("{directory}/{data_name}_peaks_protocol.txt".format(directory=out, data_name=y_data), "w")
    #peak_protocol.write("Peak estimation with peakutils.indexes.\n")
    #peak_protocol.write("Parameters to find {nump} peaks in the '{name}' data:\n".format(nump=len(peaks_x), name=y_data))
    #peak_protocol.write("Relative Threshold: {thres}\n".format(thres=threshold))
    #peak_protocol.write("Min distance: {mini}\n".format(mini=mini_dist))
    #peak_protocol.write("Peaks position enhanced by interpolation using peakutils.interpolate.\n")
    #peak_protocol.write("Gaussian fit using the surrounding {wid} points both ways.\n".format(wid=my_width))
    #peak_protocol.close()

def main_function():
    #print(calculateGvalue(0.3084))
    # for multiple seperate input files
    if not len(sys.argv) == 2:
        dataframe_dict = {}
        files = sys.argv[1:]
        print(files)
        for file in files:
            dataframe = getdata(file)
            dict[file] = dataframe
            multi_EPRplotter(dataframe)
        plt.show()

    # only one input file
    else:
        file = sys.argv[1]
        dataframe = getdata(file)
        #dataEPR2csv(dataframe, file.split(".")[0])
        EPRplotter(dataframe, file.split(".")[0])
        plt.show()

if __name__ == '__main__':
    print("EPRplotter")
    #print(calculateGvalue(Gauss2Tesla(4400)))
    main_function()
