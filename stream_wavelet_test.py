#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Simple analysis of SAMBA stream

@author: misiak
"""

import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

from import_package import custom_import
from samba_reader import read_ac_data

data_dir, output_dir = custom_import()

plt.close('all')

#==============================================================================
# PLOT EXP DATA
#==============================================================================
data_path = data_dir + '/tb19m002/tb19m002_S00'
fs, raw_stream = read_ac_data(data_path, 0)

N = raw_stream.shape[0]
L = N / fs

time_array = np.arange(0, L, fs**-1)
ind_off = int(N/10)

time = time_array[:ind_off]
stream = raw_stream[:ind_off]

plt.figure('raw stream')
plt.plot(time, stream)

##==============================================================================
## TEST THE WAVELET TRANSFORM
##==============================================================================
#import pywt
#
##A, B = pywt.dwt(stream, 'db2')
##
##C = A**2 + B**2
##
##plt.figure()
##plt.plot(C)
##
###fig, ax = plt.subplots(nrows=2)
###
###ax[0].plot(A)
###
###ax[1].plot(np.abs(B))
#
#cwtmatr, freqs=pywt.cwt(stream,np.arange(1,200),'mexh')
#
#plt.figure('hell')
##plt.matshow(coef)
##plt.show()
#
#plt.imshow(cwtmatr, extent=[-1, 1, 1, 200], cmap='PRGn', aspect='auto', vmax=abs(cwtmatr).max(), vmin=-abs(cwtmatr).max())
#
#

#==============================================================================
# EL NINO PLOT
#==============================================================================

import pywt

#time, sst = pywt.data.nino()
sst = stream
dt = time[1] - time[0]

# Taken from http://nicolasfauchereau.github.io/climatecode/posts/wavelet-analysis-in-python/
#wavelet = 'cmor1.5-1.0'
wavelet = 'mexh'
scales = np.arange(1, 200)

[cfs, frequencies] = pywt.cwt(sst, scales, wavelet, dt)
power = (abs(cfs)) ** 2

period = 1. / frequencies
#levels = [0.0625, 0.125, 0.25, 0.5, 1, 2, 4, 8]
levels = 10**np.linspace(-14, -10,10)
f, ax = plt.subplots(figsize=(15, 10))
ax.contourf(time, np.log10(period), np.log10(power), np.log10(levels),
            extend='both')

ax.set_title('%s Wavelet Power Spectrum (%s)' % ('Nino1+2', wavelet))
ax.set_ylabel('Period (years)')
Yticks = 10 ** np.arange(np.ceil(np.log10(period.min())),
                        np.ceil(np.log10(period.max())))
ax.set_yticks(np.log10(Yticks))
ax.set_yticklabels(Yticks)
ax.invert_yaxis()
ylim = ax.get_ylim()
#ax.set_ylim(ylim[0], -1)

plt.show()