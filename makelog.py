# Log maker for SpeX data

import glob
import os
import pandas
import sys
from astropy.io import fits

col_top = ['PROG_ID','OBSERVER','DATE_OBS']
cols_new = {
    'Source Name': 'TCS_OBJ',
    'RA': 'TCS_RA',
    'Dec': 'TCS_DEC',
    'UT Time': 'TIME_OBS',
    'MJD': 'MJD_OBS',
    'HA': 'TCS_HA',
    'PA': 'POSANGLE',
    'Parallactic': 'TCS_PA',
    'Airmass': 'TCS_AM',
    'Integration': 'ITIME',
    'Coadds': 'CO_ADDS',
    'Type': 'DATATYPE',
    'Slit': 'SLIT',
    'Mode': 'GRAT',
    'Program': 'PROG_ID',
    'Observer': 'OBSERVER',
}

cols_old = {
    'Source Name': 'OBJECT',
    'RA': 'RA',
    'Dec': 'DEC',
    'UT Time': 'TIME_OBS',
    'HA': 'HA',
    'PA': 'POSANGLE',
    'Airmass': 'AIRMASS',
    'Integration': 'ITIME',
    'Coadds': 'CO_ADDS',
    'Slit': 'SLIT',
    'Mode': 'GRAT',
    'Observer': 'OBSERVER',
}

basefolder = '/Volumes/splat/data/spex/'

def makelog(date):
	folder = basefolder+'/{}/'.format(date)
	if os.path.isdir(folder) == False: raise ValueError('Cannot find folder {}'.format(folder))
	files = glob.glob(folder+'/data/*.fits')
	if len(files) == 0: raise ValueError('Cannot find any .fits data files in {}'.format(folder+'/data/'))

	dp = pandas.DataFrame()
	dp['File'] = [f.split('/')[-1] for f in files]
#	dp['File number'] = [int(f.split('.')[-3]) for f in files]

# select which columns to use
	hdu = fits.open(files[0])
	h = hdu[0].header
	hdu.close()
	if 'TCS_OBJ' in list(h.keys()): cols = cols_new
	else: cols = cols_old

# make log	
	for c in list(cols.keys()): dp[c] = ['']*len(files)
	dp['Note'] = ['']*len(files)
	for i,f in enumerate(files):
	    hdu = fits.open(f)
	    hdu.verify('silentfix')
	    h = hdu[0].header
	    hdu.close()
	    for c in list(cols.keys()): dp.loc[i,c] = h[cols[c]]
	    if 'arc' in f: dp.loc[i,'Source Name'] = 'arclamp'
	    if 'flat' in f: dp.loc[i,'Source Name'] = 'flat field'
	dp.sort_values('UT Time',inplace=True)
	dp.reset_index(inplace=True,drop=True)
	dp.to_excel(folder+'logs_{}.xlsx'.format(date),index=False)	
	print('log written to {}'.format(folder+'logs_{}.xlsx'.format(date)))

	return

# external function call
if __name__ == '__main__':
	if len(sys.argv) > 1: 
		makelog(sys.argv[1])
