#!/usr/bin/env python3
"""
Returns the Gvalue for any number supplied in the three units:
Tesla (T)
milliTesla (mT)
Gauss (G)
"""

import sys

def main():
    supply = "".join(sys.argv[1:])
    number, unit = stringsplitter(supply)
    print(number, unit)
    if unit in ["mT", "T", "G"]:
        Gcalc(number, unit)
    else:
        print("Please supply unit either in mT, T or G")

    exit()


def stringsplitter(string):
    """
    Sorts input string by integers and letters.
    """
    number, unit = [], []
    for letter in string:
        if letter.isalpha():
            unit.append(letter)
        elif letter.isnumeric():
            number.append(letter)
        else:
            print("{} is not number or unit".format(letter))
    return ''.join(number), ''.join(unit)

def Gcalc(numb, unit):
    freq = 9.48 * 10**9 # Hertz
    planck = 6.62607015*10**(-34) # Unit Joule/Hertz
    bohr = 9.274009994*10**(-24) # Unit Joule/Tesla
    gvalue = (planck * freq) / (bohr * float(numb))

    if unit == "T":
        gvalue = gvalue
    elif unit == "mT":
        gvalue = gvalue*1000
    else: # Gauss
        gvalue = gvalue*10000

    print("{n} {u} - g-value {g:0.3f}".format(n=numb, u=unit, g=gvalue))




if __name__ == '__main__':
    main()
