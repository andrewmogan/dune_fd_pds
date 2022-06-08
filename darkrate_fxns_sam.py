import numpy as np
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
    photon_candidates = []

    # for including a buffer zone after each first photon candidate
    keepCandidate = True
    keepCandidate_starttime = 0
    keepCandidate_timesincestart = 0
    # roll through data with a specified time window, take integrals and look for single photon candidates
    for index_start in range(0, len(ts) - npoints_window):
        ts_sel = ts[index_start:(index_start + npoints_window)]
        Vs1_sel = Vs1[index_start:(index_start + npoints_window)]
        trace_integral = np.trapz(Vs1_sel, x=ts_sel)
        # only if integral is above the threshold and candidates are set to be accepted
        if trace_integral > V_threshold*1e-9 and keepCandidate == True:
            photon_candidates.append(trace_integral)
            keepCandidate == False
            keepCandidate_starttime = ts[index_start]
        # only happens after first accepted integral, increments time since start
        elif keepCandidate == False and keepCandidate_timesincestart < t_buffer*1e-6:
            keepCandidate_timesincestart += t_spacing 
        # only happens once the start of the interval surpasses buffer: candidates now set to be accepted
        elif keepCandidate == False and keepCandidate_timesincestart > t_buffer*1e-6:
            keepCandidate = True

    return photon_candidates

# get times and voltages for a specified csv file
def getData(filepath):
    times,voltages = readfile(filepath)
    ts = np.array(times, dtype='float')
    Vs1 = np.array(voltages, dtype='float')
    return ts, Vs1