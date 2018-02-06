import os
import raftstats
import scope
from matplotlib import pyplot as plt
import numpy as np

datadir = '/Users/nayman/Documents/REB/TS8/'
#datadir = '/Users/nayman/Documents/REB/TS8/RTM2/4876D'
#datadir = '/Users/nayman/Documents/REB/TS8/RTM2/4875D/28475'
#datadir = '/Users/nayman/Documents/REB/TS8/RTM1/RefitRuns/run-5190D'
#datadir = '/Users/nayman/Documents/REB/TS8/RTM8/singleclockscans/allRG'

#l = sorted([os.path.join(datadir, f) for f in os.listdir(datadir) if os.path.splitext(f)[1] in [".fits", ".fz"]])
#ccd154 = 'E2V-CCD250-154-Dev_fe55_bias_000_4876D_20170427035453.fits'
#ccd252 = 'E2V-CCD250-252-Dev_fe55_bias_000_4876D_20170427035453.fits'
#l = [os.path.join(datadir, f) for f in [ccd154, ccd252]]

#l = raftstats.get_fits_raft(inputfile='00_TS8_ITL_P_allRG_3.fits', datadir=datadir)

#plothisto_overscan(l[0])

#raftstats.plot_corrcoef_raft(l[0], ROIrows=slice(190, 1990), ROIcols=slice(522, 576), xylabels=l[1], title='RG all high')

#write_header_stats(l, ROIrows=slice(700,1400))

#lscans = []

#for root, dirs, files in os.walk(datadir):
#    for f in files:
#        if f[-4:] == 'fits' and os.stat(os.path.join(root, f)).st_size > 1e5 and "00" in f and "scan" in f and 'tm' in f:
#            lscans.append(os.path.join(root, f))

lscans = [
'/Users/nayman/Documents/REB/TS8/ETU1/IR2/2017-06-21/00_test_tm_20170621204509.fits',
'/Users/nayman/Documents/REB/TS8/RTM8/rtm8scanmodetm1/00_rtm8_tm_1_bias.fits',
'/Users/nayman/Documents/REB/TS8/RTM1/rmBufferS1S3/00_RTM1noise_rmBufferS1S3_2_tm.fits',
'/Users/nayman/Documents/REB/TS8/RTM2/rtm-scan-mode-data/rtm2-scan-tm-bias/00-rtm2-scan-tm-bias_2.fits',
'/Users/nayman/Documents/REB/TS8/RTM10/RTM10-scan-mode-images/00_TS8_ITL_clockcross90_bias_scan_dsi_2.fits',
]
#'/Users/nayman/Documents/REB/TS8/RTM9/rtm9scans1/00_seq-e2v-injectRD_scan_tm_2.fits',


lnames = [p[len(datadir):].split('/')[0] for p in lscans]
allstd = []

fig, ax = plt.subplots(figsize=(12, 7))

if len(allstd) == 0:
    for num, tmbasefile in enumerate(lscans):
        l = raftstats.get_fits_raft(tmbasefile)
        print l[0][-1]
        a = raftstats.roistats_raft(l[0], ROIrows=slice(100, 1000), ROIcols=slice(89, 90))
        allstd.append(a[1])
        ax.plot(a[1], label=lnames[num])
else:
    for num, a in enumerate(allstd):
        ax.plot(a, label=lnames[num])

ax.legend(bbox_to_anchor=(1.07, 0), loc='lower left', borderaxespad=0.)
ax.set_title('Standard deviation of baseline in Transparent Mode')
ax.set_xticks(np.arange(0, 144, 16))
ax.set_xticklabels(["S%d%d" % (i, j) for i in range(3) for j in range(3)])
ax.set_xlim(0, 144)
ax.grid()

plt.savefig(os.path.join(datadir, "statstm-allscans.png"))
plt.show()

