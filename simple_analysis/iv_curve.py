#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Import the IV data from a csv file.
Some data manipulation is shown with numpy.

@author: misiak
"""

import numpy as np
import matplotlib.pyplot as plt
from import_package import custom_import

# read the config.ini for the data directory and the output directory
data_dir, output_dir = custom_import()

# close all the plots
plt.close('all')

#==============================================================================
# ## quick demonstration of numpy and matplotlib, no data required
#==============================================================================
#A = np.linspace(0, 100, 1e3)
#B = np.sin(A)
#
#fig = plt.figure()
#plt.plot(A, B, label='$sin x$', color='blue', lw=2, ls='--')
#
#plt.xlabel('x-data')
#plt.ylabel('y-data')
#plt.grid(True)
#plt.legend()

#==============================================================================
# # importing and plotting iv curve data
#==============================================================================
vi_path = data_dir + '/RUN52 - VdeI.tsv'

A = np.genfromtxt(vi_path, dtype=str, delimiter='\t')

# i choose to manipulate the data with dictionnaries
current_dict = dict()
voltage_dict = dict()

# look at the csv file to know the column and rows to select
current_dict[20e-3] = A[1:16, 2].astype(float)
voltage_dict[20e-3] = A[1:16, 4].astype(float)

current_dict[21e-3] = A[20:35, 2].astype(float)
voltage_dict[21e-3] = A[20:35, 4].astype(float)

# plotting the VI curve
plt.figure('VI curve')

for k in current_dict.keys():

    current_array = current_dict[k]
    voltage_array = voltage_dict[k]
    plt.plot(current_array, voltage_array, label='{} K'.format(k))

plt.grid('True')
plt.xlabel('Current [nA]')
plt.ylabel('Voltage [mV]')
plt.xscale('log')
plt.yscale('log')
plt.legend()

#==============================================================================
# # extracting the resistance-current curve with ohm law R=U/I
#==============================================================================
resistance_dict = {k:voltage_dict[k]/current_dict[k] for k in voltage_dict.keys()}

# plotting RI curve
plt.figure('RI curve')

for k in current_dict.keys():

    current_array = current_dict[k]
    resistance_array = resistance_dict[k]
    plt.plot(current_array, resistance_array, label='{} K'.format(k))

plt.grid('True')
plt.xlabel('Current [nA]')
plt.ylabel('Resistance [MOhms]')
plt.xscale('log')
plt.yscale('log')
plt.legend()

#==============================================================================
# # extracting the pseudo snesitivity curve dV/dT
#==============================================================================
temp_range = current_dict.keys()
temp_range.sort()

sens_dict = dict()

for tinf, tsup in zip(temp_range[:-1], temp_range[1:]):
    tmoy = np.mean([tinf, tsup])
    sens_dict[tmoy] = voltage_dict[tsup] - voltage_dict[tinf]

plt.figure('pseudo sensitivity curve')

for k in sens_dict.keys():

    sens_array = sens_dict[k]
    plt.plot(current_array, sens_array, label='{} K'.format(k))

plt.grid('True')
plt.xlabel('Current [nA]')
plt.ylabel('Sensitivity [mV/K]')
plt.xscale('log')
plt.legend()
