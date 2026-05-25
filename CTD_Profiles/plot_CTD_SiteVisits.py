'''
    Plot profiles from the IMS CTD timeseries
'''

import matplotlib as mpl
mpl.interactive(True)
from matplotlib import pyplot as plt
import numpy as np
from scipy import io
import pandas as pd
import cmocean
import gsw
import os
import xarray as xr
from datetime import datetime
import sys
sys.path.append(os.path.abspath('../../'))
from functions import IMS_toolbox as IMS
from matplotlib.colors import BoundaryNorm, ListedColormap
#from matplotlib import colormaps as cmaps
fontsize=12


#
# Some globals
#

exec(open('../globals.py').read()) # year, pathroot

#
# Load in data
#

ctd = xr.open_dataset(pathroot + '/data/' + year + '/CTD_Profiles/CTD_IMS_SiteVisits.nc')

#
# Profile plots
#

# Profiles (top 10 m)
cm = plt.cm.turbo(np.linspace(0, 1, len(ctd.date))) # create colormap for time
variables = ['Conservative_Temperature','Absolute_Salinity','Oxygen Saturation','Chlorophyll','CDOM','Backscatter']
xlabels = [r'$^\circ$C','g/kg','%','$\mu$g/L','ppb','m$^{-1}$ sr$^{-1}$']
fig,axes = plt.subplots(nrows=2,ncols=3,figsize=(12,10),facecolor='white')
for i,ax in enumerate(axes.flatten()):
	ax.set_prop_cycle('color', list(cm)) # color each line in sequential order
	for date in ctd.date:
		ctd_ = ctd.sel(date=date)
		ax.plot(ctd_[variables[i]],-ctd_['Depth'])
	ax.set_title(variables[i], fontsize=fontsize)
	ax.set_xlabel(xlabels[i],fontsize=fontsize)
	plt.grid()
	ax.tick_params(axis='both',labelsize=fontsize)
	ax.set_ylim([-10,0])

axes[0,0].set_ylabel('z (m)',fontsize=fontsize)
axes[1,0].set_ylabel('z (m)',fontsize=fontsize)

# create a ListedColormap and BoundaryNorm
cmap = ListedColormap(cm)
bounds = np.linspace(0, 1, len(ctd.date) + 1)
norm = BoundaryNorm(bounds, cmap.N)
# Add a discrete colorbar for the entire figure
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar_ax = fig.add_axes([0.94, 0.12, 0.02, 0.75])  # Adjust these values as needed
cbar = plt.colorbar(sm, cax=cbar_ax,boundaries=bounds, ticks=0.5*(bounds[1:] + bounds[:-1]))
# Change the tick labels on the colorbar - month day
new_tick_labels = [pd.to_datetime(str(t)).strftime('%m-%d') for t in ctd['date'].values]
cbar.set_ticklabels(new_tick_labels)
n = 1  # Keep every nth label
[l.set_visible(False) for (i,l) in enumerate(cbar.ax.yaxis.get_ticklabels()) if i % n != 0]
cbar.ax.tick_params(labelsize=fontsize-2)

# plt.savefig('../../figures/' + year + '/CTD_Profiles/CTD_IMS_SiteVisits_Profiles_Top10m.png', dpi=600, bbox_inches='tight')

# Profiles (full depth)
cm = plt.cm.turbo(np.linspace(0, 1, len(ctd.date))) # create colormap for time
variables = ['Conservative_Temperature','Absolute_Salinity','Oxygen Saturation','Chlorophyll','CDOM','Backscatter']
xlabels = [r'$^\circ$C','g/kg','%','$\mu$g/L','ppb','m$^{-1}$ sr$^{-1}$']
fig,axes = plt.subplots(nrows=2,ncols=3,figsize=(12,10),facecolor='white')
for i,ax in enumerate(axes.flatten()):
        ax.set_prop_cycle('color', list(cm)) # color each line in sequential order
        for date in ctd.date:
                ctd_ = ctd.sel(date=date)
                ax.plot(ctd_[variables[i]],-ctd_['Depth'])
        ax.set_title(variables[i], fontsize=fontsize)
        ax.set_xlabel(xlabels[i],fontsize=fontsize)
        plt.grid()
        ax.tick_params(axis='both',labelsize=fontsize)
        ax.set_ylim([-55,0])

axes[0,0].set_ylabel('z (m)',fontsize=fontsize)
axes[1,0].set_ylabel('z (m)',fontsize=fontsize)

# create a ListedColormap and BoundaryNorm
cmap = ListedColormap(cm)
bounds = np.linspace(0, 1, len(ctd.date) + 1)
norm = BoundaryNorm(bounds, cmap.N)
# Add a discrete colorbar for the entire figure
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar_ax = fig.add_axes([0.94, 0.12, 0.02, 0.75])  # Adjust these values as needed
cbar = plt.colorbar(sm, cax=cbar_ax,boundaries=bounds, ticks=0.5*(bounds[1:] + bounds[:-1]))
# Change the tick labels on the colorbar - month day
new_tick_labels = [pd.to_datetime(str(t)).strftime('%m-%d') for t in ctd['date'].values]
cbar.set_ticklabels(new_tick_labels)
n = 1  # Keep every nth label
[l.set_visible(False) for (i,l) in enumerate(cbar.ax.yaxis.get_ticklabels()) if i % n != 0]
cbar.ax.tick_params(labelsize=fontsize-2)

# plt.savefig('../../figures/' + year + '/CTD_Profiles/CTD_IMS_SiteVisits_Profiles_FullDepth.png', dpi=600, bbox_inches='tight')

#
# TS diagrams
#

# Density contours
T_range = np.linspace(-2, np.ceil(ctd.Conservative_Temperature.max()*2)/2)
S_range = np.linspace(0, 35)
Tg, Sg = np.meshgrid(T_range, S_range)
sigma_theta = gsw.density.sigma0(Sg, Tg)
cnt = np.linspace(sigma_theta.min(), sigma_theta.max(), 156)
# Freezing line
Sfr = np.linspace(0, 35)
Tfr_0 = gsw.CT_freezing(Sfr, 0., 0.)
Tfr_50 = gsw.CT_freezing(Sfr, 50., 0.)

# Make plot
fig = plt.figure(figsize=(15,8),facecolor='white',constrained_layout=False)
# limits
y1, y2 = -2, np.ceil(ctd.Conservative_Temperature.max()*2)/2 # IMS timeseries

# Depth
plt.subplot(231)
cs = plt.contour(Sg, Tg, sigma_theta, colors='lightgrey', zorder=1)
cl = plt.clabel(cs,fontsize=10,inline=False,fmt='%.1f')
plt.plot(Sfr, Tfr_0, '--', color='0.7', zorder=4)
plt.plot(Sfr, Tfr_50, '-.', color='0.85', zorder=5)
plt.scatter(ctd['Absolute_Salinity'],ctd['Conservative_Temperature'],c=ctd['Depth'],marker='.',cmap=cmocean.cm.deep, vmin=0, vmax=8, zorder=10)
plt.colorbar(label='m',extend='max')
plt.ylabel(r'Temperature, $\Theta$ [$^\circ$C]')
plt.title('Depth')
plt.ylim([y1,y2])
plt.xlim([0,34])
# Date
ax = plt.subplot(232)
n_lines = len(ctd.date) # IMS timeseries
cmap = mpl.cm.get_cmap('turbo', n_lines)
tc = np.arange(1., len(ctd.date)+1)
dummie_cax = plt.scatter(tc, tc, c=tc, cmap=cmap)
cbar = plt.colorbar()
cbar.ax.set_yticklabels(ctd['date'].dt.strftime("%m-%d").values) # IMS timeseries
plt.cla() # Clear axis
cs = plt.contour(Sg, Tg, sigma_theta, colors='lightgrey', zorder=1)
cl = plt.clabel(cs,fontsize=10,inline=False,fmt='%.1f')
plt.plot(Sfr, Tfr_0, '--', color='0.7', zorder=4)
plt.plot(Sfr, Tfr_50, '-.', color='0.85', zorder=5)
cm = plt.cm.turbo(np.linspace(0, 1, len(ctd.date))) # create colormap for time
ax.set_prop_cycle('color', list(cm)) # color each line in sequential order
for i in range(len(ctd.date)):
    plt.plot(ctd['Absolute_Salinity'][i,:], ctd['Conservative_Temperature'][i,:], '.', zorder=10)
plt.title('Date')
plt.ylim([y1,y2])
plt.xlim([0,34])
# Oxygen
plt.subplot(233)
cs = plt.contour(Sg, Tg, sigma_theta, colors='lightgrey', zorder=1)
cl = plt.clabel(cs,fontsize=10,inline=False,fmt='%.1f')
plt.plot(Sfr, Tfr_0, '--', color='0.7', zorder=4)
plt.plot(Sfr, Tfr_50, '-.', color='0.85', zorder=5)
plt.scatter(ctd['Absolute_Salinity'],ctd['Conservative_Temperature'],c=ctd['Oxygen Saturation'],marker='.',cmap=cmocean.cm.dense_r, zorder=10)
plt.colorbar(label='%')
plt.title('Dissolved O2')
plt.ylim([y1,y2])
plt.xlim([0,34])
# Chlorophyll
plt.subplot(234)
cs = plt.contour(Sg, Tg, sigma_theta, colors='lightgrey', zorder=1)
cl = plt.clabel(cs,fontsize=10,inline=False,fmt='%.1f')
plt.plot(Sfr, Tfr_0, '--', color='0.7', zorder=4)
plt.plot(Sfr, Tfr_50, '-.', color='0.85', zorder=5)
plt.scatter(ctd['Absolute_Salinity'],ctd['Conservative_Temperature'],c=ctd['Chlorophyll'],marker='.',cmap=cmocean.cm.algae, zorder=10)
plt.colorbar(label=r'$\mu$g/L')
plt.title('Chlorophyll')
plt.ylabel(r'Temperature, $\Theta$ [$^\circ$C]')
plt.xlabel(r'Salinity, $S_\mathrm{A}$ [g/kg]')
plt.ylim([y1,y2])
plt.xlim([0,34])
# CDOM
plt.subplot(235)
cs = plt.contour(Sg, Tg, sigma_theta, colors='lightgrey', zorder=1)
cl = plt.clabel(cs,fontsize=10,inline=False,fmt='%.1f')
plt.plot(Sfr, Tfr_0, '--', color='0.7', zorder=4)
plt.plot(Sfr, Tfr_50, '-.', color='0.85', zorder=5)
plt.scatter(ctd['Absolute_Salinity'],ctd['Conservative_Temperature'],c=ctd['CDOM'],marker='.',cmap=cmocean.cm.matter, zorder=10)
plt.colorbar(label='ppb')
plt.title('CDOM')
plt.xlabel(r'Salinity, $S_\mathrm{A}$ [g/kg]')
plt.ylim([y1,y2])
plt.xlim([0,34])
# Backscaatter
plt.subplot(236)
cs = plt.contour(Sg, Tg, sigma_theta, colors='lightgrey', zorder=1)
cl = plt.clabel(cs,fontsize=10,inline=False,fmt='%.1f')
plt.plot(Sfr, Tfr_0, '--', color='0.7', zorder=4)
plt.plot(Sfr, Tfr_50, '-.', color='0.85', zorder=5)
plt.scatter(ctd['Absolute_Salinity'],ctd['Conservative_Temperature'],c=ctd['Backscatter'],marker='.',cmap=cmocean.cm.turbid, zorder=10)
plt.colorbar(label=r'm$^{-1}$ sr$^{-1}$')
plt.title('Backscatter')
plt.xlabel(r'Salinity, $S_\mathrm{A}$ [g/kg]')
plt.ylim([y1,y2])
plt.xlim([0,34])
#
plt.tight_layout()

# plt.savefig('../../figures/' + year + '/CTD_Profiles/CTD_IMS_SiteVisits_TS.png', dpi=600, bbox_inches='tight')

#
# Interpolated CTD time series in (t,z) space
#

# Interpolate time series
dt = 0.5
ctdS = {}
ddepth = {}
ttime = {}

dates_valid = ctd.date.values
times_valid = [pd.Timestamp(dates_valid[i]).toordinal() for i in range(len(dates_valid))]
times_values = [pd.Timestamp(ctd.date.values[i]).toordinal() for i in range(len(ctd.date.values))]

for key in ctd.keys():
    if ((key != 'Time') and (key != 'Depth')):
        print(key)
        ctdS[key], ttime[key], ddepth[key] = IMS.interpSectionStitch_time(times_valid, ctd, times_values, key, dt)

# Calculate dates from ordinal times
ddate = {}
for key in ttime.keys():
    ddate[key] = np.zeros(ttime[key].shape, dtype='datetime64[us]')
    for i in range(ddate[key].shape[0]):
        for j in range(ddate[key].shape[1]):
            ddate[key][i,j] = pd.Timestamp.fromordinal(int(ttime[key][i,j])).to_numpy() + np.timedelta64(int(24*np.mod(ttime[key][i,j], 1)), 'h')

# Buoyancy frequency
p = gsw.p_from_z(-ddepth['Absolute_Salinity'], 54.959)
N2, p_mid = gsw.Nsquared(ctdS['Absolute_Salinity'], ctdS['Conservative_Temperature'], p, 54.959, axis=0)
z_mid = gsw.z_from_p(p_mid, 54.959)

# Plot parameters
D = 10.
Dmax = 55.
bgcol = '0.5'

# Basics
plt.figure(figsize=(16,10))
plt.clf()
w = 25; pl = 2; pu = 98;
# Ice and snow thickness
ax = plt.subplot2grid((7,w), (0,0), rowspan=1, colspan=w-1)
plt.fill_between(ctd.date, 0., ctd.Hsnow, color='0.85') # Snow
plt.fill_between(ctd.date, -1.*ctd.Hice, 0., color='0.5') #'#B0C4DE') # Ice
plt.fill_between(ctd.date, -10, -1.*ctd.Hice, color='lightsteelblue') # # Water
plt.legend(['Snow', 'Ice', 'Water'], bbox_to_anchor=(1.09,1))
plt.plot(ctd.date, ctd.Hsnow,  'k-')
plt.plot(ctd.date, -1.*ctd.Hice,  'k-')
plt.plot(ctd.date, 0.*ctd.Hice,  'k-', linewidth=0.5)
plt.ylabel('Thickness (m)')
plt.xlim(ctd.date[0], ctd.date[-1])
plt.ylim(-1.5, 0.5)
ax.set_xticklabels([])
# Title
ax.set_title('IMS Time Series ' + year, fontsize=16)
# Temperature (surface)
ax = plt.subplot2grid((7,w), (1,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(ddate['Conservative_Temperature'], -ddepth['Conservative_Temperature'], ctdS['Conservative_Temperature'], cmap=cmocean.cm.thermal)
plt.clim(np.nanpercentile(ctdS['Conservative_Temperature'], pl), np.nanpercentile(ctdS['Conservative_Temperature'], pu))
plt.xlim(ctd.date[0], ctd.date[-1])
ax.set_xticklabels([])
plt.plot(ctd.date, 0. + 0.015*np.nanmax(ddepth['Conservative_Temperature'])*np.ones(ctd.date.data.shape), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Temperature (deep)
ax = plt.subplot2grid((7,w), (2,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(ddate['Conservative_Temperature'], -ddepth['Conservative_Temperature'], ctdS['Conservative_Temperature'], cmap=cmocean.cm.thermal)
plt.clim(np.nanpercentile(ctdS['Conservative_Temperature'], pl), np.nanpercentile(ctdS['Conservative_Temperature'], pu))
plt.ylabel('z (m)')
plt.xlim(ctd.date[0], ctd.date[-1])
ax.set_xticklabels([])
plt.ylim(-1.*np.nanmax(ddepth['Conservative_Temperature']), -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((7,w), (1,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label=r'Temperature, $\Theta$ ($^\circ$C)')
# Salinity (surface)
ax = plt.subplot2grid((7,w), (3,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(ddate['Absolute_Salinity'], -ddepth['Absolute_Salinity'], ctdS['Absolute_Salinity'], cmap=cmocean.cm.haline)
plt.clim(np.nanpercentile(ctdS['Absolute_Salinity'], pl), np.nanpercentile(ctdS['Absolute_Salinity'], pu))
plt.xlim(ctd.date[0], ctd.date[-1])
ax.set_xticklabels([])
plt.plot(ctd.date, 0. + 0.015*np.nanmax(ddepth['Conservative_Temperature'])*np.ones(ctd.date.data.shape), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Salinity (deep)
ax = plt.subplot2grid((7,w), (4,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(ddate['Absolute_Salinity'], -ddepth['Absolute_Salinity'], ctdS['Absolute_Salinity'], cmap=cmocean.cm.haline)
plt.clim(np.nanpercentile(ctdS['Absolute_Salinity'], pl), np.nanpercentile(ctdS['Absolute_Salinity'], pu))
plt.ylabel('z (m)')
plt.xlim(ctd.date[0], ctd.date[-1])
ax.set_xticklabels([])
plt.ylim(-1.*np.nanmax(ddepth['Absolute_Salinity']), -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((7,w), (3,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label=r'Salinity, $S_\mathrm{A}$ (g/kg)')
# Density (surface)
ax = plt.subplot2grid((7,w), (5,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(ddate['Potential_Density'], -ddepth['Potential_Density'], ctdS['Potential_Density'], cmap=cmocean.cm.dense)
plt.clim(np.nanpercentile(ctdS['Potential_Density'], pl), np.nanpercentile(ctdS['Potential_Density'], pu))
plt.xlim(ctd.date[0], ctd.date[-1])
ax.set_xticklabels([])
plt.plot(ctd.date, 0. + 0.015*np.nanmax(ddepth['Conservative_Temperature'])*np.ones(ctd.date.data.shape), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Density (deep)
ax = plt.subplot2grid((7,w), (6,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(ddate['Potential_Density'], -ddepth['Potential_Density'], ctdS['Potential_Density'], cmap=cmocean.cm.dense)
plt.clim(np.nanpercentile(ctdS['Potential_Density'], pl), np.nanpercentile(ctdS['Potential_Density'], pu))
plt.ylabel('z (m)')
plt.xlim(ctd.date[0], ctd.date[-1])
plt.ylim(-1.*np.nanmax(ddepth['Potential_Density']), -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((7,w), (5,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label='Density, $\\rho_\\theta$ (kg/m$^3$)')

# plt.savefig('../../figures/' + year + '/CTD_Profiles/CTD_IMS_SiteVisits_Interpolated_TempSaltIce.png', dpi=600, bbox_inches='tight')

# Higher order physical properties (N2, speed of sound, T-T_fr)
plt.figure(figsize=(16,10))
plt.clf()
w = 25
# Rossby radius and estuary width
ax = plt.subplot2grid((7,w), (0,0), rowspan=1, colspan=w-1)
plot1 = ax.plot(ctd.date, ctd.Ld/1e3, 'k-o', label=r'Rossby radius ($L_\mathrm{d}$)')
ax.set_ylabel(r'$L_\mathrm{d}$ (km)')
ax.set_xlim(ctd.date[0], ctd.date[-1])
ax.set_xticklabels([])
plt.legend()#lns, labels)
# Title
ax.set_title('IMS Time Series ' + year, fontsize=16)
# N2 (surface)
ax = plt.subplot2grid((7,w), (1,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(ddate['Salinity'][1:,:], z_mid, N2, cmap=cmocean.cm.tempo)
plt.clim(np.nanpercentile(N2, pl), np.nanpercentile(N2, pu))
ax.set_xlim(ctd.date[0], ctd.date[-1])
ax.set_xticklabels([])
plt.plot(ctd.date, 0. + 0.015*np.nanmax(ddepth['Conservative_Temperature'])*np.ones(ctd.date.data.shape), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# N2 (deep)
ax = plt.subplot2grid((7,w), (2,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(ddate['Salinity'][1:,:], z_mid, N2, cmap=cmocean.cm.tempo)
plt.clim(np.nanpercentile(N2, pl), np.nanpercentile(N2, pu))
plt.ylabel('z (m)')
ax.set_xlim(ctd.date[0], ctd.date[-1])
ax.set_xticklabels([])
plt.ylim(-1.*Dmax, -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((7,w), (1,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label=r'N$^2$ (1/s$^2$)')
# Speed of sound (surface)
ax = plt.subplot2grid((7,w), (3,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(ddate['Sound Speed'], -ddepth['Sound Speed'], ctdS['Sound Speed'], cmap=cmocean.cm.speed)
plt.clim(np.nanpercentile(ctdS['Sound Speed'], pl), np.nanpercentile(ctdS['Sound Speed'], pu))
ax.set_xlim(ctd.date[0], ctd.date[-1])
ax.set_xticklabels([])
plt.plot(ctd.date, 0. + 0.015*np.nanmax(ddepth['Conservative_Temperature'])*np.ones(ctd.date.data.shape), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Speed of sound (deep)
ax = plt.subplot2grid((7,w), (4,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(ddate['Sound Speed'], -ddepth['Sound Speed'], ctdS['Sound Speed'], cmap=cmocean.cm.speed)
plt.clim(np.nanpercentile(ctdS['Sound Speed'], pl), np.nanpercentile(ctdS['Sound Speed'], pu))
plt.ylabel('z (m)')
ax.set_xlim(ctd.date[0], ctd.date[-1])
ax.set_xticklabels([])
plt.ylim(-1.*Dmax, -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((7,w), (3,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label='Speed of sound (m/s)')
# Freezing temp diff (surface)
ax = plt.subplot2grid((7,w), (5,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(ddate['Conservative_Temperature'], -ddepth['Conservative_Temperature'], ctdS['Conservative_Temperature'] - ctdS['Freezing_Temperature'], cmap=cmocean.cm.balance)
plt.clim(-np.nanpercentile(np.abs(ctdS['Conservative_Temperature'] - ctdS['Freezing_Temperature']), pu), np.nanpercentile(np.abs(ctdS['Conservative_Temperature'] - ctdS['Freezing_Temperature']), pu))
plt.xlabel('Longitude (deg. E)')
ax.set_xlim(ctd.date[0], ctd.date[-1])
plt.plot(ctd.date, 0. + 0.015*np.nanmax(ddepth['Conservative_Temperature'])*np.ones(ctd.date.data.shape), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Freezing temp diff (deep)
ax = plt.subplot2grid((7,w), (6,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(ddate['Conservative_Temperature'], -ddepth['Conservative_Temperature'], ctdS['Conservative_Temperature'] - ctdS['Freezing_Temperature'], cmap=cmocean.cm.balance)
plt.clim(-np.nanpercentile(np.abs(ctdS['Conservative_Temperature'] - ctdS['Freezing_Temperature']), pu), np.nanpercentile(np.abs(ctdS['Conservative_Temperature'] - ctdS['Freezing_Temperature']), pu))
plt.ylabel('z (m)')
ax.set_xlim(ctd.date[0], ctd.date[-1])
plt.ylim(-1.*Dmax, -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((7,w), (5,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label=r'$\Theta-\Theta_\mathrm{fr}$ ($^\circ$C)')

# plt.savefig('../../figures/' + year + '/CTD_Profiles/CTD_IMS_SiteVisits_Interpolated_HigherOrderPO.png', dpi=600, bbox_inches='tight')

# BGC Variables
plt.figure(figsize=(18,10))
plt.clf()
w = 25
# Chlorophyll (surface)
ax = plt.subplot2grid((8,w), (0,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(ddate['Chlorophyll'], -ddepth['Chlorophyll'], ctdS['Chlorophyll'], cmap=cmocean.cm.algae)
plt.clim(np.nanpercentile(ctdS['Chlorophyll'], pl), np.nanpercentile(ctdS['Chlorophyll'], pu))
ax.set_xlim(ctd.date[0], ctd.date[-1])
ax.set_xticklabels([])
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Title
ax.set_title('IMS Time Series ' + year, fontsize=16)
# Chlorophyll (deep)
ax = plt.subplot2grid((8,w), (1,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(ddate['Chlorophyll'], -ddepth['Chlorophyll'], ctdS['Chlorophyll'], cmap=cmocean.cm.algae)
plt.clim(np.nanpercentile(ctdS['Chlorophyll'], pl), np.nanpercentile(ctdS['Chlorophyll'], pu))
plt.ylabel('z (m)')
ax.set_xlim(ctd.date[0], ctd.date[-1])
ax.set_xticklabels([])
plt.ylim(-1.*Dmax, -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((8,w), (0,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label=r'Chlorophyll ($\mu$g/L)')
# CDOM (surface)
ax = plt.subplot2grid((8,w), (2,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(ddate['CDOM'], -ddepth['CDOM'], ctdS['CDOM'], cmap=cmocean.cm.matter)
plt.clim(np.nanpercentile(ctdS['CDOM'], pl), np.nanpercentile(ctdS['CDOM'], pu))
ax.set_xlim(ctd.date[0], ctd.date[-1])
ax.set_xticklabels([])
plt.plot(ctd.date, 0. + 0.015*np.nanmax(ddepth['Conservative_Temperature'])*np.ones(ctd.date.data.shape), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# CDOM (deep)
ax = plt.subplot2grid((8,w), (3,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(ddate['CDOM'], -ddepth['CDOM'], ctdS['CDOM'], cmap=cmocean.cm.matter)
plt.clim(np.nanpercentile(ctdS['CDOM'], pl), np.nanpercentile(ctdS['CDOM'], pu))
plt.ylabel('z (m)')
ax.set_xlim(ctd.date[0], ctd.date[-1])
ax.set_xticklabels([])
plt.ylim(-1.*Dmax, -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((8,w), (2,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label='CDOM (ppb)')
# Backscatter (surface)
ax = plt.subplot2grid((8,w), (4,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(ddate['Backscatter'], -ddepth['Backscatter'], ctdS['Backscatter'], cmap=cmocean.cm.turbid)
plt.clim(np.nanpercentile(ctdS['Backscatter'], pl), np.nanpercentile(ctdS['Backscatter'], pu))
ax.set_xlim(ctd.date[0], ctd.date[-1])
ax.set_xticklabels([])
plt.plot(ctd.date, 0. + 0.015*np.nanmax(ddepth['Conservative_Temperature'])*np.ones(ctd.date.data.shape), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Backscatter (deep)
ax = plt.subplot2grid((8,w), (5,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(ddate['Backscatter'], -ddepth['Backscatter'], ctdS['Backscatter'], cmap=cmocean.cm.turbid)
plt.clim(np.nanpercentile(ctdS['Backscatter'], pl), np.nanpercentile(ctdS['Backscatter'], pu))
plt.ylabel('z (m)')
ax.set_xlim(ctd.date[0], ctd.date[-1])
ax.set_xticklabels([])
plt.ylim(-1.*Dmax, -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((8,w), (4,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label=r'Backscatter (m$^{-1}$ sr$^{-1}$)')
# Dissolved O2 (shallow)
ax = plt.subplot2grid((8,w), (6,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(ddate['Oxygen Saturation'], -ddepth['Oxygen Saturation'], ctdS['Oxygen Saturation'], cmap=cmocean.cm.tempo)
plt.clim(np.nanpercentile(ctdS['Oxygen Saturation'], pl), np.nanpercentile(ctdS['Oxygen Saturation'], pu))
ax.set_xlim(ctd.date[0], ctd.date[-1])
ax.set_xticklabels([])
plt.plot(ctd.date, 0. + 0.015*np.nanmax(ddepth['Conservative_Temperature'])*np.ones(ctd.date.data.shape), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Dissolved O2 (deep)
ax = plt.subplot2grid((8,w), (7,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(ddate['Oxygen Saturation'], -ddepth['Oxygen Saturation'], ctdS['Oxygen Saturation'], cmap=cmocean.cm.tempo)
plt.clim(np.nanpercentile(ctdS['Oxygen Saturation'], pl), np.nanpercentile(ctdS['Oxygen Saturation'], pu))
plt.ylabel('z (m)')
ax.set_xlim(ctd.date[0], ctd.date[-1])
plt.ylim(-1.*Dmax, -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((8,w), (6,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label='Oxygen Satuation (%)')

# plt.savefig('../../figures/' + year + '/CTD_Profiles/CTD_IMS_SiteVisits_Interpolated_BGC.png', dpi=600, bbox_inches='tight')

