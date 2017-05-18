import os
from raftstats import *

#datadir = '/Users/nayman/Documents/REB/TS8/RTM1/3764/Fe55Bias'
#datadir = '/Users/nayman/Documents/REB/TS8/RTM2/4876D'
datadir = '/Users/nayman/Documents/REB/TS8/RTM2/4875D/28475'

l = sorted([os.path.join(datadir, f) for f in os.listdir(datadir) if os.path.splitext(f)[1] in [".fits", ".fz"]])
#ccd154 = 'E2V-CCD250-154-Dev_fe55_bias_000_4876D_20170427035453.fits'
#ccd252 = 'E2V-CCD250-252-Dev_fe55_bias_000_4876D_20170427035453.fits'
#l = [os.path.join(datadir, f) for f in [ccd154, ccd252]]

#plothisto_overscan(l[0])
#a = corrcoef_raft(l)
#plot_corrcoef_raft(l, ROIcols=slice(525, 575))

#a = timecorr_raft(l, ROIrows=slice(12,14))
plot_timecorr_raft(l, ROIrows=slice(100, 1100), ROIcols=slice(20, 500))