# Script to compress fits files while keeping header information
import os, sys
import astropy.io.fits as pyfits
#eodir = '/Users/nayman/Documents/REB/REB4/BNLtest/ITL/20161116'
#eodir = '/sps/lsst/DataBE/REB4/BNL/ITL/20161117'

def walk_compress(eodir):
    #for f in os.listdir(eodir):
    for root, dirs, files in os.walk(eodir):
        for f in files:
            if f[-4:] != 'fits' or os.stat(os.path.join(root, f)).st_size < 1e6:
                continue
            print("Compressing %s" % f)
            h = pyfits.open(os.path.join(root, f))
            hdulist = pyfits.HDUList([pyfits.PrimaryHDU(header=h[0].header)])
            #hdulist[0].header['WIDTH'] = 576
            #hdulist[0].header['HEIGHT'] = 2048
            #hdulist[0].header["FILENAME"] = f
            # extension header
            for i in range(16):
                #h[i + 1].header['DATASEC'] = "[4:512, 1:2000]"
                #h[i + 1].header['CHANNEL'] = i
                exthdu = pyfits.CompImageHDU(data=h[i + 1].data, header=h[i + 1].header.copy(),
                                                   compression_type='RICE_1')
                hdulist.append(exthdu)

            # auxiliary data
            for i in range(17, 30, 1):
                try:
                    hdulist.append(h[i])
                except:
                    pass

            hdulist.writeto(os.path.join(root, f), clobber=True)

            h.close()
            del h


if __name__=='__main__':
    walk_compress(sys.argv[1])


#for root, dirs, files in os.walk('python/Lib/email'):
#    print root, "consumes",
#    print sum(getsize(join(root, name)) for name in files),
#    print "bytes in", len(files), "non-directory files"