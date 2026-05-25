'''
    Plot SIMBA temperatures, heating rates and gradients.
'''

import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl
mpl.interactive(True)
import cmocean
import pandas as pd
import glob
import os
# import warnings; warnings.simplefilter('ignore')
from matplotlib.colors import BoundaryNorm, ListedColormap
import xarray as xr
import pickle
import gsw
import matplotlib.ticker as tkr
#plt.ion()

# Some globals
year = '2026'
pathroot = os.path.abspath('../../')

fontsize=12

# Load temperature data
ds = xr.open_dataset(pathroot + '/data/' + year + '/SIMBA/SIMBA_temp.nc')

# Alternate method using pickle'd data
#with open(pathroot + '/data/' + year + '/SIMBA/ds.temp_z.pickle','rb') as f:
#    ds.temp = pickle.load(f)
#
#z = ds.temp.z
#time_temp = ds.temp.time

#
# Plot single profile
#

tt = 15 # time index to plot, early in season so it's "winter conditions"

plt.figure(figsize=(5,10),facecolor='white')
ax = plt.subplot(111)
ax.plot(ds.temp[tt,:].T, ds.z,'.-') 
plt.xticks(size=fontsize)
plt.yticks(size=fontsize)
plt.ylabel('z [cm]',fontsize=fontsize)
plt.xlabel('T [deg. C]', fontsize=fontsize)
plt.grid()

#
# Plot the vertical profile at each timestep 
#

plt.figure(figsize=(8,10),facecolor='white')
ax = plt.subplot(111)
cm = plt.cm.bwr(np.linspace(0, 1, len(ds.time))) # create colormap for time
ax.set_prop_cycle('color', list(cm)) # color each line in sequential order
ax.plot(ds.temp.T, ds.z) 
plt.ylabel('z [m]',fontsize=fontsize)
plt.xlabel('T [deg. C]', fontsize=fontsize)
plt.ylim(-2, 2)
plt.grid()
ax.tick_params(axis='both',labelsize=fontsize)
# create a ListedColormap and BoundaryNorm
cmap = ListedColormap(cm)
bounds = np.linspace(0, 1, len(ds.time) + 1)
norm = BoundaryNorm(bounds, cmap.N)
# Add a discrete colorbar for the entire figure
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, boundaries=bounds, ticks=0.5*(bounds[1:] + bounds[:-1]), ax=ax)
cbar.set_label('Time', fontsize=fontsize)
# Change the tick labels on the colorbar - month day
new_tick_labels = [pd.to_datetime(str(t)).strftime('%m-%d') for t in ds.time.values]
cbar.set_ticklabels(new_tick_labels)
n = 24  # Keep every nth label
[l.set_visible(False) for (i,l) in enumerate(cbar.ax.yaxis.get_ticklabels()) if i % n != 0]
cbar.ax.tick_params(labelsize=fontsize-4)

# plt.savefig(pathroot + '/figures/' + year + '/SIMBA/SIMBA_temp_profiles.png', dpi=600, bbox_inches='tight')

#
# Contour plot of temperatures and depth over time
#

plt.figure(figsize=(18,8),facecolor='white')
ax = plt.subplot(111)
# im = plt.contourf(hours_temp, z, ds.temp.T, cmap=cmocean.cm.thermal)#,levels=[-10,-5,-2,-1.8,-1.6,-1.4,-1.2,-1,-0.8,-0.6,-0.4,-0.2,0])
im = plt.pcolormesh(ds.time, ds.z, ds.temp.T, cmap=plt.cm.turbo) #cmocean.cm.thermal)

plt.clim(-10, 0) # colorbar limits
plt.ylim(-3, 1.8)
cbar = plt.colorbar(pad=0.02)
cbar.set_label(label='T [deg. C]', size=fontsize)
cbar.ax.tick_params(labelsize=fontsize)

plt.ylabel('z [m]',fontsize=fontsize)
plt.xlabel('Time',fontsize=fontsize)
ax.tick_params(axis='both',labelsize=fontsize)

# plt.savefig(pathroot + '/figures/' + year + '/SIMBA/SIMBA_temp_heatmap.png', dpi=600, bbox_inches='tight')

#
# Profiles by month (average daily temperatures)
#

# Average to daily temps
ds_daily = ds.resample(time='1D').mean()
fig,axx = plt.subplots(nrows=1,ncols=3,figsize=(10,8),sharey=True, facecolor='w')
cm = plt.cm.bwr(np.linspace(0, 1, 10))

axx[0].set_prop_cycle('color', list(cm)) # color each line in sequential order
axx[1].set_prop_cycle('color', list(cm)) # color each line in sequential order
axx[2].set_prop_cycle('color', list(cm)) # color each line in sequential order

axx[0].plot(ds_daily.temp.sel(time=year+'-02').T, ds_daily.z)
axx[0].set_title('February')
axx[0].set_ylabel('z [m]')

axx[1].plot(ds_daily.temp.sel(time=year+'-03').T, ds_daily.z)
axx[1].set_title('March')
axx[1].set_xlabel('T [deg. C]')

axx[2].plot(ds_daily.temp.sel(time=year+'-04').T, ds_daily.z)
axx[2].set_title('April')

plt.ylim([-3,1.5])

# create a ListedColormap and BoundaryNorm
cmap = ListedColormap(cm)
bounds = np.linspace(0, 1, 10+ 1)
norm = BoundaryNorm(bounds, cmap.N)

# Add a discrete colorbar for the entire figure
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar_ax = fig.add_axes([0.94, 0.12, 0.02, 0.75])  # Adjust these values as needed
cbar = plt.colorbar(sm, cax=cbar_ax,boundaries=bounds, ticks=0.5*(bounds[1:] + bounds[:-1]))
cbar.set_label('Time', fontsize=fontsize)
cbar.set_ticklabels([])

# plt.savefig(pathroot + '/figures/' + year + '/SIMBA/SIMBA_temp_bymonth.png', dpi=600, bbox_inches='tight')

#
# Subset depths on subplots with different colorbar limits
#

w=25
plt.figure(num=1, figsize=(12,10))
cmap = 'turbo'
t = ds.time.values
# Snow-air
ax = plt.subplot2grid((4,w), (0,0), rowspan=1, colspan=w-1)
plt.pcolormesh(ds.time, ds.z, ds.temp.T, cmap=cmap)
plt.clim(-12, 2)
plt.ylim(0, 1)
plt.ylabel('z [m]')
ax.set_xticklabels([])
ax.set_title('0 m to +1 m',y=1,fontsize=16)
cax = plt.subplot2grid((4,w), (0,w-1), rowspan=1, colspan=1)
plt.colorbar(cax=cax, label='T [deg. C]')
# Ice-snow
ax = plt.subplot2grid((4,w), (1,0), rowspan=1, colspan=w-1, facecolor='white')
plt.pcolormesh(ds.time, ds.z, ds.temp.T, cmap=cmap)
plt.clim(-5, 0)
plt.ylim(-1.5, 0.8)
plt.ylabel('z [m]')
ax.set_xticklabels([])
cax = plt.subplot2grid((4,w), (1,w-1), rowspan=1, colspan=1)
plt.colorbar(cax=cax, label='T [deg. C]')
ax.set_title('-1.5 m to +0.8 m',y=1,fontsize=16)
# Ice-ocean
ax = plt.subplot2grid((4,w), (2,0), rowspan=2, colspan=w-1, facecolor='white')
plt.pcolormesh(ds.time, ds.z, ds.temp.T, cmap=cmap)
plt.clim(-2, 0)
plt.ylim(-2.5, -0.5)
plt.ylabel('z [m]')
cax = plt.subplot2grid((4,w), (2,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label='T [deg. C]')
ax.set_title('-2.5 m to -0.50 m',y=1,fontsize=16)
#
plt.tight_layout()

# plt.savefig(pathroot + '/figures/' + year + '/SIMBA/SIMBA_temp_bymedium.png', dpi=600, bbox_inches='tight')

