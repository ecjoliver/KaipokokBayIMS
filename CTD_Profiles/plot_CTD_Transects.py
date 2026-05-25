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

exec(open('../globals.py').read()) # year[transect], pathroot

# Transect definitions (metadata: field trip and site names)
exec(open('transect_list.py').read())
transect = 'Kaipokok Bay (2026 Apr)' # Choose which one to plot here

#
# Load in data
#

ctd = xr.open_dataset(pathroot + '/data/' + year[transect] + '/CTD_Profiles/CTD_IMS_Transect_' + transect.replace(' ','').replace('(','').replace(')','') + '.nc')

#
# Profile plots
#

# Profiles (top 10 m)
cm = plt.cm.turbo(np.linspace(0, 1, len(ctd.site))) # create colormap for time
variables = ['Conservative_Temperature','Absolute_Salinity','Oxygen Saturation','Chlorophyll','CDOM','Backscatter']
xlabels = [r'$^\circ$C','g/kg','%','$\mu$g/L','ppb','m$^{-1}$ sr$^{-1}$']
fig,axes = plt.subplots(nrows=2,ncols=3,figsize=(12,10),facecolor='white')
for i,ax in enumerate(axes.flatten()):
	ax.set_prop_cycle('color', list(cm)) # color each line in sequential order
	for site in ctd.site:
		ctd_ = ctd.sel(site=site)
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
bounds = np.linspace(0, 1, len(ctd.site) + 1)
norm = BoundaryNorm(bounds, cmap.N)
# Add a discrete colorbar for the entire figure
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar_ax = fig.add_axes([0.94, 0.12, 0.02, 0.75])  # Adjust these values as needed
cbar = plt.colorbar(sm, cax=cbar_ax,boundaries=bounds, ticks=0.5*(bounds[1:] + bounds[:-1]))
# Change the tick labels on the colorbar - month day
new_tick_labels = [s for s in ctd['site'].values]
cbar.set_ticklabels(new_tick_labels)
n = 1  # Keep every nth label
[l.set_visible(False) for (i,l) in enumerate(cbar.ax.yaxis.get_ticklabels()) if i % n != 0]
cbar.ax.tick_params(labelsize=fontsize-2)

# plt.savefig('../../figures/' + year[transect] + '/CTD_Profiles/CTD_IMS_Transect_' + transect.replace(' ','').replace('(','').replace(')','') + '_Profiles_Top10m.png', dpi=600, bbox_inches='tight')

# Profiles (full depth)
cm = plt.cm.turbo(np.linspace(0, 1, len(ctd.site))) # create colormap for time
variables = ['Conservative_Temperature','Absolute_Salinity','Oxygen Saturation','Chlorophyll','CDOM','Backscatter']
xlabels = [r'$^\circ$C','g/kg','%','$\mu$g/L','ppb','m$^{-1}$ sr$^{-1}$']
fig,axes = plt.subplots(nrows=2,ncols=3,figsize=(12,10),facecolor='white')
for i,ax in enumerate(axes.flatten()):
        ax.set_prop_cycle('color', list(cm)) # color each line in sequential order
        for site in ctd.site:
                ctd_ = ctd.sel(site=site)
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
bounds = np.linspace(0, 1, len(ctd.site) + 1)
norm = BoundaryNorm(bounds, cmap.N)
# Add a discrete colorbar for the entire figure
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar_ax = fig.add_axes([0.94, 0.12, 0.02, 0.75])  # Adjust these values as needed
cbar = plt.colorbar(sm, cax=cbar_ax,boundaries=bounds, ticks=0.5*(bounds[1:] + bounds[:-1]))
# Change the tick labels on the colorbar - month day
new_tick_labels = [s for s in ctd['site'].values]
cbar.set_ticklabels(new_tick_labels)
n = 1  # Keep every nth label
[l.set_visible(False) for (i,l) in enumerate(cbar.ax.yaxis.get_ticklabels()) if i % n != 0]
cbar.ax.tick_params(labelsize=fontsize-2)

# plt.savefig('../../figures/' + year[transect] + '/CTD_Profiles/CTD_IMS_Transect_' + transect.replace(' ','').replace('(','').replace(')','') + '_Profiles_FullDepth.png', dpi=600, bbox_inches='tight')

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
# Location
ax = plt.subplot(232)
n_lines = len(ctd.site) # IMS timeseries
cmap = mpl.cm.get_cmap('turbo', n_lines)
tc = np.arange(1., len(ctd.site)+1)
dummie_cax = plt.scatter(tc, tc, c=tc, cmap=cmap)
cbar = plt.colorbar()
cbar.set_ticks(np.linspace(1.5, n_lines-0.5, n_lines))
cbar.ax.set_yticklabels(new_tick_labels)
cbar.ax.tick_params(labelsize=fontsize-2)
plt.cla() # Clear axis
cs = plt.contour(Sg, Tg, sigma_theta, colors='lightgrey', zorder=1)
cl = plt.clabel(cs,fontsize=10,inline=False,fmt='%.1f')
plt.plot(Sfr, Tfr_0, '--', color='0.7', zorder=4)
plt.plot(Sfr, Tfr_50, '-.', color='0.85', zorder=5)
cm = plt.cm.turbo(np.linspace(0, 1, len(ctd.site))) # create colormap for time
ax.set_prop_cycle('color', list(cm)) # color each line in sequential order
for i in range(len(ctd.site)):
    plt.plot(ctd['Absolute_Salinity'][i,:], ctd['Conservative_Temperature'][i,:], '.', zorder=10)
plt.title('Site')
plt.ylim([y1,y2])
plt.xlim([0,34])
# Oxygen
ax = plt.subplot(233)
cs = plt.contour(Sg, Tg, sigma_theta, colors='lightgrey', zorder=1)
cl = plt.clabel(cs,fontsize=10,inline=False,fmt='%.1f')
plt.plot(Sfr, Tfr_0, '--', color='0.7', zorder=4)
plt.plot(Sfr, Tfr_50, '-.', color='0.85', zorder=5)
plt.scatter(ctd['Absolute_Salinity'],ctd['Conservative_Temperature'],c=ctd['Oxygen Saturation'],marker='.',cmap=cmocean.cm.dense_r, zorder=10)
plt.colorbar(label='%')
ax.set_yticklabels([])
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

# plt.savefig('../../figures/' + year[transect] + '/CTD_Profiles/CTD_IMS_Transect_' + transect.replace(' ','').replace('(','').replace(')','') + '_TS.png', dpi=600, bbox_inches='tight')

#
# Interpolated CTD transect in (lon,z) space
#

# Interpolate sections
dlon = 0.001
ctdS = {}
ddepth = {}
llon = {}

# Loop over variables in the xarray Dataset, skipping 'Depth' and 'Time'
for key in ctd.data_vars:
    if ((key != 'Time') and (key != 'Depth')):
        print(key)
        # If a site is missing data, skip it and interpolate the last site with the next one
        ctd_valid = ctd[key].dropna(dim='site', how='all')
        sites_valid = ctd_valid.site.values
        ctdS[key], llon[key], ddepth[key] = IMS.interpSectionStitch(sites_valid, ctd, ctd.longitude.values, key, dlon)

# Buoyancy frequency
p = gsw.p_from_z(-ddepth['Absolute_Salinity'], 54.959)
N2, p_mid = gsw.Nsquared(ctdS['Absolute_Salinity'], ctdS['Conservative_Temperature'], p, 54.959, axis=0)
z_mid = gsw.z_from_p(p_mid, 54.959)

# Plot parameters
D = 10.
bgcol = '0.5'
# Site labels
site_labels_full = {'Pea Point': 'PP', 'Sandbar': 'SAN', 'Halfway Island': 'HI', 'Beaver River Point': 'BRP', 'Rapids': 'RAP', 'Big Point': 'BP', 'PostW': 'PO', 'Postville West': 'POW', 'Goulou': 'GOU', 'Woody Island': 'WI', 'IMS': 'IMS', 'Pugaviks West': 'PUW', 'Pugaviks': 'PUG', 'Alkamy': 'ALK', 'Iggiak': 'IGG', "Cape O'War": 'CW', 'Little Neck': 'LN', 'Ground Island': 'GI', 'Jackos Point': 'JP', 'Cape Point': 'CP', 'Punchin Island': 'PI', 'Black Island': 'BI'}
site_labels = []
for site in ctd.site.data:
    site_labels.append(site_labels_full[site])

# Basics (temp, salt, density)
plt.figure(num=1, figsize=(16,10))
plt.clf()
w = 25
# Ice and snow thickness
ax = plt.subplot2grid((7,w), (0,0), rowspan=1, colspan=w-1)
plt.fill_between(ctd.longitude, 0., ctd.Hsnow, color='0.85') #'lightgray') # Snow
plt.fill_between(ctd.longitude, -1.*ctd.Hice, 0., color='0.5') #'#B0C4DE') #'#d6fffa') # Ice
plt.fill_between(ctd.longitude, -10, -1.*ctd.Hice, color='lightsteelblue') #'#214761') # Water
plt.legend(['Snow', 'Ice', 'Water'], bbox_to_anchor=(1.09,1))
plt.plot(ctd.longitude, ctd.Hsnow,  'k-')
plt.plot(ctd.longitude, -1.*ctd.Hice,  'k-')
plt.plot(ctd.longitude, 0.*ctd.Hice,  'k-', linewidth=0.5)
plt.ylabel('Thickness (m)')
plt.xlim(xlims[transect][0], xlims[transect][1])
plt.ylim(thicklims[transect][0], thicklims[transect][1])
ax.set_xticklabels([])
# Add labels to sites
for i, site in enumerate(ctd.site):
    ax.annotate(site_labels[i],(ctd.longitude[i]-0.01,np.nanmax(ctd.Hsnow)+0.1),size=12,rotation=45,annotation_clip=False)
# Title
ax.set_title(transect, y=1.5, fontsize=16)
# Temperature (surface)
ax = plt.subplot2grid((7,w), (1,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Conservative_Temperature'], -ddepth['Conservative_Temperature'], ctdS['Conservative_Temperature'], cmap=cmocean.cm.thermal)
plt.clim(Tlims[transect][0], Tlims[transect][1])
plt.xlim(xlims[transect][0], xlims[transect][1])
ax.set_xticklabels([])
plt.plot(ctd.longitude.data, 0. + 0.008*Dmax[transect]*np.ones(ctd.longitude.data.shape), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Temperature (deep)
ax = plt.subplot2grid((7,w), (2,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Conservative_Temperature'], -ddepth['Conservative_Temperature'], ctdS['Conservative_Temperature'], cmap=cmocean.cm.thermal)
plt.clim(Tlims[transect][0], Tlims[transect][1])
plt.ylabel('z (m)')
plt.xlim(xlims[transect][0], xlims[transect][1])
ax.set_xticklabels([])
plt.ylim(-1.*Dmax[transect], -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((7,w), (1,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label=r'Temperature, $\Theta$ ($^\circ$C)')
# Salinity (surface)
ax = plt.subplot2grid((7,w), (3,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Absolute_Salinity'], -ddepth['Absolute_Salinity'], ctdS['Absolute_Salinity'], cmap=cmocean.cm.haline)
plt.clim(Slims[transect][0], Slims[transect][1])
plt.xlim(xlims[transect][0], xlims[transect][1])
ax.set_xticklabels([])
plt.plot(ctd.longitude.data, 0. + 0.008*Dmax[transect]*np.ones(ctd.longitude.data.shape), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Salinity (deep)
ax = plt.subplot2grid((7,w), (4,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Absolute_Salinity'], -ddepth['Absolute_Salinity'], ctdS['Absolute_Salinity'], cmap=cmocean.cm.haline)
plt.clim(Slims[transect][0], Slims[transect][1])
plt.ylabel('z (m)')
plt.xlim(xlims[transect][0], xlims[transect][1])
ax.set_xticklabels([])
plt.ylim(-1.*Dmax[transect], -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((7,w), (3,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label=r'Salinity, $S_\mathrm{A}$ (g/kg)')
# Density (surface)
ax = plt.subplot2grid((7,w), (5,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Potential_Density'], -ddepth['Potential_Density'], ctdS['Potential_Density'], cmap=cmocean.cm.dense)
plt.clim(Dlims[transect][0], Dlims[transect][1])
plt.xlabel('Longitude (deg. E)')
plt.plot(ctd.longitude.data, 0. + 0.008*Dmax[transect]*np.ones(ctd.longitude.data.shape), 'd', color='k', clip_on=False)
plt.xlim(xlims[transect][0], xlims[transect][1])
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Density (deep)
ax = plt.subplot2grid((7,w), (6,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Potential_Density'], -ddepth['Potential_Density'], ctdS['Potential_Density'], cmap=cmocean.cm.dense)
plt.clim(Dlims[transect][0], Dlims[transect][1])
plt.ylabel('z (m)')
plt.xlabel('Longitude (deg. E)')
plt.xlim(xlims[transect][0], xlims[transect][1])
plt.ylim(-1.*Dmax[transect], -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((7,w), (5,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label='Density, $\\rho_\\theta$ (kg/m$^3$)')

# plt.savefig('../../figures/' + year[transect] + '/CTD_Profiles/CTD_IMS_Transect_' + transect.replace(' ','').replace('(','').replace(')','') + '_Interpolated_TempSaltIce.png', dpi=600, bbox_inches='tight')

# Higher order physical properties (N2, speed of sound, T-T_fr)
plt.figure(figsize=(16,10))
plt.clf()
w = 25
# Rossby radius and estuary width
ax = plt.subplot2grid((7,w), (0,0), rowspan=1, colspan=w-1)
plot1 = ax.plot(ctd.longitude, ctd.Ld/1e3, 'k-o', label='Rossby radius (Ld)')
ax.set_ylabel('Ld (km)')
ax.set_xlim(xlims[transect][0], xlims[transect][1])
ax.set_xticklabels([])
plt.legend()#lns, labels)
# Add labels to sites
for i, site in enumerate(ctd.site):
    ax.annotate(site_labels[i],(ctd.longitude[i]-0.01, ax.get_ylim()[1]+0.1), size=12, rotation=45, annotation_clip=False)
# Title
ax.set_title(transect, y=1.5, fontsize=16)
# N2 (surface)
#
ax = plt.subplot2grid((7,w), (1,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Salinity'][1:,:], z_mid, N2, cmap=cmocean.cm.tempo)
plt.clim(N2lims[transect][0], N2lims[transect][1])
plt.xlim(xlims[transect][0], xlims[transect][1])
ax.set_xticklabels([])
plt.plot(ctd.longitude.data, 0. + 0.008*Dmax[transect]*np.ones(ctd.longitude.data.shape), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# N2 (deep)
ax = plt.subplot2grid((7,w), (2,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Salinity'][1:,:], z_mid, N2, cmap=cmocean.cm.tempo)
plt.clim(N2lims[transect][0], N2lims[transect][1])
plt.ylabel('z (m)')
plt.xlim(xlims[transect][0], xlims[transect][1])
ax.set_xticklabels([])
plt.ylim(-1.*Dmax[transect], -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((7,w), (1,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label=r'N$^2$ (1/s$^2$)')
# Speed of sound (surface)
ax = plt.subplot2grid((7,w), (3,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Sound Speed'], -ddepth['Sound Speed'], ctdS['Sound Speed'], cmap=cmocean.cm.speed)
plt.clim(CSlims[transect][0], CSlims[transect][1])
plt.xlim(xlims[transect][0], xlims[transect][1])
ax.set_xticklabels([])
plt.plot(ctd.longitude.data, 0. + 0.008*Dmax[transect]*np.ones(ctd.longitude.data.shape), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Speed of sound (deep)
ax = plt.subplot2grid((7,w), (4,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Sound Speed'], -ddepth['Sound Speed'], ctdS['Sound Speed'], cmap=cmocean.cm.speed)
plt.clim(CSlims[transect][0], CSlims[transect][1])
plt.ylabel('z (m)')
plt.xlim(xlims[transect][0], xlims[transect][1])
ax.set_xticklabels([])
plt.ylim(-1.*Dmax[transect], -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((7,w), (3,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label='Speed of sound (m/s)')
# Freezing temp diff (surface)
ax = plt.subplot2grid((7,w), (5,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Conservative_Temperature'], -ddepth['Conservative_Temperature'], ctdS['Conservative_Temperature'] - ctdS['Freezing_Temperature'], cmap=cmocean.cm.balance)
plt.clim(FTlims[transect][0], FTlims[transect][1])
plt.xlabel('Longitude (deg. E)')
plt.xlim(xlims[transect][0], xlims[transect][1])
plt.plot(ctd.longitude.data, 0. + 0.008*Dmax[transect]*np.ones(ctd.longitude.data.shape), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Freezing temp diff (deep)
ax = plt.subplot2grid((7,w), (6,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Conservative_Temperature'], -ddepth['Conservative_Temperature'], ctdS['Conservative_Temperature'] - ctdS['Freezing_Temperature'], cmap=cmocean.cm.balance)
plt.clim(FTlims[transect][0], FTlims[transect][1])
plt.ylabel('z (m)')
plt.xlabel('Longitude (deg. E)')
plt.xlim(xlims[transect][0], xlims[transect][1])
plt.ylim(-1.*Dmax[transect], -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((7,w), (5,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label=r'$\Theta-\Theta_\mathrm{fr}$ ($^\circ$C)')

# plt.savefig('../../figures/' + year[transect] + '/CTD_Profiles/CTD_IMS_Transect_' + transect.replace(' ','').replace('(','').replace(')','') + '_Interpolated_HigherOrderPO.png', dpi=600, bbox_inches='tight')

# BGC Variables
plt.figure(figsize=(18,10))
plt.clf()
w = 25
# Chlorophyll (surface)
ax = plt.subplot2grid((8,w), (0,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Chlorophyll'], -ddepth['Chlorophyll'], ctdS['Chlorophyll'], cmap=cmocean.cm.algae)
plt.clim(Chlims[transect][0], Chlims[transect][1])
plt.xlim(xlims[transect][0], xlims[transect][1])
ax.set_xticklabels([])
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Add labels to sites
for i, site in enumerate(ctd.site):
    ax.annotate(site_labels[i],(ctd.longitude[i]-0.01, 0.5), size=12, rotation=45, annotation_clip=False)
# Title
ax.set_title(transect, y=1.5, fontsize=16)
# Chlorophyll (deep)
ax = plt.subplot2grid((8,w), (1,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Chlorophyll'], -ddepth['Chlorophyll'], ctdS['Chlorophyll'], cmap=cmocean.cm.algae)
plt.clim(Chlims[transect][0], Chlims[transect][1])
plt.ylabel('z (m)')
plt.xlim(xlims[transect][0], xlims[transect][1])
ax.set_xticklabels([])
plt.ylim(-1.*Dmax[transect], -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((8,w), (0,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label=r'Chlorophyll ($\mu$g/L)')
# CDOM (surface)
ax = plt.subplot2grid((8,w), (2,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['CDOM'], -ddepth['CDOM'], ctdS['CDOM'], cmap=cmocean.cm.matter)
plt.clim(CDlims[transect][0], CDlims[transect][1])
plt.xlim(xlims[transect][0], xlims[transect][1])
ax.set_xticklabels([])
plt.plot(ctd.longitude.data, 0. + 0.008*Dmax[transect]*np.ones(ctd.longitude.data.shape), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# CDOM (deep)
ax = plt.subplot2grid((8,w), (3,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['CDOM'], -ddepth['CDOM'], ctdS['CDOM'], cmap=cmocean.cm.matter)
plt.clim(CDlims[transect][0], CDlims[transect][1])
plt.ylabel('z (m)')
plt.xlim(xlims[transect][0], xlims[transect][1])
ax.set_xticklabels([])
plt.ylim(-1.*Dmax[transect], -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((8,w), (2,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label='CDOM (ppb)')
# Backscatter (surface)
ax = plt.subplot2grid((8,w), (4,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Backscatter'], -ddepth['Backscatter'], ctdS['Backscatter'], cmap=cmocean.cm.turbid)
plt.clim(BSlims[transect][0], BSlims[transect][1])
plt.xlim(xlims[transect][0], xlims[transect][1])
ax.set_xticklabels([])
plt.plot(ctd.longitude.data, 0. + 0.008*Dmax[transect]*np.ones(ctd.longitude.data.shape), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Backscatter (deep)
ax = plt.subplot2grid((8,w), (5,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Backscatter'], -ddepth['Backscatter'], ctdS['Backscatter'], cmap=cmocean.cm.turbid)
plt.clim(BSlims[transect][0], BSlims[transect][1])
plt.ylabel('z (m)')
plt.xlim(xlims[transect][0], xlims[transect][1])
ax.set_xticklabels([])
plt.ylim(-1.*Dmax[transect], -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((8,w), (4,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label=r'Backscatter (m$^{-1}$ sr$^{-1}$)')
# Dissolved O2 (shallow)
ax = plt.subplot2grid((8,w), (6,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Oxygen Saturation'], -ddepth['Oxygen Saturation'], ctdS['Oxygen Saturation'], cmap=cmocean.cm.tempo)
plt.clim(OSlims[transect][0], OSlims[transect][1])
plt.xlim(xlims[transect][0], xlims[transect][1])
ax.set_xticklabels([])
plt.plot(ctd.longitude.data, 0. + 0.008*Dmax[transect]*np.ones(ctd.longitude.data.shape), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Dissolved O2 (deep)
ax = plt.subplot2grid((8,w), (7,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Oxygen Saturation'], -ddepth['Oxygen Saturation'], ctdS['Oxygen Saturation'], cmap=cmocean.cm.tempo)
plt.clim(OSlims[transect][0], OSlims[transect][1])
plt.ylabel('z (m)')
plt.xlabel('Longitude (deg. E)')
plt.xlim(xlims[transect][0], xlims[transect][1])
plt.ylim(-1.*Dmax[transect], -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((8,w), (6,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label='Oxygen Satuation (%)')

# plt.savefig('../../figures/' + year[transect] + '/CTD_Profiles/CTD_IMS_Transect_' + transect.replace(' ','').replace('(','').replace(')','') + '_Interpolated_BGC.png', dpi=600, bbox_inches='tight')


