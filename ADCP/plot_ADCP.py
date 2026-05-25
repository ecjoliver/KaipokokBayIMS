'''
    Load in ADCP data (already processed by Samuel Aucoi) and make plots
'''

import numpy as np
from matplotlib import pyplot as plt
import xarray as xr
from datetime import date
import datetime
from netCDF4 import Dataset
import matplotlib as mpl
mpl.interactive(True)
import cmocean
import sys
import os
sys.path.append(os.path.abspath('../../'))
from functions import IMS_toolbox as IMS

#
# Some globals
#

exec(open('../globals.py').read()) # year, pathroot

#
# Load in data
#

# Signature 1000 data
nc = Dataset(pathroot + '/data/' + year + '/ADCP/sig1000_upward/sig1000_downsized_20min.nc')
u_SIG = nc['uE'][:].data
v_SIG = nc['vN'][:].data
time_SIG = nc['Time'][:].data # days since 1900-01-01 00:00:00
p_SIG = nc['Ps'][:].data # Pressure
VRange_SIG = nc['VRange'][:].data # Along-beam range of the HR burst variables (aligned with beam 5)
#echorange = nc['echorange'][:].data # Along-beam range of the echosounder variables (aligned with beam 5)
#Ae = nc['Ae'][:].data # Echosounder amplitude
nc.close()

# RDI data
nc = Dataset(pathroot + '/data/' + year + '/ADCP/rdi_downward/RDI_processed.nc')
u_RDI = nc['uE'][:].data
v_RDI = nc['vN'][:].data
time_RDI = nc['Time'][:].data # days since 1900-01-01 00:00:00
p_RDI = nc['P'][:].data # Pressure (dbar)
VRange_RDI = nc['VRange'][:].data # distance of each cell from the ADCP
nc.close()

# Reference time to datetime ordinal
time_SIG = time_SIG + date(1900,1,1).toordinal()
time_RDI = time_RDI + date(1900,1,1).toordinal()

#
# Processing of data
#

# Hourly mean of u, v, p variables
dt = 1./24
t_SIG = np.arange(np.floor(time_SIG[0]), np.ceil(time_SIG[-1])+dt, dt)
t_RDI = np.arange(np.floor(time_RDI[0]), np.ceil(time_RDI[-1])+dt, dt)
uh_SIG = np.nan*np.ones((len(t_SIG), u_SIG.shape[1]))
vh_SIG = np.nan*np.ones((len(t_SIG), v_SIG.shape[1]))
ph_SIG = np.nan*np.ones((len(t_SIG),))
uh_RDI = np.nan*np.ones((len(t_RDI), u_RDI.shape[1]))
vh_RDI = np.nan*np.ones((len(t_RDI), v_RDI.shape[1]))
ph_RDI = np.nan*np.ones((len(t_RDI),))
for tt in range(len(t_SIG)):
    ttt = (time_SIG >= t_SIG[tt] - 0.5*dt) * (time_SIG < t_SIG[tt] + 0.5*dt)
    uh_SIG[tt,:] = np.nanmean(u_SIG[ttt,:], axis=0)
    vh_SIG[tt,:] = np.nanmean(v_SIG[ttt,:], axis=0)
    ph_SIG[tt] = np.nanmean(p_SIG[ttt])
for tt in range(len(t_RDI)):
    ttt = (time_RDI >= t_RDI[tt] - 0.5*dt) * (time_RDI < t_RDI[tt] + 0.5*dt)
    uh_RDI[tt,:] = np.nanmean(u_RDI[ttt,:], axis=0)
    vh_RDI[tt,:] = np.nanmean(v_RDI[ttt,:], axis=0)
    ph_RDI[tt] = np.nanmean(p_RDI[ttt])

# Rotate into along channel and across channel directions
th = -30.4*np.pi/180. # rotation angle in radians
#th = -45.0*np.pi/180. # rotation angle in radians
ur_SIG = uh_SIG*np.cos(th) - vh_SIG*np.sin(th)
vr_SIG = uh_SIG*np.sin(th) + vh_SIG*np.cos(th)
ur_RDI = uh_RDI*np.cos(th) - vh_RDI*np.sin(th)
vr_RDI = uh_RDI*np.sin(th) + vh_RDI*np.cos(th)

# Vertical coordinates
z_RDI = -1*(np.nanmean(ph_RDI) - 10.1285) - VRange_RDI
z_SIG = -1*(np.nanmean(ph_SIG) - 10.1285) + VRange_SIG

# Tidal decomposition
uNT_SIG = np.nan*ur_SIG
vNT_SIG = np.nan*vr_SIG
uNT_RDI = np.nan*ur_RDI
vNT_RDI = np.nan*vr_RDI
for k in range(ur_SIG.shape[1]):
    uNT_SIG[:,k] = IMS.DoodsonX0(ur_SIG[:,k])
    vNT_SIG[:,k] = IMS.DoodsonX0(vr_SIG[:,k])
uT_SIG = ur_SIG - uNT_SIG
vT_SIG = vr_SIG - vNT_SIG
for k in range(ur_RDI.shape[1]):
    uNT_RDI[:,k] = IMS.DoodsonX0(ur_RDI[:,k])
    vNT_RDI[:,k] = IMS.DoodsonX0(vr_RDI[:,k])
uT_RDI = ur_RDI - uNT_RDI
vT_RDI = vr_RDI - vNT_RDI

# Create datetime64 array
dates_SIG = [np.datetime64(str(date.fromordinal(int(np.floor(t_SIG[tt]))))) + np.timedelta64(int(np.round(np.mod(t_SIG[tt], 1)*24)), 'h') for tt in range(len(t_SIG))]
dates_RDI = [np.datetime64(str(date.fromordinal(int(np.floor(t_RDI[tt]))))) + np.timedelta64(int(np.round(np.mod(t_RDI[tt], 1)*24)), 'h') for tt in range(len(t_RDI))]

#
# Basic plots
#

# (t,z) heat maps

# RDI, total
plt.figure(figsize=(9,8))
plt.subplot(3,1,1)
plt.pcolor(dates_RDI, z_RDI, ur_RDI.T, cmap=cmocean.cm.balance)
plt.xlim(dates_RDI[0], dates_RDI[-1])
plt.ylim(-55, 0)
plt.clim(-0.06, 0.06)
cbar = plt.colorbar()
cbar.set_label(r'$u$ (m/s)')
plt.subplot(3,1,2)
plt.pcolor(dates_RDI, z_RDI, vr_RDI.T, cmap=cmocean.cm.balance)
plt.xlim(dates_RDI[0], dates_RDI[-1])
plt.ylim(-55, 0)
plt.clim(-0.06, 0.06)
cbar = plt.colorbar()
cbar.set_label(r'$v$ (m/s)')
plt.subplot(3,1,3)
plt.pcolor(dates_RDI, z_RDI, np.sqrt(ur_RDI**2 + vr_RDI**2).T, cmap=cmocean.cm.speed)
plt.xlim(dates_RDI[0], dates_RDI[-1])
plt.ylim(-55, 0)
plt.clim(0, 0.07)
cbar = plt.colorbar()
cbar.set_label('Speed (m/s)')
plt.tight_layout()

plt.savefig('../../figures/' + year + '/ADCP/ADCP_TimeDepth_RDI_Total.png', dpi=600, bbox_inches='tight')

# SIG, total
plt.figure(figsize=(9,8))
plt.subplot(3,1,1)
plt.pcolor(dates_SIG, z_SIG, ur_SIG.T, cmap=cmocean.cm.balance)
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylim(-6.25, 0)
plt.clim(-0.06, 0.06)
cbar = plt.colorbar()
cbar.set_label(r'$u$ (m/s)')
plt.subplot(3,1,2)
plt.pcolor(dates_SIG, z_SIG, vr_SIG.T, cmap=cmocean.cm.balance)
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylim(-6.25, 0)
plt.clim(-0.06, 0.06)
cbar = plt.colorbar()
cbar.set_label(r'$v$ (m/s)')
plt.subplot(3,1,3)
plt.pcolor(dates_SIG, z_SIG, np.sqrt(ur_SIG**2 + vr_SIG**2).T, cmap=cmocean.cm.speed)
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylim(-6.25, 0)
plt.clim(0, 0.07)
cbar = plt.colorbar()
cbar.set_label('Speed (m/s)')
plt.tight_layout()

plt.savefig('../../figures/' + year + '/ADCP/ADCP_TimeDepth_Sig1000_Total.png', dpi=600, bbox_inches='tight')

# Combined, total
plt.figure(figsize=(9,8))
plt.subplot(3,1,1)
plt.pcolor(dates_RDI, z_RDI, ur_RDI.T, cmap=cmocean.cm.balance)
plt.clim(-0.06, 0.06)
plt.pcolor(dates_SIG, z_SIG, ur_SIG.T, cmap=cmocean.cm.balance)
plt.clim(-0.06, 0.06)
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylim(-55, 0)
cbar = plt.colorbar()
cbar.set_label(r'$u$ (m/s)')
plt.subplot(3,1,2)
plt.pcolor(dates_RDI, z_RDI, vr_RDI.T, cmap=cmocean.cm.balance)
plt.clim(-0.06, 0.06)
plt.pcolor(dates_SIG, z_SIG, vr_SIG.T, cmap=cmocean.cm.balance)
plt.clim(-0.06, 0.06)
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylim(-55, 0)
cbar = plt.colorbar()
cbar.set_label(r'$v$ (m/s)')
plt.subplot(3,1,3)
plt.pcolor(dates_RDI, z_RDI, np.sqrt(ur_RDI**2 + vr_RDI**2).T, cmap=cmocean.cm.speed)
plt.clim(0, 0.07)
plt.pcolor(dates_SIG, z_SIG, np.sqrt(ur_SIG**2 + vr_SIG**2).T, cmap=cmocean.cm.speed)
plt.clim(0, 0.07)
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylim(-55, 0)
cbar = plt.colorbar()
cbar.set_label('Speed (m/s)')
plt.tight_layout()

plt.savefig('../../figures/' + year + '/ADCP/ADCP_TimeDepth_Combined_Total.png', dpi=600, bbox_inches='tight')

# RDI, non-tidal
plt.figure(figsize=(9,8))
plt.subplot(3,1,1)
plt.pcolor(dates_RDI, z_RDI, uNT_RDI.T, cmap=cmocean.cm.balance)
plt.xlim(dates_RDI[0], dates_RDI[-1])
plt.ylim(-55, 0)
plt.clim(-0.06, 0.06)
cbar = plt.colorbar()
cbar.set_label(r'$u$ (m/s)')
plt.subplot(3,1,2)
plt.pcolor(dates_RDI, z_RDI, vNT_RDI.T, cmap=cmocean.cm.balance)
plt.xlim(dates_RDI[0], dates_RDI[-1])
plt.ylim(-55, 0)
plt.clim(-0.06, 0.06)
cbar = plt.colorbar()
cbar.set_label(r'$v$ (m/s)')
plt.subplot(3,1,3)
plt.pcolor(dates_RDI, z_RDI, np.sqrt(uNT_RDI**2 + vNT_RDI**2).T, cmap=cmocean.cm.speed)
plt.xlim(dates_RDI[0], dates_RDI[-1])
plt.ylim(-55, 0)
plt.clim(0, 0.07)
cbar = plt.colorbar()
cbar.set_label('Speed (m/s)')
plt.tight_layout()

plt.savefig('../../figures/' + year + '/ADCP/ADCP_TimeDepth_RDI_NonTidal.png', dpi=600, bbox_inches='tight')

# SIG, non-tidal
plt.figure(figsize=(9,8))
plt.subplot(3,1,1)
plt.pcolor(dates_SIG, z_SIG, uNT_SIG.T, cmap=cmocean.cm.balance)
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylim(-6.25, 0)
plt.clim(-0.06, 0.06)
cbar = plt.colorbar()
cbar.set_label(r'$u$ (m/s)')
plt.subplot(3,1,2)
plt.pcolor(dates_SIG, z_SIG, vNT_SIG.T, cmap=cmocean.cm.balance)
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylim(-6.25, 0)
plt.clim(-0.06, 0.06)
cbar = plt.colorbar()
cbar.set_label(r'$v$ (m/s)')
plt.subplot(3,1,3)
plt.pcolor(dates_SIG, z_SIG, np.sqrt(uNT_SIG**2 + vNT_SIG**2).T, cmap=cmocean.cm.speed)
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylim(-6.25, 0)
plt.clim(0, 0.07)
cbar = plt.colorbar()
cbar.set_label('Speed (m/s)')
plt.tight_layout()

plt.savefig('../../figures/' + year + '/ADCP/ADCP_TimeDepth_Sig1000_NonTidal.png', dpi=600, bbox_inches='tight')

# Combined, non-tidal
plt.figure(figsize=(9,8))
plt.subplot(3,1,1)
plt.pcolor(dates_RDI, z_RDI, uNT_RDI.T, cmap=cmocean.cm.balance)
plt.clim(-0.06, 0.06)
plt.pcolor(dates_SIG, z_SIG, uNT_SIG.T, cmap=cmocean.cm.balance)
plt.clim(-0.06, 0.06)
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylim(-55, 0)
cbar = plt.colorbar()
cbar.set_label(r'$u$ (m/s)')
plt.subplot(3,1,2)
plt.pcolor(dates_RDI, z_RDI, vNT_RDI.T, cmap=cmocean.cm.balance)
plt.clim(-0.06, 0.06)
plt.pcolor(dates_SIG, z_SIG, vNT_SIG.T, cmap=cmocean.cm.balance)
plt.clim(-0.06, 0.06)
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylim(-55, 0)
cbar = plt.colorbar()
cbar.set_label(r'$v$ (m/s)')
plt.subplot(3,1,3)
plt.pcolor(dates_RDI, z_RDI, np.sqrt(uNT_RDI**2 + vNT_RDI**2).T, cmap=cmocean.cm.speed)
plt.clim(0, 0.07)
plt.pcolor(dates_SIG, z_SIG, np.sqrt(uNT_SIG**2 + vNT_SIG**2).T, cmap=cmocean.cm.speed)
plt.clim(0, 0.07)
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylim(-55, 0)
cbar = plt.colorbar()
cbar.set_label('Speed (m/s)')
plt.tight_layout()

plt.savefig('../../figures/' + year + '/ADCP/ADCP_TimeDepth_Combined_NonTidal.png', dpi=600, bbox_inches='tight')

# RDI, tidal
plt.figure(figsize=(9,8))
plt.subplot(3,1,1)
plt.pcolor(dates_RDI, z_RDI, uT_RDI.T, cmap=cmocean.cm.balance)
plt.xlim(dates_RDI[0], dates_RDI[-1])
plt.ylim(-55, 0)
plt.clim(-0.06, 0.06)
cbar = plt.colorbar()
cbar.set_label(r'$u$ (m/s)')
plt.subplot(3,1,2)
plt.pcolor(dates_RDI, z_RDI, vT_RDI.T, cmap=cmocean.cm.balance)
plt.xlim(dates_RDI[0], dates_RDI[-1])
plt.ylim(-55, 0)
plt.clim(-0.06, 0.06)
cbar = plt.colorbar()
cbar.set_label(r'$v$ (m/s)')
plt.subplot(3,1,3)
plt.pcolor(dates_RDI, z_RDI, np.sqrt(uT_RDI**2 + vT_RDI**2).T, cmap=cmocean.cm.speed)
plt.xlim(dates_RDI[0], dates_RDI[-1])
plt.ylim(-55, 0)
plt.clim(0, 0.07)
cbar = plt.colorbar()
cbar.set_label('Speed (m/s)')
plt.tight_layout()

plt.savefig('../../figures/' + year + '/ADCP/ADCP_TimeDepth_RDI_Tidal.png', dpi=600, bbox_inches='tight')

# SIG, tidal
plt.figure(figsize=(9,8))
plt.subplot(3,1,1)
plt.pcolor(dates_SIG, z_SIG, uT_SIG.T, cmap=cmocean.cm.balance)
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylim(-6.25, 0)
plt.clim(-0.06, 0.06)
cbar = plt.colorbar()
cbar.set_label(r'$u$ (m/s)')
plt.subplot(3,1,2)
plt.pcolor(dates_SIG, z_SIG, vT_SIG.T, cmap=cmocean.cm.balance)
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylim(-6.25, 0)
plt.clim(-0.06, 0.06)
cbar = plt.colorbar()
cbar.set_label(r'$v$ (m/s)')
plt.subplot(3,1,3)
plt.pcolor(dates_SIG, z_SIG, np.sqrt(uT_SIG**2 + vT_SIG**2).T, cmap=cmocean.cm.speed)
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylim(-6.25, 0)
plt.clim(0, 0.07)
cbar = plt.colorbar()
cbar.set_label('Speed (m/s)')
plt.tight_layout()

plt.savefig('../../figures/' + year + '/ADCP/ADCP_TimeDepth_Sig1000_Tidal.png', dpi=600, bbox_inches='tight')

# Combined, non-tidal
plt.figure(figsize=(9,8))
plt.subplot(3,1,1)
plt.pcolor(dates_RDI, z_RDI, uT_RDI.T, cmap=cmocean.cm.balance)
plt.clim(-0.06, 0.06)
plt.pcolor(dates_SIG, z_SIG, uT_SIG.T, cmap=cmocean.cm.balance)
plt.clim(-0.06, 0.06)
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylim(-55, 0)
cbar = plt.colorbar()
cbar.set_label(r'$u$ (m/s)')
plt.subplot(3,1,2)
plt.pcolor(dates_RDI, z_RDI, vT_RDI.T, cmap=cmocean.cm.balance)
plt.clim(-0.06, 0.06)
plt.pcolor(dates_SIG, z_SIG, vT_SIG.T, cmap=cmocean.cm.balance)
plt.clim(-0.06, 0.06)
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylim(-55, 0)
cbar = plt.colorbar()
cbar.set_label(r'$v$ (m/s)')
plt.subplot(3,1,3)
plt.pcolor(dates_RDI, z_RDI, np.sqrt(uT_RDI**2 + vT_RDI**2).T, cmap=cmocean.cm.speed)
plt.clim(0, 0.07)
plt.pcolor(dates_SIG, z_SIG, np.sqrt(uT_SIG**2 + vT_SIG**2).T, cmap=cmocean.cm.speed)
plt.clim(0, 0.07)
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylim(-55, 0)
cbar = plt.colorbar()
cbar.set_label('Speed (m/s)')
plt.tight_layout()

plt.savefig('../../figures/' + year + '/ADCP/ADCP_TimeDepth_Combined_Tidal.png', dpi=600, bbox_inches='tight')

# Time-mean profiles
plt.figure(figsize=(12,8))
# Non-tidal currents
plt.subplot(1,2,1)
plt.plot(np.nanmean(uNT_RDI, axis=0), z_RDI, 'b-')
plt.plot(np.nanmean(uNT_SIG, axis=0), z_SIG, 'b--')
#
plt.plot(np.nanmean(vNT_RDI, axis=0), z_RDI, 'r-')
plt.plot(np.nanmean(vNT_SIG, axis=0), z_SIG, 'r--')
#
plt.plot(np.sqrt(np.nanmean(uNT_RDI, axis=0)**2 + np.nanmean(vNT_RDI, axis=0)**2), z_RDI, 'k-')
plt.plot(np.sqrt(np.nanmean(uNT_SIG, axis=0)**2 + np.nanmean(vNT_SIG, axis=0)**2), z_SIG, 'k--')
plt.legend(['uNT (RDI)', 'uNT (SIG)', 'vNT (RDI)', 'vNT (SIG)', 'Speed (RDI)', 'Speed (SIG)'], loc='center right')
plt.plot([0, 0], [-55, 0], 'k:')
plt.ylim(-55, 0)
plt.ylabel('z (m)')
plt.xlabel('m/s')
# Tidal currents
plt.subplot(1,2,2)
plt.fill_betweenx(z_RDI, np.nanpercentile(np.sqrt(uT_RDI**2 + vT_RDI**2), 10, axis=0), np.nanpercentile(np.sqrt(uT_RDI**2 + vT_RDI**2), 90, axis=0), color='0.8')
plt.fill_betweenx(z_SIG, np.nanpercentile(np.sqrt(uT_SIG**2 + vT_SIG**2), 10, axis=0), np.nanpercentile(np.sqrt(uT_SIG**2 + vT_SIG**2), 90, axis=0), color='0.8')
plt.plot(np.nanmean(np.sqrt(uT_RDI**2 + vT_RDI**2), axis=0), z_RDI, 'k-')
plt.plot(np.nanmean(np.sqrt(uT_SIG**2 + vT_SIG**2), axis=0), z_SIG, 'k--')
plt.legend(['Tidal speed, 10%-90% (RDI)', 'Tidal speed, 10%-90% (SIG)', 'Tidal speed, mean (RDI)', 'Tidal speed, mean (SIG)']) 
plt.plot([0, 0], [-55, 0], 'k:')
plt.ylim(-55, 0)
plt.ylabel('z (m)')
plt.xlabel('m/s')
plt.tight_layout()

plt.savefig('../../figures/' + year + '/ADCP/ADCP_TimeMean_Profile.png', dpi=600, bbox_inches='tight')

# Vertical mean time series
plt.figure(figsize=(11,9))
ax = plt.subplot(4,1,1)
plt.plot(dates_RDI, np.zeros(t_RDI.shape), 'k:')
plt.plot(dates_RDI, np.nanmean(ur_RDI, axis=1)*np.abs(np.nanmean(np.diff(z_RDI))), alpha=0.5, color='k')
plt.plot(dates_RDI, np.nanmean(uNT_RDI, axis=1)*np.abs(np.nanmean(np.diff(z_RDI))), 'k-', label=r'u')
plt.title('RDI depth-mean')
plt.xlim(dates_RDI[0], dates_RDI[-1])
plt.ylabel('m/s')
plt.legend(loc='lower left')
ax.set_xticklabels([])
ax = plt.subplot(4,1,2)
plt.plot(dates_RDI, np.zeros(t_RDI.shape), 'k:')
plt.plot(dates_RDI, np.nanmean(vr_RDI, axis=1)*np.abs(np.nanmean(np.diff(z_RDI))), alpha=0.5, color='k')
plt.plot(dates_RDI, np.nanmean(vNT_RDI, axis=1)*np.abs(np.nanmean(np.diff(z_RDI))), 'k-', label=r'v')
plt.xlim(dates_RDI[0], dates_RDI[-1])
plt.ylabel('m/s')
plt.legend(loc='lower left')
ax.set_xticklabels([])
ax = plt.subplot(4,1,3)
plt.plot(dates_SIG, np.zeros(t_SIG.shape), 'k:')
plt.plot(dates_SIG, np.nanmean(ur_SIG, axis=1)*np.abs(np.nanmean(np.diff(z_SIG))), alpha=0.5, color='k')
plt.plot(dates_SIG, np.nanmean(uNT_SIG, axis=1)*np.abs(np.nanmean(np.diff(z_SIG))), 'k-', label=r'u')
plt.title('Sig1000 depth-mean')
plt.xlim(dates_RDI[0], dates_RDI[-1])
plt.ylabel('m/s')
plt.legend(loc='lower left')
ax.set_xticklabels([])
ax = plt.subplot(4,1,4)
plt.plot(dates_SIG, np.zeros(t_SIG.shape), 'k:')
plt.plot(dates_SIG, np.nanmean(vr_SIG, axis=1)*np.abs(np.nanmean(np.diff(z_SIG))), alpha=0.5, color='k')
plt.plot(dates_SIG, np.nanmean(vNT_SIG, axis=1)*np.abs(np.nanmean(np.diff(z_SIG))), 'k-', label=r'v')
plt.xlim(dates_RDI[0], dates_RDI[-1])
plt.ylabel('m/s')
plt.legend(loc='lower left')
plt.tight_layout()

plt.savefig('../../figures/' + year + '/ADCP/ADCP_DepthMean_Timeseries.png', dpi=600, bbox_inches='tight')

#
# TCM comparison
#

da_tcm_hourly = xr.open_dataset(pathroot + '/data/' + year + '/TCM-1/TCM_currents_hourly.nc')
da_tcm_detided = xr.open_dataset(pathroot + '/data/' + year + '/TCM-1/TCM_currents_detided.nc')
da_tcm_daily = xr.open_dataset(pathroot + '/data/' + year + '/TCM-1/TCM_currents_daily.nc')
z_tcm = list(da_tcm_hourly['Speed'].z.data)

plt.figure(figsize=(11,9))
ax = plt.subplot(4,1,1)
zi = 1.5
ki = np.argmin(np.abs(z_SIG - (-zi)))
plt.plot(dates_SIG, ur_SIG[:,ki], 'k-', alpha=0.5)
plt.plot(da_tcm_detided.time, da_tcm_hourly['Velocity-E'].sel(z=zi), 'b-', alpha=0.5)
plt.plot(dates_SIG, uNT_SIG[:,ki], 'k-', label=r'$u$ (' + str(-zi) + ' m, Sig1000)')
plt.plot(da_tcm_detided.time, da_tcm_detided['Velocity-E'].sel(z=zi), 'b-', label=r'$u$ (' + str(-zi) + ' m, TCM-1)')
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylabel('m/s')
plt.legend(loc='upper right')
ax.set_xticklabels([])
ax = plt.subplot(4,1,2)
zi = 1.5
ki = np.argmin(np.abs(z_SIG - (-zi)))
plt.plot(dates_SIG, vr_SIG[:,ki], 'k-', alpha=0.5)
plt.plot(da_tcm_detided.time, da_tcm_hourly['Velocity-N'].sel(z=zi), 'b-', alpha=0.5)
plt.plot(dates_SIG, vNT_SIG[:,ki], 'k-', label=r'$v$ (' + str(-zi) + ' m, Sig1000)')
plt.plot(da_tcm_detided.time, da_tcm_detided['Velocity-N'].sel(z=zi), 'b-', label=r'$v$ (' + str(-zi) + ' m, TCM-1)')
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylabel('m/s')
plt.legend(loc='upper right')
ax.set_xticklabels([])
ax = plt.subplot(4,1,3)
zi = 2.0
ki = np.argmin(np.abs(z_SIG - (-zi)))
plt.plot(dates_SIG, ur_SIG[:,ki], 'k-', alpha=0.5)
plt.plot(da_tcm_detided.time, da_tcm_hourly['Velocity-E'].sel(z=zi), 'b-', alpha=0.5)
plt.plot(dates_SIG, uNT_SIG[:,ki], 'k-', label=r'$u$ (' + str(-zi) + ' m, Sig1000)')
plt.plot(da_tcm_detided.time, da_tcm_detided['Velocity-E'].sel(z=zi), 'b-', label=r'$u$ (' + str(-zi) + ' m, TCM-1)')
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylabel('m/s')
plt.legend(loc='upper right')
ax.set_xticklabels([])
ax = plt.subplot(4,1,4)
zi = 2.0
ki = np.argmin(np.abs(z_SIG - (-zi)))
plt.plot(dates_SIG, vr_SIG[:,ki], 'k-', alpha=0.5)
plt.plot(da_tcm_detided.time, da_tcm_hourly['Velocity-N'].sel(z=zi), 'b-', alpha=0.5)
plt.plot(dates_SIG, vNT_SIG[:,ki], 'k-', label=r'$v$ (' + str(-zi) + ' m, Sig1000)')
plt.plot(da_tcm_detided.time, da_tcm_detided['Velocity-N'].sel(z=zi), 'b-', label=r'$v$ (' + str(-zi) + ' m, TCM-1)')
plt.xlim(dates_SIG[0], dates_SIG[-1])
plt.ylabel('m/s')
plt.legend(loc='upper right')
plt.tight_layout()

plt.savefig('../../figures/' + year + '/ADCP/ADCP_TCM1_Comparison.png', dpi=600, bbox_inches='tight')




