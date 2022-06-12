import numpy as np
import math
from darkrate_consts_sam import *

def readfile(filepath):
    word,words = 0,0
    ts, Vs1 = [], [] # seconds, volts


    with open(filepath) as fp: # this line opens the file and makes sure to close it when all is done
        line = fp.readline()
        while line: # start read file loop
            words = line.strip().split(',') # splits each line at a comma
                                                # the strip part makes sure there aren't any weird characters left over at the start or end of a line
            if (words[0] == 'TIME' and words[0] != ''): # finds where to start taking the data, may need to change 
                word = 1                                # for different files
                line = fp.readline() # get next line
                words = line.strip().split(',')
            if word == 1 and words[0] != '': # this ensures it starts recording the data lines only 
                ts.append(words[0].strip())
                Vs1.append(words[1].strip()) 
            line = fp.readline()
    return ts, Vs1

# function to search for single or multi photon events
def findcandidates(ts, Vs1):
    t_spacing = ts[1] - ts[0]
    npoints_window = int(t_window*1e-6/t_spacing) # number of points in window
    #print("npoints per window = ", npoints_window)
    all_integrals = []
    window_start_indices = []
    window_end_indices = []
    darkcount = 0
    # roll through data with a specified time window, take integrals and look for single photon candidates
    index_start = 0
    while index_start < (len(ts) - npoints_window):
        ts_sel = ts[index_start:(index_start + npoints_window)]
        Vs1_sel = Vs1[index_start:(index_start + npoints_window)]
        trace_integral = np.trapz(Vs1_sel, x=ts_sel)
        # only if integral is above the threshold and candidates are set to be accepted
        if trace_integral > V_threshold*1e-9:
            # only iterate dark count when integral is above threshold
            darkcount += 1
            all_integrals.append(trace_integral)
            window_start_indices.append(index_start)
            window_end_indices.append(index_start+npoints_window)
            #index_start += 1
            if t_buffer != 0:
                index_start += int(t_buffer*1e-6/t_spacing) 
            else: 
                index_start += 1
        else:
            # keep all integrals to see full spectrum of integrals
            all_integrals.append(trace_integral)
            window_start_indices.append(index_start)
            window_end_indices.append(index_start+npoints_window)
            index_start += 1
        

    return darkcount, np.array(all_integrals), np.array(window_start_indices), np.array(window_end_indices)

# function list indices of the windows that exceed integral threshold
def findwindows(ts, Vs1):
    t_spacing = ts[1] - ts[0]
    npoints_window = int(t_window*1e-6/t_spacing) # number of points in window
    window_start_indices = []
    window_end_indices = []

    # roll through data with a specified time window, take integrals and look for single photon candidates
    for index_start in range(0, len(ts) - npoints_window):
        ts_sel = ts[index_start:(index_start + npoints_window)]
        Vs1_sel = Vs1[index_start:(index_start + npoints_window)]
        trace_integral = np.trapz(Vs1_sel, x=ts_sel)
        # only if integral is above the threshold and candidates are set to be accepted
        if np.abs(trace_integral) > V_threshold*1e-9:
            window_start_indices.append(index_start)
            window_end_indices.append(index_start+npoints_window)

    return window_start_indices, window_end_indices

# get times and voltages for a specified csv file
def getData(filepath):
    times,voltages = readfile(filepath)
    ts = np.array(times, dtype='float')
    Vs1 = np.array(voltages, dtype='float')
    return ts, Vs1