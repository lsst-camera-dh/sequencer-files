# !/usr/bin/env python

# python raftstats.py [<path>/s00/tm-scan.fits]
# (expects the name and path for the first of the image files of the raft, will go looking for the others)

import os
import sys
import pyfits
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors as mplcol

def get_fits_raft(inputfile, datadir=''):
    """
    Builds up list of all raft files and list of segment names.
    :param datadir: optional, directory where data is stored
    :param inputfile: the first file (S00/ or 00_). Full path if datadir is not given
    :return:
    """
    # starts with 00 through 22
    seglist = ["%d%d" % (i, j) for i in range(3) for j in range(3)]
    raftfits = [os.path.join(datadir, inputfile.replace("00", s)) for s in seglist]

    return raftfits, seglist


def print_header_stats(fitsfile):
    """
    Prints out statistics stored in extension headers.
    :return:
    """

    hdulist = pyfits.open(fitsfile)

    for i in range(16):
        h = hdulist[i + 1].header
        print h['EXTNAME'], h['AVERAGE'], h['STDEV'],h['AVGBIAS'], h['STDVBIAS']

    hdulist.close()
    del hdulist


def plothisto_overscan(fitsfile):
    """
    Display distribution of data in overscan region for each channel of a CCD file.
    :param fitsfile:
    :return:
    """
    hdulist = pyfits.open(fitsfile)

    fig, axes = plt.subplots(nrows = 4, ncols = 4, figsize=(12, 9))
    #color_idx = [plt.cm.jet(i) for i in np.linspace(0, 1, 16)]

    # single CCD plot
    for i in range(16):
        h = hdulist[i + 1].header
        d = hdulist[i + 1].data[10: , 530:].flatten()
        #print h['EXTNAME'], h['AVGBIAS'], d.mean(), h['STDVBIAS'], d.std()

        ax = axes[i / 4, i % 4]

        # the histogram of the data
        # one bin per value
        num_bins = np.amax(d) - np.amin(d)
        n, bins, patches = ax.hist(d, num_bins)
        #print bins[num_bins/2 : num_bins/2 + 10]

        ax.set_xlabel('ADU')
        ax.set_ylabel('Number of pixels')
        ax.set_title(h['EXTNAME'])

    hdulist.close()
    del hdulist

    datadir, dataname = os.path.split(fitsfile)
    dataname = os.path.splitext(dataname)[0]
    plt.savefig(os.path.join(datadir, "histoverscan-%s.png" % dataname))
    plt.show()


def corrcoef_raft(raftsfits, ROIrows=slice(10, 1990), ROIcols=slice(512, 521)):
    """
    Correlation over one or more CCDs. Original from Paul, expanded for several CCDs and streamlined.
    :param raftsfits: file list
    :return:
    """
    stackh = []
    #nccd = len(raftsfits)

    for fl in raftsfits:
        h = pyfits.open(fl)
        for i in range(1, 17):
            stackh.append(h[i].data[ROIrows, ROIcols].ravel())
        h.close()
        del h
    stackh = np.stack(stackh)

    a = np.corrcoef(stackh)
    # a.shape is (nccd * 16, nccd * 16)
    return a


def plot_corrcoef_raft(raftsfits, ROIrows=slice(10, 1990), ROIcols=slice(512, 521)):
    """
    Plot of correlation coefficients over list of CCD images.
    :param raftsfits:
    :param ROIrows:
    :param ROIcols:
    :return:
    """
    datadir, dataname = os.path.split(raftsfits[0])
    dataname = os.path.splitext(dataname)[0]

    a = corrcoef_raft(raftsfits, ROIrows, ROIcols)
    fig, ax = plt.subplots(figsize=(8, 8))
    cax = ax.imshow(a, cmap=plt.get_cmap('jet'), norm=mplcol.Normalize(vmax=0.3, clip=True))
    ax.set_title('Correlation for %s' % dataname)
    cbar = fig.colorbar(cax, orientation='vertical')

    plt.savefig(os.path.join(datadir, "corr-%s.png" % dataname))
    plt.show()


if __name__ == '__main__':
    # temporary for test files
    datadir = sys.argv[1]
    raftfits = [os.path.join(datadir, f) for f in os.listdir(datadir)]
    for f in raftfits:
        if os.path.splitext(f)[1] in [".fits", ".fz"]:
            print f
            print_header_stats(f)
            #plothisto_overscan(f)

#ld = [os.path.join(datadir, 'S%d%d' % (i, j)) for i in range(3) for j in range(3)]
#raftfits = [os.path.join(d, f) for d in ld for f in os.listdir(d)]