# !/usr/bin/env python

# Displays a scope-like view of the CCD output waveform, matched with the clock states of the sequencer function
# used to acquire it.
#
# Changelog
# 20161205: C. Juramy, initialized from LPNHE bench code.
#
# Syntax as main:
# python scope.py [dsi-scan.fits] [tm-scan.fits] [sequencer-file.seq] [Channel] <[Main *or* function used for readout]>
# Example:
# python scope.py dsi-scan.fits tm-scan.fits seq-newflush.txt Segment00
# With LPNHE file formats:
# python scope.py dsi_scan_0x0020161027151605.fits tm_scan_0x0020161027151628.fits test-multiflush.txt chan_09
#
# Syntax in a script:
# import scope
# scope.combined_scope_display("dsi-scan.fits", "tm-scan.fits", "seq-newflush.txt", "Segment00", "Bias")

import sys
import pyfits
import numpy as np
from matplotlib import pyplot as plt

# add sequencer reading method
import rebtxt


def combined_scope_display(idsi, itm, seqfile, c, readout='ReadPixel'):
    """
    Display scan scope for a channel along with sequencer states.
    Sequencer file needs full path.
    Can be given the name of the main used (will detect automatically the function used and the offset of the ADC),
    or the name of the readout function. What is hardcoded here is the name of the ADC trigger ('TRG').
    Averages over all scan lines that are supposed to be within the detector physically.
    """

    # image extensions are labeled as 'Segment00' in CCS
    # they are in extensions 1 to 16
    # skip first ten lines and last 50 to stop before sensor edge
    dsiscope = pyfits.getdata(idsi, extname=c)[10:-50, :].mean(axis=0)
    tmscope = pyfits.getdata(itm, extname=c)[10:-50, :].mean(axis=0)

    # gets sequencer object
    seq = rebtxt.Sequencer.fromtxtfile(seqfile, verbose=False)

    # finds the function used for readout if given the Main
    if readout in seq.functions_desc:
        readfunction = readout
    else:
        readfunction = seq.find_function_withclock(readout, 'TRG')

    funcscope = seq.functions_desc[readfunction]['function']  # function to display
    clocklist = seq.functions_desc[readfunction]['clocks']  # names of active clocks

    fig, ax1 = plt.subplots(figsize=(13, 8))
    ax1.set_xlabel('Time increment (10 ns)')
    # ax1.set_xlim(0,255)
    ax1.set_xticks(np.arange(0, 256, 32))
    ax1.plot(dsiscope, label='DSI')
    ax1.plot(tmscope, label='TM')
    ax1.set_ylabel('Scan (ADU)')
    ax1.grid(axis='x')
    ax1.set_title(c)

    ax2 = ax1.twinx()
    ax2.grid(True)
    ax2.set_ylabel('Sequencer states')
    ax2.set_yticklabels(clocklist)

    # find offset between start of function and trigger of ADC
    clockline = seq.channels['TRG']
    offset = funcscope.scope(clockline).index(1)

    # creates waveform for each clock with matching timing
    for i, clock in enumerate(clocklist):
        clockline = seq.channels[clock]
        states = funcscope.scope(clockline)
        # repeats the clock waveform enough times and applies offset of ADC sampling
        scanstates = np.tile(np.array(states), 3)[offset:offset + 256]
        # plot one clock waveform per axis unit
        ax2.plot(scanstates * 0.8 + i, drawstyle='steps-post')

    plt.savefig("combinedscope.png")
    plt.show()



if __name__ == '__main__':
    idsi = sys.argv[1]
    itm = sys.argv[2]
    seqfile = sys.argv[3]
    c = sys.argv[4]
    if len(sys.argv) > 5:
        readout = sys.argv[5]
    else:
        readout = 'ReadPixel'

    combined_scope_display(idsi, itm, seqfile, c, readout)
