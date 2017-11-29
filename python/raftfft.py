# !/usr/bin/env python

import sys
import os.path
import pyfits
import re
import numpy as np
from matplotlib import pyplot as plt
from raftstats import get_fits_raft
from scope import get_rootfile

def get_detsize(detstring):
    """
    Converts string in the format [x1:x2, y1:y2] to indexes. Accepts empty indexes.
    :param detstring:
    :return:
    """
    m = re.match("\[(\d*)\:(\d*),([ ]*)(\d*)\:(\d*)\]", detstring)
    indexes = []
    for i in [1, 2, 4, 5]:
        try:
            indexes.append(int(m.group(i)))
        except:
            if i in [1, 4]:
                indexes.append(0)
            else:
                indexes.append(-1)

    return indexes


def get_frame_coords(detstring):
    """
    Gets the coordinates of dark and light areas from the header or by default.
    :return:
    """
    try:
        ins = get_detsize(detstring)
        imgcols = ins[1] - ins[0] + 1
        colstart = ins[0] - 1
        imglines = ins[3]
    except:
        imgcols = 512
        colstart = 10
        imglines = 2002

    return imglines, colstart, imgcols


def fft1d_col(hdulist, ax, sumchannels=False, borders=False, npad=0):
    """
    Computes 1-dimensional FFT over each line and outputs power spectrum for each channel/ all stacked.
    :param hdulist:
    :param ax: matplotlib ax for the plot
    :param sumchannels: if all channels should be stacked
    :param borders: if area outside of physical detector should be included
    :param npad: if padding with zeros to avoid aliasing
    :return:
    """
    fftstack = []
    countchan = 0
    color_idx = [plt.cm.jet(i) for i in np.linspace(0, 1, 16)]

    for c in range(1,17):
        hdr = hdulist[c].header
        if borders:
            img = hdulist[c].data
            imglines, imgcols = img.shape
        else:
            imglines, colstart, imgcols = get_frame_coords(hdr['DATASEC'])
            img = hdulist[c].data[50:imglines, colstart+20:colstart + imgcols]

        # for RTM8: need to subtract column average
        baseline = img.mean(axis=0)
        img = np.subtract(img, baseline)

        # fft along columns, average over lines
        #  padding with zeroes avoids aliasing but can introduce artifacts
        # average over power spectrum (modulus, squared)
        f = np.mean(np.square(np.absolute((np.fft.rfft(img, n=imgcols + npad, axis=1)))), axis=0)

        if sumchannels:
            # add in place, operate on power spectrum
            if countchan == 0:
                fftstack = f
            else:
                fftstack += f
            countchan += 1
        else:
            # square root and plot
            f = np.sqrt(f)
            ax.plot(f, label="C%02d" % (c-1), color=color_idx[c-1])

    if sumchannels:
        # plot stack
        ax.plot(np.sqrt(fftstack)/countchan)

    ax.set_xlabel("Spatial frequency (columns)")
    ax.set_ylabel('FFT amplitude spectrum')
    ax.grid()


def raft_fft1d_col(inputfile, datadir='', suptitle=''):
    """
    Builds up data from all raft files and display scans.
    :param datadir: optional, directory where data is stored
    :param inputfile: the first file (for Reb0 or S00). Full path if datadir is not given
    :param suptitle: personalized title
    :return:
    """
    raftarrays, seglist = get_fits_raft(inputfile, datadir)

    #if not sumchannels:
    fig, axes = plt.subplots(nrows = 3, ncols = 3, figsize=(15, 9))
    # when REB2 data is missing
    # fig, axes = plt.subplots(nrows = 2, ncols = 3, figsize=(15, 9))

    #else:
     #   fig, axes = plt.subplots(nrows = 3, ncols = 3, figsize=(15, 9))

    # plot all channels, with one subplot per CCD

    for num,fitsname in enumerate(raftarrays):
        ax = axes[num  / 3, num  % 3 ]
        print("Computing FFT for %s" % fitsname)
        hdulist = pyfits.open(fitsname)
        fft1d_col(hdulist, ax, sumchannels=False, borders=False, npad=0)
        hdulist.close()
        del hdulist

    ax.legend(bbox_to_anchor=(1.05, 0), loc='lower left', borderaxespad=0.)

    dataname = get_rootfile(inputfile)
    if suptitle:
        plt.suptitle(suptitle, fontsize='x-large')
    plt.savefig(os.path.join(datadir, "raftfft-%s.png" % dataname))
    plt.show()
