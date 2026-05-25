'''
    Load SIMBA temperature and heating rates
    Process the data and save as pickle files
''' 

import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl
mpl.interactive(True)
import cmocean
import pandas as pd
import glob
import os
import pickle
from matplotlib.colors import BoundaryNorm, ListedColormap
import xarray as xr
import sys
sys.path.append(os.path.abspath('../../'))
from functions import IMS_toolbox as IMS
from scipy.interpolate import UnivariateSpline

# Some globals
fontsize = 14
year = '2026'
pathroot = os.path.abspath('../../')
dt = {'2024': 1, '2025': 1, '2026': 6} # sample rate in hours
time_offset = {'2024': np.timedelta64(0, 'h'), '2025': np.timedelta64(0, 'h'), '2026': np.timedelta64(94368, 'h')} # Offset in time index, only needed for 2026 data which was offset for some reason

# Position of ice surface along SIMBA thermistor string
# 2024: node 89 is the ice surface. It gave a z of 176, hence the offset 
# 2025: node 75 is the ice surface. It gave a z of 150, hence the offset 
# 2026: node 94 is the ice surface. 2x94 = 186
z_offset = {'2024': 176, '2025': 150, '2026': 186}

# Delta data from heating phases
da_temp = IMS.SIMBA_to_da(pathroot + '/data/' + year + '/SIMBA/TEMPDATA*') # all temp data manually stored in one filed
da_del0 = IMS.SIMBA_to_da(pathroot + '/data/' + year + '/SIMBA/DELDATA0*') # Temperature at t=0s
da_del1 = IMS.SIMBA_to_da(pathroot + '/data/' + year + '/SIMBA/DELDATA1*') # Temperature change at t=30s
da_del4 = IMS.SIMBA_to_da(pathroot + '/data/' + year + '/SIMBA/DELDATA4*') # Temperature change at t=120s (90s after da_del1)

# Fix any time offset (e.g. 2026 data)
da_temp['time'] = da_temp['time'] + time_offset[year]
da_del0['time'] = da_del0['time'] + time_offset[year]
da_del1['time'] = da_del1['time'] + time_offset[year]
da_del4['time'] = da_del4['time'] + time_offset[year]

# Cut out the bottom 5 nodes - weird data
da_temp = da_temp.sel(node=slice(0,236))
da_del0 = da_del0.sel(node=slice(0,236))
da_del1 = da_del1.sel(node=slice(0,236))
da_del4 = da_del4.sel(node=slice(0,236))

#time_temp = da_temp.time.values
#hours_temp = np.arange(len(time_temp))*dt[year]

#time_del = da_del0.time.values
#hours_del = np.arange(len(da_del0))*dt[year]

# Vertical coordinate array
node_spacing = 2 # Each node is spaced 2cm apart
z = (-np.arange(len(da_temp.node))*node_spacing + z_offset[year])/100 # depth in m

#
# Clean out articial gradient procuded by calibration offsets
#

# Clark's method:
# Only select a chunk where the ice interface is not changing much
T_meas = da_temp.sel(time=slice(year+'-03-25',year+'-04-10')).mean('time')
cs = UnivariateSpline(T_meas.node,T_meas,s=1)
x_smooth = np.linspace(0, len(T_meas) - 1, len(T_meas))
T_spl = cs(x_smooth) # <T>

# Plot to check (diagnostic)
plt.figure()
plt.plot(T_meas.node,T_meas)
plt.plot(x_smooth,T_spl)

# Terr = <Tmeas> - <T>, assuming it's constant in time
T_err = T_meas - T_spl

# Now subtract the error from the all sensors
da_temp_smooth = da_temp - T_err

# Vizualize the results
vmin=-2
vmax=0
fig,axx = plt.subplots(figsize=(10,8),nrows=2,ncols=1,sharex=True)
im1 = axx[0].pcolormesh(da_temp.time, z, da_temp.T, vmin=vmin,vmax=vmax, cmap=plt.cm.turbo)
axx[0].set_title('Original data')
im3 = axx[1].pcolormesh(da_temp.time, z, da_temp_smooth.T,vmin=vmin,vmax=vmax, cmap=plt.cm.turbo)
axx[1].set_title('Smoothing via smoothing spline')
# hacky lol
plt.colorbar(im1,ax=axx[0])
plt.colorbar(im1,ax=axx[1])

# plt.savefig(pathroot + '/figures/' + year + '/SIMBA/Smoothed_Temps.png', dpi=600, bbox_inches='tight')

#
# Change the node dimension to z in all SIMBA data arrays
#

da_temp_z = da_temp_smooth # copy
da_temp_z['node'] = z
da_temp_z = da_temp_z.rename({"node":"z"})

da_del0_z = da_del0 # copy
da_del0_z['node'] = z
da_del0_z = da_del0_z.rename({"node":"z"})

da_del1_z = da_del1 # copy
da_del1_z['node'] = z
da_del1_z = da_del1_z.rename({"node":"z"})

da_del4_z = da_del4 # copy
da_del4_z['node'] = z
da_del4_z = da_del4_z.rename({"node":"z"})

#
# Make into Datasets
#

simba_temp = da_temp_z.to_dataset(name='temp')
simba_del = xr.merge([da_del0_z.to_dataset(name='del0'), da_del1_z.to_dataset(name='del1'), da_del4_z.to_dataset(name='del4')])

#
# Save as a pickle files
#

#with open(pathroot + '/data/' + year + '/SIMBA/da_temp_z.pickle','wb') as f:
#    pickle.dump(da_temp_z, f)
#
#with open(pathroot + '/data/' + year + '/SIMBA/da_del0_z.pickle','wb') as f:
#    pickle.dump(da_del0_z, f)
#
#with open(pathroot + '/data/' + year + '/SIMBA/da_del1_z.pickle','wb') as f:
#    pickle.dump(da_del1_z, f)
#
#with open(pathroot + '/data/' + year + '/SIMBA/da_del4_z.pickle','wb') as f:
#    pickle.dump(da_del4_z, f)

#
# Save as NetCDF
#

nc = simba_temp.to_netcdf(pathroot + '/data/' + year + '/SIMBA/SIMBA_temp.nc') # Save to netCDF file
nc = simba_del.to_netcdf(pathroot + '/data/' + year + '/SIMBA/SIMBA_del.nc') # Save to netCDF file

