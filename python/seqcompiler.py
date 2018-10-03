#! /usr/bin/env python
# -*- Coding: utf-8 -*- 
#
# ========================================================================
# LSST
#
# REB Sequencer Compiler
#
# Compiler of the high-level LSST REB Sequencer Language
# (defined in LCA-XXXXX: "LSST REB Sequencer Language - User Manual")
#
# Authors: Laurent Le Guillou, Claire Juramy
#
# ========================================================================

import sys
import os.path
import datetime

import optparse

# from lsst.camera.generic.rebtxt import *
from rebtxt import *

# ========================================================================

version = '0.9.1'

# ========================================================================

outputs_base_addr = 0x100000
slices_base_addr  = 0x200000
program_base_addr = 0x300000

def write_compfile(seq, seqfile, compname=''):

    # creating output name
    if compname:
        compfile = compname
    else:  # default name
        compfile = os.path.basename(seqfile).replace(".seq", ".compiled").replace(".txt", ".compiled")
        if compfile == os.path.basename(seqfile):
            compfile = os.path.basename(seqfile) + ".compiled"

    compf = open(compfile, "w")

    # Small header to described the file

    print >> compf, "## LSST REB compiled sequencer file"
    print >> compf, "## REB: REB5"
    print >> compf, "## Source:", seqfile
    print >> compf, "## Compilation date:", datetime.datetime.utcnow()
    # print >> compf, "## Compiler:", "python seqcompiler", version
    print >> compf, "## Compiler:", "python seqcompiler", version
    print >> compf, "## Compiler authors:", "L. Le Guillou, C. Juramy"

    # Now writing the functions

    print >> compf, "## ======================================================"
    print >> compf, "# [functions]"
    print >> compf, "##"

    for func_id in xrange(len(seq.functions)):
        func = seq.functions[func_id]
        funcbc = func.bytecode(func_id,
                               slices_base_addr = slices_base_addr,
                               outputs_base_addr = outputs_base_addr)
        print >> compf, "## ------------------------------------------------------"
        print >> compf, "## function: #%d" % func_id
        print >> compf, "##   name: ", func.name
        print >> compf, "##   description: ", func.fullname
        print >> compf, "##   execution time: ", func.total_time()
        print >> compf, "##"

        addrs = funcbc.keys()
        addrs.sort()
        for addr in addrs:
            print >> compf, "0x%06x: 0x%08x" % (addr, funcbc[addr])

    # Now writing the subroutines and mains

    print >> compf, "## ======================================================"
    print >> compf, "# [subroutines/mains]"
    print >> compf, "##"

    print >> compf, "## ------------------------------------------------------"

    print >> compf, "## Main/Subroutine relative addresses"
    print >> compf, "## (program base addr 0x300000)"
    print >> compf, "## "
    for name, reladdr in seq.program.subroutines.iteritems():
        print >> compf, "# %s: 0x%06x" % (name, reladdr)

    print >> compf, "## ------------------------------------------------------"

    progbc = seq.program.bytecode(program_base_addr = program_base_addr)
    addrs = progbc.keys()
    addrs.sort()
    for addr in addrs:
        print >> compf, "0x%06x: 0x%08x" % (addr, progbc[addr])

    # Now writing the pointers

    print >> compf, "## ======================================================"
    print >> compf, "# [pointers]"
    print >> compf, "##"

    ptrs = seq.pointers

    for name, ptr in ptrs.iteritems():
        print >> compf, "0x%06x: 0x%06x   # %s:  %s" % (ptr.address,
                                                        ptr.value,
                                                        ptr.pointer_type,
                                                        ptr.name)

    print >> compf, "## ======================================================"

    compf.close()

    return compfile

# ========================================================================
if __name__ == '__main__':
    parser = optparse.OptionParser(usage = \
    """
    %prog [-v] <sequencer-file> [<compiled-file>]

    Sequencer compiler for the LSST REB FPGA.

    This program takes a sequencer program (in *.seq format)
    as its argument, compiles it, and return a compiled
    version (address/value list) of the same program, ready
    to be written in the REB FPGA program memory.

    The LSST REB sequencer programming language is specified
    in LCA-XXXXX: 'LSST REB Sequencer Language - Use Manual'.
    """)
    parser.add_option('-v', '--verbose', default=True, action='store_true',
                      help='Verbose run')

    (options, args) = parser.parse_args()

    # print options
    # print "args = ", args

    if len(args) < 1:
        # no seqfile provided
        print >>sys.stderr, "error: no sequencer program file."
        parser.print_help()
        sys.exit(1)

    seqfile = args[0]


    if len(args) >= 2:
        compfile = args[1]
    else:
        compfile = ''

    # ========================================================================

    try:
        seq = Sequencer.fromtxtfile(seqfile)  # compilation proper
    except:
        print >>sys.stderr, 'error: compilation of file "%s" failed: no output.' % seqfile
        sys.exit(2)

    # Now, writing the various parts into the resulting file
    write_compfile(seq, seqfile, compname=compfile)

