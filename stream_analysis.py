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
data_path = data_dir + '/tb19m002/tb19m002_S00'
fs, raw_stream = read_ac_data(data_path, 0)

N = raw_stream.shape[0]
L = N / fs

time_array = np.arange(0, L, fs**-1)
ind_off = int(N)

plt.figure('raw stream')
plt.plot(time_array[:ind_off], raw_stream[:ind_off])


### Definng high-pass filter function
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
plt.plot(time_array[:ind_off], hp_stream[:ind_off])
#plt.plot(time_array[:ind_off], pos_stream[:ind_off])
#plt.yscale('log')
plt.grid(True)

thresh = 4e-7 #V
plt.axhline(thresh, ls='--', color='red')

### locating local maxima above given threshold
def local_maxima_above_threshold(array, thresh):
    """ Return the index array of the local maximum of the stream, passing the
    given threshold.

    Parameters
    ==========
    array : np.ndarray
        Filtered Data stream

    thresh : float
        Energy threshold

    Return
    ======
    index_array : np.ndarray
        Array of the index of the local maxima.

    amp_array : np.ndarray
        Array of the local maximal amplitude
    """
    # index of the value passing the threshold
    pass_index = np.where(array > thresh)[0]

    # length of the passing index array
    num = pass_index.shape[0]

    # empty lists to gather the final indexes and maximums
    index_list = list()

    # intialize the highest amplitude index and the last index
    i0 = 0
    i_last = 0

    # loop over all the passing indexes except the first
    for i in range(1, num-1):

        ind = pass_index[i]
        ind_last = pass_index[i_last]

        # check if contiguous
        if ind - ind_last == 1:

            # check hierarchy, save highest amplitude index
            amp = array[ind]
            amp0 = array[pass_index[i0]]
            if amp > amp0:
                i0 = i

        # if not contiguous
        else:
#            print ind - ind_last
            # save last maxima and update i0
            index_list.append(i0)
            i0 = i

        # update the last index
        i_last = i

    return pass_index[np.array(index_list)]


loc_max = local_maxima_above_threshold(hp_stream[:ind_off], thresh)

### apply the deadtime cut on local maxima to extract events
def deadtime_cut(index_array, time_array, stream_array, deadtime=0.5):
    """ Apply a deadtime constraint on the local maximum so that it can be
    considered as a legitimate event.
    If two maxima are seperated by less than the deadtime, only the highest
    is considered an event.

    Parameters
    ==========
    index_array: numpy.ndarray
        Array of the indexes of the local maximum of the stream.
        (output of the local_maxima_above_threshold function)

    time_array: numpy.ndarray
        Time array

    stream_array: numpy.ndarray
        Stream array, to recover amplitude.

    deadtime : float
        Deadtime after a pulse.

    Return
    ======
    index_event: numpy.ndarray
        Array of the indexes of the events in the stream
    """
    # length of the passing index array
    num = index_array.shape[0]

    # empty lists to gather the final indexes and maximums
    index_list = list()

    # intialization
    i_max = 0
    i_last = 0

    # loop over all the indexes of the local maximum except the first
    for i in range(1, num-1):

        ind = index_array[i]
        ind_max = index_array[i_max]
        ind_last = index_array[i_last]

        # check if deadtime is ok
        time = time_array[ind]
        time_max = time_array[ind_max]
        time_last = time_array[ind_last]
        dt_last = time - time_last
        dt_max = time - time_max

        if dt_last < deadtime:
            # check hierarchy
            amp = stream_array[ind]
            amp_max = stream_array[ind_max]
            amp_last = stream_array[ind_last]

            if dt_max < deadtime:

                if amp > amp_max:
                    i_max = i
                    i_last = i

                if amp < amp_max:
                    i_last = i

            else:

                if amp > amp_last:
                    index_list.append(i_max)
                    i_max = i
                    i_last = i


                if amp < amp_last:
                    i_last = i

        else:
            index_list.append(i_max)
            i_max = i
            i_last = i


    return index_array[np.array(index_list)]

loc_event = deadtime_cut(loc_max, time_array, hp_stream)

time_event = time_array[loc_event]

for time in time_event:
    plt.axvline(time, ls='-.', color='black')

amp_event = hp_stream[loc_event]

print 'DONE'
# ENERGY SPECTRUM !
plt.close('energy spectrum')
plt.figure('energy spectrum')
plt.hist(amp_event, bins=20000)
plt.xscale('log')
plt.yscale('log')
#
plt.figure('time event')
plt.plot(time_event, amp_event, ls='none', marker='+')
plt.grid(True)

