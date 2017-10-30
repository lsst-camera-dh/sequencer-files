# !/usr/bin/env python

# Displays a scope-like view of the CCD output waveforms for the whole raft.
#
# Changelog
# 20161207: C. Juramy, initialized from LPNHE bench code.
#
# Syntax as main:
# python multiscope.py [s00-tm-scan.fits]
# python multiscope.py [<path>/s00/tm-scan.fits]
# (expects the name and path for the first of the image files of the raft, will go looking for the others)
#
# Syntax in a script:
# import multiscope
# multiscope.raft_display("tm-scan.fits")

import sys
import os.path
import numpy as np
from matplotlib import pyplot as plt
import scope
import pyfits


def get_scandata_raft(inputfile, datadir=''):
    """
    Builds up list of data arrays from all raft files (one array per CCD), plus list of segment names.
    :param datadir: optional, directory where data is stored
    :param inputfile: the first file (for Reb0 or S00). Full path if datadir is not given
    :return:
    """
    raftarrays = []
    if os.path.splitext(inputfile)[1] in [".fits", ".fz"]:
        # starts with 00 through 22
        seglist = ["%d%d" % (i, j) for i in range(3) for j in range(3)]
        # when REB2 data is missing
        #seglist = ["%d%d" % (i, j) for i in range(2) for j in range(3)]
        #raftfits = [inputfile.replace("00_", s + '_') for s in seglist]
        raftfits = [inputfile.replace("00", s) for s in seglist]
        for f in raftfits:
            raftarrays.append(scope.get_scandata_fromfile(f, datadir))
    else:
        # starts with Reb0 through Reb2
        reblist = ["Reb0", "Reb1", "Reb2"]
        rebraws = [inputfile.replace("Reb0", s) for s in reblist]
        seglist = [r + "-%s" % stripe for r in reblist for stripe in ['A', 'B', 'C'] ]
        for f in rebraws:
            fullreb = scope.get_scandata_fromfile(f, datadir)  # 3D array: 48 channels, lines, columns
            #print fullreb.shape
            raftarrays.extend([a for a in np.split(fullreb, 3, axis=0)])  # splits REB data into 3 CCDs

    return raftarrays, seglist

def raft_display_allchans(inputfile, datadir='', suptitle=''):
    """
    Builds up data from all raft files and display scans.
    :param datadir: optional, directory where data is stored
    :param inputfile: the first file (for Reb0 or S00). Full path if datadir is not given
    :param suptitle: personalized title
    :return:
    """
    raftarrays, seglist = get_scandata_raft(inputfile, datadir)

    fig, axes = plt.subplots(nrows = 3, ncols = 3, figsize=(15, 9))
    # when REB2 data is missing
    # fig, axes = plt.subplots(nrows = 2, ncols = 3, figsize=(15, 9))
    color_idx = [plt.cm.jet(i) for i in np.linspace(0, 1, 16)]

    # plot all channels, with one subplot per CCD
    listaxes = []
    for num,tmscope in enumerate(raftarrays):
        ax = axes[num  / 3, num  % 3 ]

        # single CCD plot
        for c in range(16):
            # image extensions are labeled as 'Segment00' in CCS
            # they are in extensions 1 to 16
            #print tmscope.shape
            tmchan = tmscope[c].mean(axis=0)
            ax.plot(tmchan, label=c, color=color_idx[c])
            #if num == 0:
                # for common legend
                #listaxes.append(ax)

            ax.set_xlim(0, 255)
            ax.set_xticks(np.arange(0, 256, 32))
            ax.set_title(seglist[num])

            if num%3 == 0:
                ax.set_ylabel('Scan (ADU)')
            if num/3 == 2:
                ax.set_xlabel('Time increment (10 ns)')
            ax.grid(True)


    ax.legend(bbox_to_anchor=(1.05, 0), loc='lower left', borderaxespad=0.)

    #plt.legend(handles=listaxes,loc = 'upper center', bbox_to_anchor = (0.5, 0), bbox_transform = plt.gcf().transFigure)
    dataname = scope.get_rootfile(inputfile)
    if suptitle:
        plt.suptitle(suptitle, fontsize='x-large')
    else:
        plt.suptitle(dataname)
    plt.savefig(os.path.join(datadir, "multiscope-%s.png" % dataname))
    plt.show()


def get_extension_header(imgcols, imglines, CCDchan, fitshdu, detstring):
    """
    Builds FITS extension header with position information for each channel.
    :type CCDchan: int
    :type fitshdu: pyfits.HDU
    :type detstring: basestring
    :type channels: list
    :type displayborders: bool
    :return:
    """
    extheader = fitshdu.header
    extheader["NAXIS1"] = imgcols
    extheader["NAXIS2"] = imglines
    extheader['DETSIZE'] = detstring
    extheader['CHANNEL'] = CCDchan

    parstringlow = '1:%d' % imglines
    parstringhigh = '%d:%d' % (2 * imglines, imglines + 1)
    colwidth = imgcols
    extheader['DATASEC'] = '[1:%d,1:%d]' % (imgcols, imglines)

    numCCD = CCDchan / 16
    chan = CCDchan - numCCD * 16
    if chan < 8:
        pdet = parstringhigh
        # REB3 with swapped channels
        #si = colwidth * (7 - CCDchan - 8 * numCCD) + 1
        #sf = colwidth * (7 - CCDchan - 8 * numCCD + 1)
        # REB5
        si = colwidth * (CCDchan - 8 * numCCD) + 1
        sf = colwidth * (CCDchan - 8 * numCCD + 1)
    else:
        pdet = parstringlow
        si = colwidth * (CCDchan - 8 * (numCCD + 1) + 1)
        sf = colwidth * (CCDchan - 8 * (numCCD + 1)) + 1

    extheader['DETSEC'] = '[%d:%d,%s]' % (si, sf, pdet)


def reframe_scope_frames(listfits):
    """
    Corrects datasec keywords based on real frame size.
    :param listfits:
    :return:
    """
    for f in listfits:
        h = pyfits.open(f)
        imgcols = h[1].header['naxis1']
        imglines = h[1].header['naxis2']
        detstring = '[1:%d,1:%d]' % (imgcols * 8, 2 * imglines)
        # Create HDU list
        primaryhdu = pyfits.PrimaryHDU()
        primaryhdu.header = h[0].header.copy()
        primaryhdu.header['DETSIZE'] = (detstring, 'NOAO MOSAIC keywords')
        hcopy = pyfits.HDUList([primaryhdu])

        #print h.info()
        for extnum in range(1,17,1):
            exthdu = pyfits.ImageHDU(data=h[extnum].data)
            get_extension_header(imgcols, imgcols, extnum-1, exthdu, detstring)
            hcopy.append(exthdu)

        hcopy.writeto(f[:-5] + "f.fz", clobber=True)


if __name__ == '__main__':

    itm = sys.argv[1]
    raft_display_allchans(itm)
