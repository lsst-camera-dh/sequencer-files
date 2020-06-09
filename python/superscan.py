#! /usr/bin/env python
#
# Utilities to create and analyze the super-scan frames.
#
# Super-scan: series of frames in which the ADC trigger is moved within the pixel readout function
# by a given time increment for each frame.
# The ASPIC must be put in Transparent Mode (unless we are that interested in the DSI scan).
#
# Changelog:
# 2017-03-14: created by Claire Juramy to replicate code from LPNHE test bench.
#
#

import os
import copy
import numpy as np
import scope
from matplotlib import pyplot as plt
import rebtxt


def set_trigger_function(self, trigtime, trigfunc):
    """
    For the super-scan, sets the trigger at the right time in the function (and removes it elsewhere).
    :param trigtime:
    :param trigfunc: the base function
    :return:
    """
    # need to copy from the base function (to be able to re-use it)
    newtrigfunc = copy.deepcopy(trigfunc)
    # will wrap after total duration of function
    newtrigfunc.set_output_at_time(1, 'TRG', trigtime, wrap=True)
    self.reb.set_function(newtrigfunc.name, newtrigfunc)
    print newtrigfunc


def generate_seqfiles(self, modelfile, readfunc='ReadPixel', scanpoints=None):
    """
    Generates the sequencer timing files for the superscan based on the model file.
    :param self:
    :param exptype:
    :param exptime:
    :param tm:
    :param validamps:
    :return:
    """

    if scanpoints is None:
        scaniter = xrange(0, 200, 2)  # to be changed if pixel read time is higher
        niter = 100
    else:
        scaniter = scanpoints
        niter = len(scanpoints)

    # gets sequencer object
    seq = rebtxt.Sequencer.fromtxtfile(modelfile, verbose=False)

    # creates base function with no trigger signal
    trigfunc = seq.functions_desc[readfunc]['function']  # function object
    trigfunc.set_output_channel(0, 'TRG')  # clears all timeslice


    for iterscan, offset in enumerate(scaniter):
        # recreates the ReadPixel function with the right trigger
        try:
            self.set_trigger_function(offset, trigfunc)
        except:
            continue

        fname = "scantime_%d_%s" % (offset, os.path.split(modelfile)[1])


def getdata_superscan(datadir, listchan, listlines=None, listcols=None):
    """
    Offline reading of superscan files, with average over lines and/or columns.
    Directory should not have fits files with the same _xxx_ format.
    Now takes only image columns for average vs lines and image lines for average vs columns.
    :return:
    """

    # index files by time
    dictfiles = {}
    for fname in analysis.get_fits_indir(datadir):
        try:
            offset = int(fname.rsplit('_', 2)[1])
        except:
            continue
        dictfiles[offset] = fname

    # sort times
    dolines = False
    docols = False
    timeindex = sorted(dictfiles.keys())
    if listlines is not None:
        chanlines = np.empty((len(listchan), len(timeindex), len(listlines)))
        dolines = True
    else:
        chanlines = np.array([])
    if listcols is not None:
        chancols = np.empty((len(listchan), len(timeindex), len(listcols)))
        docols = True
    else:
        chancols = np.array([])

    # read data for each time
    for iterscan, offset in enumerate(timeindex):
        fname = dictfiles[offset]
        try:
            h = analysis.open_fits(fname)
        except:
            continue

        for n, c in enumerate(analysis.find_channels(h, listchan)):
            # for iterl, l in enumerate(listlines):
            #    chanlines[n, iterscan, iterl] = h[c].data[l, 10:].mean()
            if dolines:
                # removes first 10 columns (pre-scan, unstable)
                chanlines[n, iterscan, :] = h[c].data[:, 10:522].mean(axis=1)[listlines]
            if docols:
                # removes first 10 lines (bleed from serial register at high flux)
                chancols[n, iterscan, :] = h[c].data[10:2002, :].mean(axis=0)[listcols]
        h.close()
        del h

    return timeindex, chanlines, chancols


def plot_superscan_lines(listchan, listlines, listcols, timeindex, chanlines, chancols):
    """
    Offline plot of superscan from files, averaged over lines and/or columns.
    chanlines or chancols are = np.array([]) if not doing one or the other.
    :return:
    """
    if chanlines.any():
        plt.figure(figsize=(8, 5))
        ax = plt.subplot(111)
        plt.xlabel('Scan increment (10 ns)')
        plt.ylabel('Average of line')
        for chan in range(len(listchan)):
            for l in range(len(listlines)):
                ax.plot(timeindex, chanlines[chan, :, l], label='Ch %d - L %d' % (listchan[chan], listlines[l]))

        scope.set_legend_outside(ax)
        plt.title('Super-scan averaged over single line')

    if chancols.any():
        plt.figure(figsize=(8, 5))
        ax = plt.subplot(111)
        plt.xlabel('Scan increment (10 ns)')
        plt.ylabel('Average of column')
        for chan in range(len(listchan)):
            for l in range(len(listcols)):
                ax.plot(timeindex, chancols[chan, :, l], label='Ch %d - C %d' % (listchan[chan], listcols[l]))

        scope.set_legend_outside(ax)
        plt.title('Super-scan averaged over single column')

    plt.show()
