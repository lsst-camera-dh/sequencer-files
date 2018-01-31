# !/usr/bin/env python

# Prints out a breakdown of a sequence as defined in a TXT sequender file.
#
# Changelog
# 20161206: C. Juramy, initialized from LPNHE bench code.
#
# Syntax as main:
# python timing.py [sequencer-file.seq] [Main or Subroutine]
# Example:
# python timing.py seq-newflush.txt Acquisition
#
# Syntax in a script:
# import timing
# timing.breakout("seq-newflush.txt", "Acquisition")

import sys

# add sequencer reading method
import rebtxt


def breakout(seqfile, exptype):
    """
    :param seqfile:
    :param exptype:
    :return:
    """
    seq = rebtxt.Sequencer.fromtxtfile(seqfile, verbose=False)

    if exptype in seq.program.subroutines:
        reprseq = seq.sequence(exptype, verbose=False)

        for l in reprseq:
            print l

    elif exptype in seq.functions_desc:
        f = seq.get_function(exptype)
        print f
        print "Total time: %d ns" % (f.total_time() * 10)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("timing.py requires sequencer file and main/subroutine/function name")
        sys.exit()
    seqfile = sys.argv[1]
    exptype = sys.argv[2]

    breakout(seqfile, exptype)
