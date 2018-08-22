# !/usr/bin/env python

# python raftstats.py [<path>/s00/tm-scan.fits]
# (expects the name and path for the first of the image files of the raft, will go looking for the others)

import os
import sys
import pyfits
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors as mplcol

def get_fits_raft(inputfile='', datadir=''):
    """
    Builds up list of all raft files and list of segment names.
    :param datadir: for tree structure, directory where data is stored. Root path if all files are in the same dir.
    :param inputfile: the first file (00_). Can also work with full path if datadir is not given.
    :return:
    """
    # starts with 00 through 22
    seglist = ["%d%d" % (i, j) for i in range(3) for j in range(3)]

    # if all files in same directory
    if inputfile:
        if '00_0_' in inputfile:  # new numbering scheme from eTraveler
            raftfits = [os.path.join(datadir, inputfile.replace("00_0", s + '_' + s[1:])) for s in seglist]
        elif '00_' in inputfile:
            raftfits = [os.path.join(datadir, inputfile.replace("00_", s + '_')) for s in seglist]
        else:
            raftfits = [os.path.join(datadir, inputfile.replace("00-", s + '-')) for s in seglist]
    # tree structure
    else:
        raftfits = []
        for segstr in seglist:
            d = os.path.join(datadir, 'S%s' % segstr)
            for f in os.listdir(d):
                print f
                if f[-4:] == 'fits' and os.stat(os.path.join(d, f)).st_size > 1e6:
                    # one file per directory
                    raftfits.append(os.path.join(d, f))
                    break

    return raftfits, seglist


def repr_stats(fitsfile, recalc=False, ROI1rows=slice(100, 1900), ROI1cols=slice(20, 500),
               ROI2rows=slice(100, 1900), ROI2cols=slice(540, 576)):
    """
    String from statistics stored in extension headers or recalculated.
    :return:
    """

    hdulist = pyfits.open(fitsfile)
    statstr = ""
    if recalc:
        for i in range(16):
            h = hdulist[i + 1].header
            data = hdulist[i + 1].data
            statstr += "%s %10.2f %10.2f %10.2f %8.2f\n" % (h['EXTNAME'], data[ROI1rows, ROI1cols].mean(),
                                                            data[ROI1rows, ROI1cols].std(),
                                                            data[ROI2rows, ROI2cols].mean(),
                                                            data[ROI2rows, ROI2cols].std())

    else:
        for i in range(16):
            h = hdulist[i + 1].header
            statstr += "%s %10.2f %10.2f %10.2f %8.2f\n" % (h['EXTNAME'], h['AVERAGE'], h['STDEV'],h['AVGBIAS'], h['STDVBIAS'])

    hdulist.close()
    del hdulist

    return statstr


def print_header_stats(fitsfile, recalc=False):
    """
    String from statistics stored in extension headers.
    :return:
    """
    print repr_stats(fitsfile, recalc=recalc)


def plothisto_overscan(fitsfile, ROIrows=slice(100, 1900), ROIcols=slice(540, 576)):
    """
    Display distribution of data in overscan region for each channel of a CCD file.
    :param fitsfile:
    :return:
    """
    hdulist = pyfits.open(fitsfile)

    fig, axes = plt.subplots(nrows = 4, ncols = 4, figsize=(13, 9))
    #color_idx = [plt.cm.jet(i) for i in np.linspace(0, 1, 16)]

    # single CCD plot
    for i in range(16):
        h = hdulist[i + 1].header
        d = hdulist[i + 1].data[ROIrows , ROIcols].flatten()
        #print h['EXTNAME'], h['AVGBIAS'], d.mean(), h['STDVBIAS'], d.std()

        ax = axes[i / 4, i % 4]

        # the histogram of the data
        # one bin per value
        num_bins = np.amax(d) - np.amin(d)
        n, bins, patches = ax.hist(d, num_bins)
        #print bins[num_bins/2 : num_bins/2 + 10]
        if i/4 == 3:
            ax.set_xlabel('ADU')
        if i%4 == 0:
            ax.set_ylabel('Number of pixels')
        ax.set_title(h['EXTNAME'])

    hdulist.close()
    del hdulist

    datadir, dataname = os.path.split(fitsfile)
    dataname = os.path.splitext(dataname)[0]
    plt.savefig(os.path.join(datadir, "histoverscan-%s.png" % dataname))
    plt.show()


def average_1D_tofile(listfile, listsensor, datadir, axis, ROI, norm=False):
    """
    Output to file of frames averaging over one direction.
    0 = average over lines, stack for each column
    1 = average over columns, stack for each line
    """
    outfile = open(os.path.join(datadir, 'average1D.txt'), 'w')

    for num, hfile in enumerate(listfile):
        try:
            h = pyfits.open(os.path.join(datadir, hfile))
        except:
            continue

        for channel in range(16):
            outfile.write('%s-%02d\t\t' % (listsensor[num], channel))
        outfile.write('\n')

        #print h[1].data.shape
        imax = h[1].data.shape[0 if axis else 1]
        linedata = np.zeros((16, imax))
        linestd = np.zeros((16, imax))

        for channel in range(16):
            if axis == 0:
                linedata[channel, :] = h[channel + 1].data[ROI, :].mean(axis=axis)
                linestd[channel, :] = h[channel + 1].data[ROI, :].std(axis=axis)
            else:
                linedata[channel, :] = h[channel + 1].data[:, ROI].mean(axis=axis)
                linestd[channel, :] = h[channel + 1].data[:, ROI].std(axis=axis)
            # option to normalize
            if norm:
                linedata[channel, :] = linedata[channel, :] - linedata[channel, -30:].mean()

        for i in range(imax):
            for channel in range(16):
                outfile.write("%.2f\t%.2f\t" % (linedata[channel, i], linestd[channel, i] ))
            outfile.write('\n')

        h.close()
        del h
    outfile.close()


def average_1D_toplot(fitsfile, datadir, axis, ROIlines, ROIcols, norm=False, title=''):
    """
    Output to plot of averaging over one direction for a single frame.
    0 = average over lines
    1 = average over columns
    """
    h = pyfits.open(os.path.join(datadir, fitsfile))

    fig, axes = plt.subplots(nrows = 2, ncols = 1, figsize=(10, 10))
    color_idx = [plt.cm.jet(i) for i in np.linspace(0, 1, 16)]

    for channel in range(16):
        if norm:
            axes[0].plot(h[channel + 1].data[ROIlines, ROIcols].mean(axis=axis)
                         -  h[channel + 1].data[-30:, -30:].mean(), color=color_idx[channel], label="%d" % channel)
        else:
            axes[0].plot(h[channel + 1].data[ROIlines, ROIcols].mean(axis=axis), color=color_idx[channel], label="%d" % channel)
        axes[1].plot(h[channel + 1].data[ROIlines, ROIcols].std(axis=axis), color=color_idx[channel], label="%d" % channel)

    if title:
        plt.suptitle(title)
    axes[0].grid(True)
    axes[1].grid(True)
    if norm:
        axes[0].set_ylabel("Average, normalized  (ADU)")
    else:
        axes[0].set_ylabel("Average (ADU)")

    axes[1].legend(bbox_to_anchor=(1.05, 0), loc='lower left', borderaxespad=0.)

    plt.savefig(os.path.join(datadir, 'average1D-%s.png' % title))
    plt.show()


def roistats_raft(raftsfits, ROIrows=slice(100, 1900), ROIcols=slice(530, 576)):
    """
    Statistics in ROI for raft.
    :param raftsfits: file list
    :return:
    """
    allmean = np.zeros(16 * len(raftsfits))
    allstd = np.zeros(16 * len(raftsfits))

    for num, fl in enumerate(raftsfits):
        try:
            h = pyfits.open(fl)
        except:
            continue
        for i in range(1, 17):
            allmean[num * 16 + i - 1] = h[i].data[ROIrows, ROIcols].mean()
            allstd[num * 16 + i - 1] = h[i].data[ROIrows, ROIcols].std()
        h.close()
        del h

    return allmean, allstd


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


def plot_corrcoef_raft(raftfits, ROIrows=slice(10, 1990), ROIcols=slice(512, 521), xylabels=None, title=''):
    """
    Plot of correlation coefficients over list of CCD images.
    :param raftsfits:
    :param ROIrows:
    :param ROIcols:
    :return:
    """
    datadir, dataname = os.path.split(raftfits[0])
    dataname = os.path.splitext(dataname)[0]

    a = corrcoef_raft(raftfits, ROIrows, ROIcols)
    fig, ax = plt.subplots(figsize=(8, 8))
    cax = ax.imshow(a, cmap=plt.get_cmap('jet'), norm=mplcol.Normalize(vmax=1, clip=True), interpolation='none')
    if title:
        ax.set_title('Correlation for %s' % title)
    else:
        ax.set_title('Correlation for %s' % dataname)
    ax.set_xticks(np.arange(0, 16*len(raftfits), 16))
    ax.set_yticks(np.arange(0, 16*len(raftfits), 16))
    if xylabels:
        ax.set_xticklabels(xylabels)
        ax.set_yticklabels(xylabels)
    cbar = fig.colorbar(cax, orientation='vertical')

    plt.savefig(os.path.join(datadir, "corr-%s.png" % dataname))
    plt.show()


if __name__ == '__main__':
    datadir = sys.argv[1]
    # for test files
    #raftfits = [os.path.join(datadir, f) for f in sorted(os.listdir(datadir))]
    # for tree structure
    raftfits = get_fits_raft('', datadir)[0]

    outstats = open(os.path.join(datadir, "statsheader.txt"), 'w')
    for f in raftfits:
        if os.path.splitext(f)[1] in [".fits", ".fz"]:
            #print f
            #outstats.write(f+'\n')
            #print_header_stats(f)
            #plothisto_overscan(f)
            outstats.write(repr_stats(f, True))

    outstats.close()

#ls = ['S%d%d' % (i, j)) for i in range(3) for j in range(3)]
#ld = [os.path.join(datadir, '%s' % seg) for seg in ls]
#raftfits = [os.path.join(d, f) for d in ld for f in os.listdir(d) if ".fits" in f]
#raftstats.plot_corrcoef_raft(raftfits, ROIcols=slice(530,576), xylabels=ls,title='run-8000 for modified RTM10')
