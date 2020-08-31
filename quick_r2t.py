#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 09:13:42 2019

@author: misiak
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

from import_package import custom_import

data_dir, save_dir = custom_import()

plt.close('all')

# function to model the resistance of the NTD thermal sensor
def ntd_char(t, t0, r0):
    return r0 * np.exp((t0/t)**0.5)

#import Tkinter as Tk
#from tkFileDialog import askopenfilename
#
#root = Tk.Tk()
#data_path = askopenfilename(parent=root)
#root.destroy()

det_name = ['red70_early', 'red70_late', 'red80_early', 'red80_late']
det_list = list()

for name in det_name:
    fname = 'rt_run57_{}.csv'.format(name)
    data_path = '/'.join([data_dir, 'rt_data', fname])
    tr_array = np.loadtxt(data_path, skiprows=1, unpack=True)
    det_list.append(tr_array)

# for VI data, use curve_fit to determine the parameters R0, T0
popt_list = list()
for tr in det_list:
    t_range, v = tr[:, 1:]
    popt = curve_fit(ntd_char, t_range, v, sigma=v*0.20)[0]
    popt_list.append(popt)
    
color_list = ['lightsteelblue', 'slateblue', 'coral', 'red']

# beautiful plot !
fig = plt.figure()

# looping over the IV curves and the color associated
for tr, name, popt, color in zip(det_list, det_name, popt_list, color_list):

    t_range, v = tr
    # plotting the data
    plt.errorbar(t_range, v, yerr=v*0.20,
                 label=name + '\n T0={0:.2f} K, R0={1:.2f} $\Omega$'.format(*popt),
                 color=color, ls='none', marker='.')

    # plotting the fitting model with R0 and T0 from the curve_fit function
    t_range_full = np.linspace(t_range[0], t_range[-1], 100)
    plt.plot(t_range_full, ntd_char(t_range_full, *popt), color=color)

plt.legend()
plt.grid(True)
plt.yscale('log')
plt.ylabel('Resistance [$\Omega$]')
plt.xlabel('Temperature [K]')
plt.title('rt_run57_red70_and_red80')
plt.tight_layout()

plt.show()



















