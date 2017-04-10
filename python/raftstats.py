# !/usr/bin/env python

# python raftstats.py [<path>/s00/tm-scan.fits]
# (expects the name and path for the first of the image files of the raft, will go looking for the others)

import os
import sys
import pyfits

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


if __name__ == '__main__':
    # temporary for test files
    datadir = sys.argv[1]
    raftfits = [os.path.join(datadir, f) for f in os.listdir(datadir)]
    for f in raftfits:
        if os.path.splitext(f)[1] in [".fits", ".fz"]:
            print f
            print_header_stats(f)

