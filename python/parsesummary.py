# !/usr/bin/env python

# usage in command line:
# python parsesummary.py /Users/nayman/Documents/REB/TS8/ITL-sensors
# python parsesummary.py /Users/nayman/Documents/REB/TS8/ITL-sensors/recap-confluence.txt


import os
import sys

def half_median(table):
    """
    Outputs the medians of the two halves of a 16-element table, in string format.
    :return:
    """

    stable = sorted(table[:8])
    retstr = "%.2f" % ((stable[3] + stable[4]) * 0.5)
    stable = sorted(table[8:])
    retstr += "\t%.2f" % ((stable[3] + stable[4]) * 0.5)

    return retstr


def parse_summary(summaryfile, selectitem, Nfits=1):
    """
    Parses summary files produced by eTraveler jobs, outputs selected
    statistics for N fits files (1 > single sensor, 9 > raft).
    :param summaryfile:
    :param selectitem: 0: AVG, 1: AVGBIAS, 2: STDBIAS
    :param Nfits:
    :return:
    """
    f = open(summaryfile, 'r')
    table = []
    for l in f.readlines():
        if len(table) >= Nfits * 16:
            break
        if l.lstrip()[:7] != "Segment":
            continue
        numstr = l.split("=")[selectitem + 1].split('|')[0]
        table.append(float(numstr))
    f.close()

    return table

def parse_summary_dump(dumpfile, selectitem):
    """
    When all summaries have already been collected into a single file.
    :param dumpfile:
    :param selectitem:
    :param Nfits:
    :return:
    """
    f = open(dumpfile, 'r')
    outf = open(dumpfile[:-4] + "_max.txt", 'w')

    table = []
    for l in f.readlines():
        if l.lstrip()[:7] != "Segment":
            try:
                ccd = int(l)
            except:
                continue
            if table:
                stable = sorted(table)
                outf.write("%.2f\t%s\n" % (max(table[:7] + table[9:]), half_median(table)))  # writes out previous sensor
            outf.write("%s\t" % ccd)
            table = []  # empty table
            continue

        numstr = l.split("=")[selectitem + 1].split('|')[0]
        table.append(float(numstr))

    outf.write("%.2f\t%s\n" % (max(table[:7] + table[9:]), half_median(table)))  # last sensor
    f.close()
    outf.close()


def parse_all_directory(datadir, Nfits=1):
    """
    Parses all summary files in directory and finds maximum/median/etc. outputs to file.
    :param datadir:
    :param Nfits:
    :return:
    """
    outf = open(os.path.join(datadir, "allsummary.txt"), 'w')

    for f in sorted(os.listdir(datadir)):
        if f[:7] != "summary":
            continue

        print("Opening %s" % f)
        table = parse_summary(os.path.join(datadir, f), 1, Nfits)
        outf.write("%s\t %.2f\t%s\n" % (f[8:11], max(table[:7] + table[9:]), half_median(table)))

    outf.close()

if __name__ == '__main__':
    inputdata = sys.argv[1]
    if os.path.isdir(inputdata):
        parse_all_directory(inputdata)
    else:
        parse_summary_dump(inputdata, 1)
