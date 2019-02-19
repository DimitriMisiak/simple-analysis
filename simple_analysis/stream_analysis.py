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
# BEGIN SCRIPTS
#==============================================================================
data_path = data_dir + '/tb18m005/tb18m005_S00'
fs, raw_stream = read_ac_data(data_path, 0)

N = raw_stream.shape[0]
L = N / fs

time_array = np.arange(0, L, fs**-1)
ind_off = int(N/10)

plt.figure('raw stream')
plt.plot(time_array[:ind_off], raw_stream[:ind_off])



def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

hp_stream = butter_highpass_filter(raw_stream, 3, fs)

pos_stream = hp_stream
pos_stream[pos_stream < 0] = 1e-13

plt.figure('filtered stream')
#plt.plot(time_array[:ind_off], hp_stream[:ind_off])
plt.plot(time_array[:ind_off], pos_stream[:ind_off])
plt.yscale('log')