#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 09:13:42 2019

@author: misiak
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

def ntd_char(t, t0, r0):
    return r0 * np.exp((t0/t)**0.5)

t_range = np.array([30, 35, 40, 45, 50, 60]) * 1e-3

t_range_full = np.linspace(25, 65, 100) * 1e-3

default_param = (3, 1.)

default_array = ntd_char(t_range, *default_param)

v12 = 1e6*np.array([3.1, 0.751141552511409, 0.522831050228309, 0.223287671232875, 0.15205479452055, 0.05079908675799])
v34 = 1e6*np.array([5.5, 1.03196347031964, 0.682648401826475, 0.370319634703197, 0.225570776255705, 0.083219178082193])
v78 = 1e6*np.array([0.348, 0.163926940639269, 0.073287671232878, 0.058675799086757, 0.036187214611872, 0.016181500662411])
v910 = 1e6*np.array([0.326, 0.125570776255707, 0.103881278538812, 0.050913242009131, 0.030707762557077, 0.01410484162351])
v1112 = 1e6*np.array([0.355, 0.131050228310503, 0.078082191780823, 0.04474885844749, 0.020547945205479, 0.010548897988679])

det_list = [v12, v34, v78, v910, v1112]
det_name = ['NTD 628-26', 'NTD 628-30', 'NTD 605-31', 'NTD 605-32', 'NTD LUM641']

popt_list = [curve_fit(ntd_char, t_range, v)[0] for v in det_list]

color_list = ['blue', 'red', 'orange', 'green', 'black']

fig = plt.figure()
for v, name, popt, color in zip(det_list, det_name, popt_list, color_list):
    plt.plot(t_range, v, label=name + '\n T0={0:.3f} K, R0={1:.3f} $\Omega$'.format(*popt),
             ls='none', marker='o', color=color)
    plt.plot(t_range_full, ntd_char(t_range_full, *popt), color=color)

plt.legend()
plt.grid(True)
plt.yscale('log')
plt.ylabel('Resistance [$\Omega$]')
plt.xlabel('Temperature [K]')
plt.tight_layout()






















