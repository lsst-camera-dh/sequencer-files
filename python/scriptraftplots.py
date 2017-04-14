import os
from raftstats import *

eodir = '/Users/nayman/Documents/REB/TS8/RTM1/3764/Fe55Bias'

l = [os.path.join(eodir, f) for f in os.listdir(eodir) if os.path.splitext(f)[1] in [".fits", ".fz"]]

#plothisto_overscan(l[0])
#a = corrcoef_raft(l)
plot_corrcoef_raft(l, ROIcols=slice(525, 575))
