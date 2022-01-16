#!/usr/bin/env python3

"""
Last edited: 10.01.2022

Getting CSV file from Bruker ASCII EPR File with G-value calculated
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
    df2["Field(mT)"] = df2["Field(T)"]*1000

    df2.to_csv("{path}/CSV_{filename}.csv".format(path=cwd, filename=filename),
    columns=("Field(T)", "Field(mT)", "Field(G)", "g-value","Intensity"),
    index=False)
    print("CSV for {filename} was written.".format(filename=filename))

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

    gvalue = (planck * freq) / (bohr * magn)
    return gvalue

def main_function():
    files = sys.argv[1:]
    print(files)
    for file in files:
        dataframe = getdata(file)
        dataEPR2csv(dataframe, file.split(".")[0])

if __name__ == '__main__':
    print("EPR ascii to CSV converter")
    main_function()
