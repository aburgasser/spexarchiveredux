# Basic visual check and analysis of SpeX SXD data

import glob
import os
import pandas
import sys
import splat
import numpy
import matplotlib.pyplot as plt
from astropy.io import fits
import astropy.units as u

basefolder = '/Volumes/splat/data/spex/'


def readsxd(file,output='',name='',**kwargs):
    funit = u.erg/u.s/u.cm/u.cm/u.Angstrom
    wunit = u.micron
    xrngs = [[1.95,2.47],[1.43,1.81],[1.1,1.5],[0.92,1.2],[0.83,1.02],[0.735,0.93],[0.7,0.8]]
    with fits.open(file, **kwargs) as hdulist:
        header = hdulist[0].header
        meta = {'header': header}
        data = hdulist[0].data
    spec = []
    orders = header['ORDERS'].split(',')
    for i in range(len(data[:,0,0])):
        sp = splat.Spectrum(wave=data[i,0,:]*wunit,flux=data[i,1,:]*funit,noise=data[i,2,:]*funit,header=header,instrument='SPEX-SXD',name='{} order {}'.format(name,orders[i]))
        sp.trim(xrngs[i])
        spec.append(sp)
        
    if output=='multispec': return spec
    elif output=='1dspec':
        spc = spec[0]
        for s in spec[1:]: spc = splat.stitch(spc,s,scale=False)
        spc.name=name
        return spc
        
    else: return spec

def plotmultispec(sparr,output='',ncol=2):
    nrow = numpy.ceil(len(sparr)/ncol)
    plt.figure(figsize=[ncol*6,nrow*4])
    sparr.reverse()
    for i,sp in enumerate(sparr):
        plt.subplot(nrow,ncol,i+1)
        plt.plot(sp.wave.value,sp.flux.value,'k-')
        plt.legend([sp.name],fontsize=14)
        plt.plot(sp.wave.value,sp.noise.value,'k-',alpha=0.3)
        plt.ylim([0,numpy.nanquantile(sp.flux.value,0.95)*1.2])
        plt.xlabel('Wavelength ($\mu$m)',fontsize=14)
        plt.ylabel('F$_{\lambda}$'+' ({})'.format(sp.flux.unit),fontsize=14)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
    sparr.reverse()
    if output!='':
        plt.tight_layout()
        try:
            plt.savefig(output)
        except:
            print('Could not save to {}'.format(output))
    return


def process(date,smth=50):
	folder = basefolder+'/{}/'.format(date)
	if os.path.isdir(folder) == False: raise ValueError('Cannot find folder {}'.format(folder))

# plot individual SXD orders
	files = glob.glob(folder+'/proc/spex-sxd_*{}.fits'.format(date))
	if len(files) == 0: print('Cannot find any spex-sxd*.fits data files in {}'.format(folder+'/proc/'))
	else:
		names = [f.split('_')[-2] for f in files]
		for i in range(len(files)): 
		    sps = readsxd(files[i],name=names[i])
		    plotmultispec(sps,output=folder+'/proc/plot_orders_{}_{}_sxd.pdf'.format(names[i],date))

# classify merged SXD files
	mfiles = glob.glob(folder+'/proc/spex-sxd-merged_*{}.fits'.format(date))
	if len(mfiles) == 0: print('Cannot find any spex-sxd-merged*.fits data files in {}'.format(folder+'/proc/'))
	else:
		names = [f.split('_')[-2] for f in mfiles]
		for i,m in enumerate(mfiles): 
		    sp = splat.Spectrum(file=m,instrument='SPEX-SXD',name=names[i])
		    sp.smooth(smth)
		    sp.trim([0.7,2.45])
		    splat.classifyByStandard(sp,plot=True,method='kirkpatrick',telluric=True,output=folder+'/proc/plot_classify_{}_{}_sxd.pdf'.format(names[i],date))

# classify prism files
	mfiles = glob.glob(folder+'/proc/spex-prism_*{}.fits'.format(date))
	if len(mfiles) == 0: print('Cannot find any spex-prism*.fits data files in {}'.format(folder+'/proc/'))
	else:
		names = [f.split('_')[-2] for f in mfiles]
		for i,m in enumerate(mfiles): 
		    sp = splat.Spectrum(file=m,instrument='SPEX-PRISM',name=names[i])
		    splat.classifyByStandard(sp,plot=True,method='kirkpatrick',telluric=True,output=folder+'/proc/plot_classify_{}_{}_prism.pdf'.format(names[i],date))

	return

# external function call
if __name__ == '__main__':
	if len(sys.argv) > 1: 
		process(sys.argv[1])


