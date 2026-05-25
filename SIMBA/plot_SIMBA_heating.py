'''
    Calculate thermal proxies from SIMBA heating data.
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

# Load temperature deltas

# Initial temp readings are saved to DELDATA0 before heating. 
# Heating turns on for 30s, then temp readings are svaed to DELDATA1.
# Heating continues and temp readings after 90s are saved in DELDATA4.

ds = xr.open_dataset(pathroot + '/data/' + year + '/SIMBA/SIMBA_del.nc')

#
# Calculate thermal proxy ratios
#

T_0_30 = ds.del0/ds.del1 # T @ 0s / T @ 30 s
T_30_120 = ds.del1/ds.del4
T_0_120 = ds.del0/ds.del4

fig = plt.figure(figsize=(18,8),facecolor='white')
ax = fig.add_subplot(111)
im = plt.pcolormesh(ds.time, ds.z, T_30_120.T, cmap='RdBu_r')
cbar = plt.colorbar(pad=0.02)
cbar.set_label(label='Thermal proxy (HT30/HT120)',fontsize=fontsize)

#
# Calculate heating rates
#

HeatRate30 = (ds.del1 - ds.del0)/30
HeatRate90 = (ds.del4 - ds.del1)/90
HeatRate120 = (ds.del4 - ds.del0)/120

fig, axs = plt.subplots(2, 3, figsize=(10, 10), facecolor='white')
cm = plt.cm.bwr(np.linspace(0, 1, len(ds.time)))
# T
# Subplot 1
ax = axs[0, 0]
ax.set_ylim(-1.5, 1.0)
ax.set_prop_cycle('color', list(cm))
ax.plot(ds.del0.T, ds.z)
ax.set_xlabel('[deg. C]', fontsize=fontsize-4)
ax.set_title('T @ t=0s', fontsize=fontsize-4)
# Subplot 2
ax2 = axs[0, 1]
ax2.set_prop_cycle('color', list(cm))
ax2.plot(ds.del1.T, ds.z)
ax2.set_ylim(-1.5, 1.0)
ax2.set_xlabel('[deg. C]', fontsize=fontsize-4)
ax2.set_title('T @ t=30s', fontsize=fontsize-4)
# Subplot 3
ax3 = axs[0, 2]
ax3.set_prop_cycle('color', list(cm))
ax3.plot(ds.del4.T, ds.z)
ax3.set_ylim(-1.5, 1.0)
ax3.set_xlabel('[deg. C]', fontsize=fontsize-4)
ax3.set_title('T @ t=120s', fontsize=fontsize-4)
# dT/dt
# Subplot 4
ax4 = axs[1, 0]
ax4.set_prop_cycle('color', list(cm))
ax4.plot(HeatRate30.T, ds.z)
ax4.set_ylim(-1.5, 1.0)
ax4.set_xlabel('[deg. C/s]', fontsize=fontsize-4)
ax4.set_title('dT/dt (0 to 30s)', fontsize=fontsize-4)
# Subplot 5
ax5 = axs[1, 1]
ax5.set_prop_cycle('color', list(cm))
ax5.plot(HeatRate90.T, ds.z)
ax5.set_ylim(-1.5, 1.0)
ax5.set_xlabel('[deg. C/s]', fontsize=fontsize-4)
ax5.set_title('dT/dt (30s to 90s)', fontsize=fontsize-4)
# Subplot 6
ax6 = axs[1, 2]
ax6.set_prop_cycle('color', list(cm))
pl = ax6.plot(HeatRate120.T, ds.z)
ax6.set_ylim(-1.5, 1.0)
ax6.set_xlabel('[deg. C/s]', fontsize=fontsize-4)
ax6.set_title('dT/dt (0 to 90s)', fontsize=fontsize-4)
# create a ListedColormap and BoundaryNorm
cmap = ListedColormap(cm)
bounds = np.linspace(0, 1, len(ds.del0) + 1)
norm = BoundaryNorm(bounds, cmap.N)
# Add a discrete colorbar for the entire figure
cbar_ax = fig.add_axes([1.01, 0.1, 0.02, 0.8])  # Adjust these values as needed
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
# Add a discrete colorbar
cbar = plt.colorbar(sm, cax=cbar_ax, boundaries=bounds, ticks=0.5*(bounds[1:] + bounds[:-1]))
cbar.set_label('Time', fontsize=fontsize)
# Change the tick labels on the colorbar
new_tick_labels = [pd.to_datetime(str(t)).strftime('%m-%d') for t in ds.del0['time'].values]
cbar.set_ticklabels(new_tick_labels)
cbar.ax.tick_params(labelsize=fontsize-4)
#
n = 3  # Keep every nth label
[l.set_visible(False) for (i,l) in enumerate(cbar.ax.yaxis.get_ticklabels()) if i % n != 0]
#
ax.tick_params(axis='both',labelsize=fontsize-4)
ax2.tick_params(axis='both',labelsize=fontsize-4)
ax3.tick_params(axis='both',labelsize=fontsize-4)
ax4.tick_params(axis='both',labelsize=fontsize-4)
ax5.tick_params(axis='both',labelsize=fontsize-4)
ax6.tick_params(axis='both',labelsize=fontsize-4)
#
plt.tight_layout()

# plt.savefig(pathroot + '/figures/' + year + '/SIMBA/SIMBA_heatingRates.png', dpi=600, bbox_inches='tight')


