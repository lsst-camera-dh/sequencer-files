# eotest.py
from org.lsst.ccs.scripting import *
from REBlib import *
import numpy as np

# set this value to the number of photons per second you get
fluence = 2830.0 #e-/pix/second

# serial CTE sweep
Lo_Start = -9.00
Lo_End   = -6.00
Lo_Step  =  0.50
Range_Start = +9.00
Range_End   = +11.00
Range_Step  =  0.50
og_sup_Start = -2
og_sup_End   = 2.00
og_sup_Step  = 0.5

Par_Lo_Start = -9.5
Par_Lo_End = -8.0
Par_Lo_Step = 0.5
Par_Swing_Start=10
Par_Swing_End=11
Par_Swing_Step = 0.5


odometer = 1
imageCount = 1
etimes = [0,50000.0/float(fluence)]
setDefaults()

for Lo_Volts in np.arange(Lo_Start, Lo_End +0.1, Lo_Step):
    for Range in np.arange(Range_Start, Range_End +0.1, Range_Step):
        Hi_Volts = Lo_Volts+Range
        vsetSerLo('w',Lo_Volts)
        vsetSerLo('g',Lo_Volts)
        vsetSerHi('w',Hi_Volts)
        vsetSerHi('g',Hi_Volts)
        og_End = Hi_Volts+og_sup_End
        # loop on difference between serial up and og
        for og_sup in np.arange(og_sup_Start, og_sup_End +0.1, og_sup_Step) :
             og_Volts = Hi_Volts+og_sup
             if og_Volts >= 5 : continue
             vsetOG('w',og_Volts)
             vsetOG('g',og_Volts)
             Par_Lo_Volts = Par_Lo_Start
             for Par_Lo_Volts in np.arange(Par_Lo_Start, Par_Lo_End +0.1, Par_Lo_Step) :
                 # check that charges can flow into the serial register : 
                 if Par_Lo_Volts > Lo_Volts -0.9 : continue
                 vsetParLo('w', Par_Lo_Volts)
                 vsetParLo('g', Par_Lo_Volts)
                 for Par_Swing in np.arange(Par_Swing_Start, Par_Swing_End +0.1, Par_Swing_Step) :
                     Par_Hi = Par_Lo_Volts + Par_Swing
                     # check that charges can flow into the serial register : 
                     if Par_Hi > Hi_Volts -0.9 : continue
                     vsetDphi('w', Par_Swing)
                     vsetDphi('g', Par_Swing)
                     for c,exptime in enumerate(etimes):
                         for i in range(0, imageCount):
                             # 05.2f_%05.2f_%05.2f_%03i" % (Lo_Volts, Hi_Volts, og_Volts, i))
                             fbase = "scte_%04d_%1d"%(odometer,c)
                             odometer += 1
                             acquireExposure(exptime, fbase)
                             print fbase
setDefaults()
print "Serial CTE sweep complete."

