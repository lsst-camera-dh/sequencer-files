import os
import raftstats
from matplotlib import pyplot as plt
import numpy as np

datadir = '/Users/nayman/Documents/REB/ATS/'
rtm = "RTM8"
run = "5577D"
#datadir = "/Users/nayman/Documents/REB/TS8/%s/run-%s" % (rtm, run)


l = sorted([os.path.join(datadir, f) for f in os.listdir(datadir) if os.path.splitext(f)[1] in [".fits", ".fz"]])
#l = raftstats.get_fits_raft(inputfile='', datadir=datadir)[0]

#bias2s = l[0]
#bias3s = l[3]

#raftstats.plothisto_overscan(l[0])

#raftstats.plot_corrcoef_raft([bias3s], ROIcols=slice(530,576),title="Bias with 3s sequencer")

#outfile = open(os.path.join(datadir, "recapstats.txt"))
#for f in l:
#    outfile.write("%s\n" % f)
#    outfile.write(raftstats.repr_stats(f, recalc=True))
#outfile.close()

for f in l:
    raftstats.average_1D_toplot(f, datadir, 0, slice(50,1950), slice(1,576), norm=True, title=os.path.split(f)[1])
