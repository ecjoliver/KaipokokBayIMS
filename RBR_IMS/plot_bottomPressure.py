'''
    Adjust ocean pressure data with atmospheric pressure from weather station

    RBR uses a constant atmospheric pressure and density to derive the depth channel: 
    https://docs.rbr-global.com/display/L3DOCpublicVE/Example+9%3A+depth+-+derivation+of+depth+from+pressure
    https://rbr-global.com/wp-content/uploads/2017/04/0001963revB-Logger2-Command-Reference.pdf

'''


from pyrsktools import RSK as RSK
import numpy as np
import matplotlib.pyplot as plt
import cmocean
import matplotlib as mpl
mpl.interactive(True)
import xarray as xr
import sys
import os
sys.path.append(os.path.abspath('../../'))
from functions import IMS_toolbox as IMS
import gsw 
import matplotlib.ticker as tkr
import pandas as pd 
import pickle

#
# Some globals
#

exec(open('../globals.py').read())

#
# Load in data
#

# Bottom CTD data (z=55.0)
ds_S = xr.open_dataset(pathroot + '/data/' + year + '/RBR_IMS/RBR_salinity_density.nc')

# Weather data
ds_W = xr.open_dataset(pathroot + '/data/' + year + '/WeatherStation/WeatherVars_SD.nc') # SD card data
resampled_data_vars = {var: ds_W[var].resample(time='1H').mean() for var in ds_W.data_vars}
ds_W = xr.Dataset(resampled_data_vars) # make xr dataset from resampled data

#
# Pull out pressure and convert
#

# Extract atmospheric pressure and convert mbar to dbar
p_atm = ds_W['BP_mbar_Avg']*0.01

# Merge Bottom CTD and Atmospheric pressure data to same array
ds = xr.merge([ds_S.sel(z=55.0), p_atm], join="outer")
ds = ds.rename({'BP_mbar_Avg': 'p_atm'})

#
# Time series plots
#

# Time series of bottom pressure
fig,axx = plt.subplots(nrows=3,ncols=1,figsize=(11,8),sharex=True, facecolor='w')
lw = 1.5
axx[0].plot(ds.time, ds.p, 'k-', linewidth=lw, label=r'Bottom pressure, $p$')
axx[0].set_ylabel(r'Pressure (dbar)')
axx[0].legend(loc='lower left')
axx[1].plot(ds.time, ds.p_atm, 'k-', linewidth=lw, label=r'Surface air pressure, $p_\mathrm{a}$')
axx[1].set_ylabel(r'Pressure (dbar)')
axx[1].legend(loc='lower left')
axx[2].plot(ds.time, ds.p- ds.p_atm, 'k-', linewidth=lw, label=r'Bottom sea pressure, $p-p_\mathrm{a}$')
axx[2].set_ylabel(r'Pressure (dbar)')
axx[2].legend(loc='lower left')
#
plt.xlim([ds_S.time[0], ds_S.time[-1]])
plt.tight_layout()

# plt.savefig(pathroot + '/figures/' + year + '/RBR_IMS/RBR_Timeseries_BottomPressureCorrected.png', dpi=600, bbox_inches='tight')

