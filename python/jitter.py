# dedicated to jitter measurement on scan waveforms

import os
import sys
import pyfits
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors as mplcol
import raftstats


def get_scan_data(hfile, datadir, ROI=slice(1, 1000)):
    """
    Produces arrays with average and standard deviation of scans.
    """
    fitsfile = os.path.join(datadir, hfile)
    try:
        h = pyfits.open(fitsfile)
    except:
        print("Failed to open %s" % fitsfile)
        return [], []

    imax = h[1].data.shape[1]
    linedata = np.zeros((16, imax))
    linestd = np.zeros((16, imax))

    for channel in range(16):
        linedata[channel, :] = h[channel + 1].data[ROI, :].mean(axis=0)
        linestd[channel, :] = h[channel + 1].data[ROI, :].std(axis=0)

    h.close()
    del h

    return linedata, linestd


def get_raft_jitter(listfile, listsensor, datadir, RObaseline, ROjump):

    allslope = np.zeros(16 * len(listfile))
    alljitter = np.zeros(16 * len(listfile))
    colors = [plt.cm.jet(i) for i in np.linspace(0, 1, len(listfile))]
    basename = os.path.splitext(os.path.basename(listfile[0]))[0]

    fig, ax = plt.subplots(figsize=(12, 8))
    outfile = open(os.path.join(datadir, 'calcjitter-%s.txt' % basename), 'w')
    medianjitter = np.zeros(len(listfile))

    for num, hfile in enumerate(listfile):
        linedata, linestd = get_scan_data(hfile, datadir)
        if not(linestd.any()) or not(linedata.any()):
            continue

        stdbase = linestd[:, RObaseline].mean(axis=1)
        indexmax = np.argmax(linestd[:, ROjump], axis=1) + ROjump.start
        timejitter = np.zeros(16)

        for c in range(16):
            allslope[c + num * 16] = (linedata[c, indexmax[c] + 1] - linedata[c, indexmax[c] - 1]) * 0.05  # in ADU/ns
            peakstd = linestd[c, indexmax[c]]
            alljitter[c + num * 16] = np.sqrt((peakstd ** 2) - (stdbase[c] ** 2))
            timejitter[c] = alljitter[c + num * 16]/allslope[c + num * 16]
            outfile.write("S%s-%02d %.2f %d %.2f %.2f %.2f %.3f\n" % \
                  (listsensor[num], c, stdbase[c], indexmax[c], peakstd, allslope[c + num * 16],
                   alljitter[c + num * 16], timejitter[c]))

        # plot per sensor
        ax.plot(allslope[num * 16: (num + 1) * 16], alljitter[num * 16: (num + 1) * 16], 'o', color=colors[num], label=listsensor[num])
        # jitter estimate per sensor (could also do a fit)
        timejitter.sort()
        medianjitter[num] = (timejitter[7]+timejitter[8]) * 0.5

    outfile.close()

    ax.set_xlabel('Slope (ADU/ns)')
    ax.set_ylabel('Jitter (ADU)')
    ax.grid()
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.85, box.height])
    plt.legend(bbox_to_anchor=(1.07, 1), loc=2, borderaxespad=0.)
    plt.title(basename)
    plt.savefig(os.path.join(datadir, "jitter-%s.png" % basename))
    #plt.show()

    return medianjitter

def get_raft_integration_bounds(listfile, listsensor, medianjitter, datadir, RDstart, RDstop, RUstart, RUstop):

    basename = os.path.basename(listfile[0])[:-5]
    outfile = open(os.path.join(datadir, 'RDRUbounds-%s.txt' % basename), 'w')

    for num, hfile in enumerate(listfile):
        linedata, linestd = get_scan_data(hfile, datadir)
        if not(linestd.any()) or not(linedata.any()):
            continue

        for c in range(16):
            RDamplitude = abs(linedata[c, RDstart] - linedata[c, RDstop])
            RUamplitude = abs(linedata[c, RUstart] - linedata[c, RUstop])
            jitternoise = np.sqrt(RDamplitude ** 2 + RUamplitude ** 2) * medianjitter[num]/(RDstop - RDstart) * 0.1
            outfile.write("S%s-%02d %d %d %d %d %d %d %.3f %.2f\n" %
                          (listsensor[num], c, linedata[c, RDstart], linedata[c, RDstop],
                           linedata[c, RUstart], linedata[c, RUstop], RDamplitude, RUamplitude,
                           medianjitter[num], jitternoise))

    outfile.close()


def get_raft_integration_total(listfile, listsensor, datadir, RDstart, RDstop, RUstart, RUstop):

    basename = os.path.basename(listfile[0])[:-5]
    outfile = open(os.path.join(datadir, 'RDRUtotals-%s.txt' % basename), 'w')

    for num, hfile in enumerate(listfile):
        linedata, linestd = get_scan_data(hfile, datadir)
        if not(linestd.any()) or not(linedata.any()):
            continue

        for c in range(16):
            baseline = linedata[c, RDstart - 20:RDstart - 5].mean()
            RDamplitude = linedata[c, RDstop + 5:RUstart - 10].mean()
            RUamplitude = linedata[c, RUstop + 5:RUstop + 25].mean()
            outfile.write("S%s-%02d %.2f %.2f %.2f %.2f %.2f\n" %
                          (listsensor[num], c, baseline, RDamplitude, RUamplitude,
                           abs(RDamplitude - baseline), abs(RUamplitude - RDamplitude)))

    outfile.close()


#datadir = '/Users/nayman/Documents/REB/TS8/RTM8/singleclockscans/singleS1'
#tmjitterfile = "00_bias2.fits"
#datadir = '/Users/nayman/Documents/REB/TS8/RTM8/RGhigh-longS1'
#tmjitterfile = "00_TS8_ITL_RGhigh_longS1_fix_bias_scan_tm.fits"
#datadir = '/Users/nayman/Documents/REB/TS8/RTM10/RGhigh'
#tmjitterfile = "00_scan_tm_TS8_ITL_RGhigh_longS1_fix.fits"
datadir = "/data/eotest/091/scan/scan-v0/20180220"
tmjitterfile = "tm_scan_10_CCD1_20180220102551.fz"

# returns tuple: (list of files, list of segments)
#l = raftstats.get_fits_raft(inputfile=tmjitterfile, datadir=datadir)

if True:
    #medianjitter = get_raft_jitter(l[0], l[1], datadir, RObaseline=slice(70, 85), ROjump=slice(90, 130))
    #medianjitter = get_raft_jitter(l[0], l[1], datadir, RObaseline=slice(60, 80), ROjump=slice(90, 100))
    #medianjitter = get_raft_jitter(l[0], l[1], datadir, RObaseline=slice(130, 150), ROjump=slice(160, 170))
    medianjitter = get_raft_jitter([tmjitterfile], "091", datadir, RObaseline=slice(80, 90), ROjump=slice(95, 120))

    print medianjitter

else:
    #medianjitter = [ 0.21927865,  0.28621586,  0.11381844,  0.10551608,  0.10325677,  0.1850758, 0.17761087,  0.14448285,  0.10784372]
    medianjitter = [0.18985758,  0.14373283,  0.16518399,  0.08404735,  0.10938918,  0.21957924,
  0.23564675,  0.16540295,  0.14028727]

#datadir = '/Users/nayman/Documents/REB/TS8/RTM8/'
datadir = '/Users/nayman/Documents/REB/TS8/RTM10/RTM10-scan-mode-images'
#tmpixelfile = "rtm8scanmodetm1/00_rtm8_tm_1_bias.fits"
#dsipixelfile = "rtm8scanmodedsi1/00_rtm8_dsi_1_bias.fits"
tmpixelfile = "00_TS8_ITL_clockcross90_bias_scan_tm.fits"
dsipixelfile = "00_TS8_ITL_clockcross90_bias_scan_dsi.fits"

#li = raftstats.get_fits_raft(inputfile=tmpixelfile, datadir=datadir)
#ldsi = raftstats.get_fits_raft(inputfile=dsipixelfile, datadir=datadir)

# extracting "slope" (difference of waveform levels) from TM
if False:
    get_raft_integration_bounds(li[0], li[1], medianjitter, datadir, RDstart=60, RDstop=92, RUstart=133, RUstop=165)

# extracting integrated levels from DSI
if False:
    get_raft_integration_total(ldsi[0], ldsi[1], datadir, RDstart=60, RDstop=92, RUstart=133, RUstop=165)
