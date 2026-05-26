'''
   Load in RBR insrument data and make basic diagnostic plots
'''

#
# Some globals
#

exec(open('../globals.py').read()) # modules, year, pathroot

#
# Load in data
#

ds_T = xr.open_dataset(pathroot + '/data/' + year + '/RBR_IMS/RBR_temperature.nc')
ds_S = xr.open_dataset(pathroot + '/data/' + year + '/RBR_IMS/RBR_salinity_density.nc')
ds_BGC = xr.open_dataset(pathroot + '/data/' + year + '/RBR_IMS/RBR_BGC.nc')
ds_PAR = xr.open_dataset(pathroot + '/data/' + year + '/RBR_IMS/RBR_PAR.nc')

#
# Time series plots
#

# Time series of Salinity
fig,axx = plt.subplots(nrows=4,ncols=1,figsize=(11,8),sharex=True, facecolor='w')
#cols = {1.0: 'black', 5.0: 'blue'}
lw = 3
i = 0
for zi in ds_S.z.data:
    # Salinity
    axx[i].plot(ds_S.time, ds_S.SA.sel(z=zi), color='k', alpha=0.5, zorder=5)
    axx[i].plot(ds_S.time, IMS.DoodsonX0(ds_S.SA.sel(z=zi)), color='k', linewidth=lw, zorder=10, label=str(zi)+' m')
    axx[i].set_ylabel(r'Salinity, $S_\mathrm{A}$ (g/kg)')
    axx[i].legend(loc='lower left')
    # Temperature
    par1 = axx[i].twinx()
    par1.plot(ds_T.time, ds_T.CT.sel(z=zi), color='blue', alpha=0.5, zorder=3)
    par1.plot(ds_T.time, IMS.DoodsonX0(ds_T.CT.sel(z=zi)), color='blue', linewidth=lw, zorder=7)
    par1.set_ylabel(r'Temperature, $\Theta$ ($^\circ$C)', color='blue')
    i += 1
#
plt.xlim([ds_S.time[0], ds_S.time[-1]])
plt.tight_layout()

# plt.savefig('../../figures/' + year + '/RBR_IMS/RBR_Timeseries_SA_CT.png', dpi=600, bbox_inches='tight')

# Time series of BGC variables
fig,axx = plt.subplots(nrows=5,ncols=1,figsize=(11,9),sharex=True, facecolor='w')
cols = {1.0: 'black', 5.0: 'blue'}
lw = 3
# CDOM
for zi in ds_BGC.z.data:
    axx[0].plot(ds_BGC.time, ds_BGC.cdom.sel(z=zi), color=cols[zi], alpha=0.5, zorder=2)
    axx[0].plot(ds_BGC.time, IMS.DoodsonX0(ds_BGC.cdom.sel(z=zi)), color=cols[zi], linewidth=lw, zorder=5, label=str(zi)+' m')
    axx[0].set_ylabel('CDOM (ppt)')
axx[0].legend(loc='upper left')
# Chlorophyll
for zi in ds_BGC.z.data:
    axx[1].plot(ds_BGC.time, ds_BGC.chlorophyll.sel(z=zi), color=cols[zi], alpha=0.5, zorder=2)
    axx[1].plot(ds_BGC.time, IMS.DoodsonX0(ds_BGC.chlorophyll.sel(z=zi)), color=cols[zi], linewidth=lw, zorder=5, label=str(zi)+' m')
    axx[1].set_ylabel(r'Chlorophyll ($\mu$mol/L)')
axx[1].legend(loc='upper left')
# Backscatter
for zi in ds_BGC.z.data:
    axx[2].plot(ds_BGC.time, ds_BGC.backscatter.sel(z=zi), color=cols[zi], alpha=0.5, zorder=2)
    axx[2].plot(ds_BGC.time, IMS.DoodsonX0(ds_BGC.backscatter.sel(z=zi)), color=cols[zi], linewidth=lw, zorder=5, label=str(zi)+' m')
    axx[2].set_ylabel(r'Backscatter (m$^{-1}$ sr$^{-1}$)')
axx[2].legend(loc='upper left')
# Oxygen
for zi in ds_BGC.z.data:
    axx[3].plot(ds_BGC.time, ds_BGC.dissolved_o2_saturation.sel(z=zi), color=cols[zi], alpha=0.5, zorder=2)
    axx[3].plot(ds_BGC.time, IMS.DoodsonX0(ds_BGC.dissolved_o2_saturation.sel(z=zi)), color=cols[zi], linewidth=lw, zorder=5, label=str(zi)+' m')
    axx[3].set_ylabel('Diss. O2 Sat. (%)')
axx[3].legend(loc='upper left')
# PAR
axx[4].plot(ds_PAR.time, ds_PAR.PAR, color=cols[1.0], linewidth=lw, label='1.2 m')
axx[4].set_ylabel(r'PAR (umol m$^{-2}$ s$^{-1}$)')
axx[4].legend(loc='upper left')
#
plt.xlim([ds_BGC.time[0], ds_BGC.time[-1]])
plt.tight_layout()

# plt.savefig('../../figures/' + year + '/RBR_IMS/RBR_Timeseries_BGC.png', dpi=600, bbox_inches='tight')

# Time series of bottom pressure
fig = plt.figure(figsize=(11,3), facecolor='w')
lw = 1.5
plt.plot(ds_T.time, ds_T.p.sel(z=55.0), 'k-', linewidth=lw, label=r'Bottom pressure, $p$')
plt.xlim([ds_S.time[0], ds_S.time[-1]])
plt.legend(loc='lower left')
plt.ylabel(r'Pressure (dbar)')

# plt.savefig('../../figures/' + year + '/RBR_IMS/RBR_Timeseries_BottomPressure.png', dpi=600, bbox_inches='tight')

#
# Time-depth plot of temperatures
#

# Divide sensors into shallow and deep, critical depth of zc of e.g. 10 m
zc = 10.1
z_shallow = -ds_T.sel(z=slice(0,zc)).z.data
z_deep = -ds_T.sel(z=slice(zc,100)).z.data
# Create de-tided temperature data
TNT = ds_T.T.data.copy()
for k in range(TNT.shape[1]):
    TNT[:,k] = IMS.DoodsonX0(TNT[:,k])

# Plot-it-up
fig = plt.figure(figsize=(10,8))
w=40
fontsize=12
levels = np.linspace(-1.8, -0.75, 20)
# Plot hourly data
# Temperature (surface)
ax1 = plt.subplot2grid((4,w), (0,0), rowspan=1, colspan=w-1, facecolor='0.5')
ax1.set_title('Seawater temperature from RBR instruments')
ax1.contourf(ds_T.time, -ds_T.z, ds_T.T.T, cmap=cmocean.cm.thermal, levels=levels, add_colorbar=False)
ax1.set_xticklabels([])
plt.ylim(-zc, 0.)
plt.yticks(fontsize=fontsize)
bbox1 = ax1.get_position().get_points()
ax1.spines['bottom'].set_visible(False)
# sensor locations
[plt.plot(ds_T.time[0], z_shallow[k], c='white', marker='o', markersize=7, markeredgecolor='black', zorder=100, clip_on=False) for k in range(len(z_shallow))]
# Temperature (deep)
ax2 = plt.subplot2grid((4,w), (1,0), rowspan=1, colspan=w-1, facecolor='0.5')
ax2.contourf(ds_T.time, -ds_T.z, ds_T.T.T, cmap=cmocean.cm.thermal, levels=levels, add_colorbar=False)
# sensor locations
[plt.plot(ds_T.time[0], z_deep[k], c='white', marker='o', markersize=7, markeredgecolor='black', zorder=100, clip_on=False) for k in range(len(z_deep))]
plt.ylabel('z (m)',fontsize=fontsize)
ax2.yaxis.set_label_coords(-0.07,0.9) # move the y label
plt.ylim(np.nanmin(-ds_T.z), -zc)
bbox2 = ax2.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax2.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax2.spines['top'].set_visible(False)
ax2.set_xticklabels([])
ax2.set_xlabel('')
plt.yticks(fontsize=fontsize)
# Plot detided hourly data
ax3 = plt.subplot2grid((4,w), (2,0), rowspan=1, colspan=w-1, facecolor='0.5')
ax3.set_title('With Doodson Filter')
ax3.contourf(ds_T.time, -ds_T.z, TNT.T, cmap=cmocean.cm.thermal, levels=levels, add_colorbar=False)
#ax.set_title('RBR temperatures with Doodson filter')
plt.ylabel("")
ax3.set_xticklabels([])
plt.ylim(-zc, 0.)
plt.yticks(fontsize=fontsize)
bbox1 = ax3.get_position().get_points()
ax3.spines['bottom'].set_visible(False)
# # Plot sensor locations
[plt.plot(ds_T.time[0], z_shallow[k], c='white', marker='o', markersize=7, markeredgecolor='black', zorder=100, clip_on=False) for k in range(len(z_shallow))]
# Temperature (deep)
ax4 = plt.subplot2grid((4,w), (3,0), rowspan=1, colspan=w-1, facecolor='0.5')
#im = da_temps_hourly_detided.plot.contourf(cmap=cmocean.cm.thermal,levels=levels,add_colorbar=False)
im = ax4.contourf(ds_T.time, -ds_T.z, TNT.T, cmap=cmocean.cm.thermal, levels=levels, add_colorbar=False)
# Plot sensor locations
[plt.plot(ds_T.time[0], z_deep[k], c='white', marker='o', markersize=7, markeredgecolor='black', zorder=100, clip_on=False) for k in range(len(z_deep))]
plt.ylabel('z (m)',fontsize=fontsize)
ax4.yaxis.set_label_coords(-0.07,0.9) # move the y label
plt.xlabel("")
#plt.xlim(l1.values, l2.values)
plt.xticks(rotation=15,fontsize=fontsize)
plt.yticks(fontsize=fontsize)
plt.ylim(np.nanmin(-ds_T.z), -zc)
bbox2 = ax4.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax4.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax4.spines['top'].set_visible(False)
# Colorbar
cbar = fig.colorbar(im, ax=[ax1, ax2, ax3, ax4], orientation='vertical', fraction=0.04, shrink=0.9,pad=0.03, format=mpl.ticker.FormatStrFormatter('%.2f'))
cbar.ax.tick_params(labelsize=fontsize-2)
cbar.set_label(r'Temperature, $T$ ($^\circ$C)', size=fontsize)
cbar.ax.tick_params(labelsize=fontsize-2)

# plt.savefig('../../figures/' + year + '/RBR_IMS/RBR_TimeDepth_Temperature.png', dpi=600, bbox_inches='tight')

#
# Time series of temperature
#

fig,axx = plt.subplots(nrows=3,ncols=1,figsize=(11,8),sharex=True, facecolor='w')
lw = 3
cm = plt.cm.turbo(np.linspace(0, 1, 2*len(ds_T.z))) # create colormap for time
# Surface
axx[0].set_prop_cycle('color', list(cm)) # color each line in sequential order
axx[0].plot(ds_T.time, ds_T.T.sel(z=1.0), color='k', alpha=0.5, zorder=5)
axx[0].plot(ds_T.time, IMS.DoodsonX0(ds_T.T.sel(z=1.0)), linewidth=lw, zorder=10, label='1.0  m')
axx[0].set_ylabel(r'Temperature, $T$ ($^\circ$C)')
axx[0].legend(loc='upper left', ncols=4).set_zorder(15)
# Shallow
axx[1].set_prop_cycle('color', list(cm)) # color each line in sequential order
for zi in ds_T.sel(z=slice(1.0001,zc)).z.data:
    axx[1].plot(ds_T.time, ds_T.T.sel(z=zi), color='k', alpha=0.5, zorder=5)
    axx[1].plot(ds_T.time, IMS.DoodsonX0(ds_T.T.sel(z=zi)), linewidth=lw, zorder=10, label=str(zi)+' m')
axx[1].set_ylabel(r'Temperature, $T$ ($^\circ$C)')
axx[1].legend(loc='upper left', ncols=4).set_zorder(15)
# Deep
axx[2].set_prop_cycle('color', list(cm)) # color each line in sequential order
for zi in ds_T.sel(z=slice(zc,100)).z.data:
    axx[2].plot(ds_T.time, ds_T.T.sel(z=zi), color='k', alpha=0.5, zorder=5)
    axx[2].plot(ds_T.time, IMS.DoodsonX0(ds_T.T.sel(z=zi)), linewidth=lw, zorder=10, label=str(zi)+' m')
axx[2].set_ylabel(r'Temperature, $T$ ($^\circ$C)')
axx[2].legend(loc='upper left', ncols=4).set_zorder(15)
#
plt.xlim([ds_S.time[0], ds_S.time[-1]])
plt.tight_layout()

# plt.savefig('../../figures/' + year + '/RBR_IMS/RBR_Timeseries_Temperature.png', dpi=600, bbox_inches='tight')

#
# Scatter plots (BGC)
#

variables = ['CT', 'SA', 'cdom', 'chlorophyll', 'backscatter', 'dissolved_o2_saturation']
Nvars = len(variables)
ds = {'CT': ds_T, 'SA': ds_S, 'cdom': ds_BGC, 'chlorophyll': ds_BGC, 'backscatter': ds_BGC, 'dissolved_o2_saturation': ds_BGC}

# Hourly
for zi in ds_BGC.z.values:
    fig, axx = plt.subplots(nrows=Nvars, ncols=Nvars, figsize=(12,11), facecolor='w')
    cnt = 0
    for i in range(Nvars):
        vari = variables[i]
        for j in range(Nvars):
            varj = variables[j]
            im = axx[j][i].scatter(ds[vari][vari].sel(z=zi), ds[varj][varj].sel(z=zi), c=ds[vari].time, s=30., marker='.', alpha=0.5, zorder=10)
            if i == 0:
                axx[j][i].set_ylabel(varj)
            else:
                axx[j][i].set_yticklabels('')
            if j == Nvars-1:
                axx[j][i].set_xlabel(vari)
            else:
                axx[j][i].set_xticklabels('')
            cnt += 1
            axx[j][i].grid(zorder=1)
    plt.tight_layout()
    plt.savefig('../../figures/' + year + '/RBR_IMS/RBR_Scatter_BGC_z' + str(zi) + '.png', dpi=600, bbox_inches='tight')

# No tides (Doodson X0 filter applied)
for zi in ds_BGC.z.values:
    fig, axx = plt.subplots(nrows=Nvars, ncols=Nvars, figsize=(12,11), facecolor='w')
    cnt = 0
    for i in range(Nvars):
        vari = variables[i]
        for j in range(Nvars): 
            varj = variables[j]
            im = axx[j][i].scatter(IMS.DoodsonX0(ds[vari][vari].sel(z=zi)), IMS.DoodsonX0(ds[varj][varj].sel(z=zi)), c=ds[vari].time, s=30., marker='.', alpha=0.5, zorder=10)
            if i == 0:
                axx[j][i].set_ylabel(varj)
            else:
                axx[j][i].set_yticklabels('')
            if j == Nvars-1:
                axx[j][i].set_xlabel(vari)
            else:
                axx[j][i].set_xticklabels('')
            cnt += 1
            axx[j][i].grid(zorder=1)
    plt.tight_layout()
    plt.savefig('../../figures/' + year + '/RBR_IMS/RBR_Scatter_BGC_z' + str(zi) + '_noTides.png', dpi=600, bbox_inches='tight')

#
# T-S diags
#

# Hourly time series
fig = plt.figure(figsize=(10,9))
i = 1
for zi in ds_S.z.data:
    ax = plt.subplot(2,2,i)
    # Density contours
    Tmin = np.nanmin(ds_T.CT.sel(z=zi))
    Tmax = np.nanmax(ds_T.CT.sel(z=zi))
    Smin = np.nanmin(ds_S.SA.sel(z=zi))
    Smax = np.nanmax(ds_S.SA.sel(z=zi))
    T_range = np.linspace(Tmin - 0.05*(Tmax - Tmin), Tmax + 0.05*(Tmax - Tmin))
    S_range = np.linspace(Smin - 0.05*(Smax - Smin), Smax + 0.05*(Smax - Smin))
    Tg, Sg = np.meshgrid(T_range, S_range)
    sigma_theta = gsw.density.sigma0(Sg, Tg)
    cs = plt.contour(Sg, Tg, sigma_theta, colors='lightgrey', zorder=1)
    cl = plt.clabel(cs, fontsize=10, inline=True, fmt='%.1f')
    # T-S scatter
    plt.scatter(ds_S.SA.sel(z=zi), ds_T.CT.sel(z=zi), c=ds_S.time, label=str(zi) + ' m',zorder=5)
    plt.ylim(Tmin - 0.05*(Tmax - Tmin), Tmax + 0.05*(Tmax - Tmin))
    plt.xlim(Smin - 0.05*(Smax - Smin), Smax + 0.05*(Smax - Smin))
    # Labels
    if np.mod(i,2) == 1:
        plt.ylabel(r'Temperature, $\Theta$ ($^\circ$C)')
    if i >= 3:
        plt.xlabel(r'Salinity, $S_\mathrm{A}$ (g/kg)')
    ax.legend(loc='lower left')
    i += 1
#
plt.tight_layout()
    
# plt.savefig('../../figures/' + year + '/RBR_IMS/RBR_Scatter_TS.png', dpi=600, bbox_inches='tight')

# No tides (Doodson X0 filter applied)
fig = plt.figure(figsize=(10,9))
i = 1
for zi in ds_S.z.data:
    ax = plt.subplot(2,2,i)
    # Density contours
    Tmin = np.nanmin(ds_T.CT.sel(z=zi))
    Tmax = np.nanmax(ds_T.CT.sel(z=zi))
    Smin = np.nanmin(ds_S.SA.sel(z=zi))
    Smax = np.nanmax(ds_S.SA.sel(z=zi))
    T_range = np.linspace(Tmin - 0.05*(Tmax - Tmin), Tmax + 0.05*(Tmax - Tmin))
    S_range = np.linspace(Smin - 0.05*(Smax - Smin), Smax + 0.05*(Smax - Smin))
    Tg, Sg = np.meshgrid(T_range, S_range)
    sigma_theta = gsw.density.sigma0(Sg, Tg)
    cs = plt.contour(Sg, Tg, sigma_theta, colors='lightgrey', zorder=1)
    cl = plt.clabel(cs, fontsize=10, inline=True, fmt='%.1f')
    # T-S scatter
    plt.scatter(IMS.DoodsonX0(ds_S.SA.sel(z=zi)), IMS.DoodsonX0(ds_T.CT.sel(z=zi)), c=ds_S.time, label=str(zi) + ' m',zorder=5)
    plt.ylim(Tmin - 0.05*(Tmax - Tmin), Tmax + 0.05*(Tmax - Tmin))
    plt.xlim(Smin - 0.05*(Smax - Smin), Smax + 0.05*(Smax - Smin))
    # Labels
    if np.mod(i,2) == 1:
        plt.ylabel(r'Temperature, $\Theta$ ($^\circ$C)')
    if i >= 3:
        plt.xlabel(r'Salinity, $S_\mathrm{A}$ (g/kg)')
    ax.legend(loc='lower left')
    i += 1
#
plt.tight_layout()

# plt.savefig('../../figures/' + year + '/RBR_IMS/RBR_Scatter_TS_noTides.png', dpi=600, bbox_inches='tight')
