'''
Plot stuff for the paper 
'''
import matplotlib.colors as mcolors
import matplotlib as mpl
import matplotlib.collections as mcoll
import colormaps as cmaps
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.colors import LinearSegmentedColormap
from functions import plotting as pl
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
from matplotlib.ticker import MultipleLocator
from datetime import datetime 

t1,t2 = '2024-01-26','2024-04-15'
fontsize = 12

filepath = './Weather/data/2024/postville_weather_2020-2024.csv'
file = pd.read_csv(filepath,low_memory=False)

# Shortcut to just loading rain data
rain_mm = IMS.load_Rway_station_data(file,'rain').sel(time=slice('2024-01-26','2024-04-15'))
# Timeseries of when rainfall != 0
rain_non0 = rain_mm.where(rain_mm>0,drop=True)

def convert2da(sol,begT,endT,params=None,time_origin=0):
    # spinup time
    
    """Create a xarray.DataArray from the Semtner model outputs."""
    # Bulk of the function
    ds_sol = xr.Dataset(coords={'time': T_air.sel(time=slice(begT,endT)).time},
                        data_vars={'H_i': ('time',sol)}
                                   
                       )
    # Then assign some attributes to describe the solution
    ds_sol['H_i'].attrs['name'] = 'Thickness'
    ds_sol['H_i'].attrs['long_name'] = 'Sea Ice Thickness'
    ds_sol['H_i'].attrs['units'] = 'm'

    return ds_sol


# -------------Fig. 2: Evolution of ice and snow (SIMBA and weekly observations) ---------------------------------

time_temp = da_temp.time
# orig = cmaps.NCV_jet 
orig = cmaps.WhBlGrYeRe

cmap = pl.custom_cmap_trimmed(orig,skew=3,vmin=0.2,vmax=1)

# cmap = cmaps.hotres_r
plt.figure(figsize=(10,6),facecolor='white')
ax = plt.subplot(111)
# im = plt.contourf(hours_temp, z, da_temp.T, cmap=cmocean.cm.thermal)#,levels=[-10,-5,-2,-1.8,-1.6,-1.4,-1.2,-1,-0.8,-0.6,-0.4,-0.2,0])
im = plt.pcolormesh(time_temp.values, da_temp.z, da_temp.T, cmap=cmap,alpha=0.8)

plt.clim(-15, 0) # colorbar limits
plt.ylim(-2.9, 1.7)
cbar = plt.colorbar(pad=0.02,extend='both')
cbar.set_label(label=r'Temperature ($^\circ$C)',
                                size=fontsize)
cbar.ax.tick_params(labelsize=fontsize)

# Interfaces and weekly observatinos (ordered for the legend_)
SnowAir, = plt.plot(snow_air.time,snow_air,c='gainsboro',label='Air-snow')
m1, = plt.plot(weekly_ice.time[1:],-weekly_ice['Hice'][1:],'o',c='blue',markeredgecolor='k',clip_on=False, label='Weekly ice thickness')
SnowIce, = plt.plot(snow_ice_smoothed.time,snow_ice_smoothed,c='k',linestyle='-',label='Snow-ice')
m2, = plt.plot(weekly_ice.time[1:],weekly_ice['Hsnow'][1:],'^',c='white',markeredgecolor='k',clip_on=False, label='Weekly snow depth')
IceOcean, = plt.plot(time_temp,H_bottom,'b-',label='Ice-water')


# Line through z=0
plt.axhline(0,color='k',linestyle='--')

plt.ylabel(r'$z$ (m)',fontsize=fontsize)
plt.xlabel('')
ax.tick_params(axis='both',labelsize=fontsize)
ax.tick_params(axis='x',rotation=0,pad=3.5)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

# plt.legend(loc='upper left',fontsize=fontsize)
# legends
l1 = plt.legend(bbox_to_anchor=(0,1.15),loc='upper left',fontsize=fontsize, ncol=3)

plt.xlim(['2024-01-26','2024-04-16'])

# Add dat markers for notable events
# c = 'grey'
# alp = 0.8
# plt.axvline('2024-02-09',c=c,alpha=alp) # Inner ice flooding
# plt.axvline('2024-02-29',c=c,alpha=alp) # Surface flooding
# plt.axvline('2024-02-13',c=c,alpha=alp)
# plt.axvline('2024-02-19',c=c,alpha=alp) # Growth range 13-19 Feb
# plt.axvline('2024-03-09',c=c,alpha=alp) # Second flooding
# plt.axvline('2024-03-23',c=c,alpha=alp) # Third flooding
# plt.axvline('2024-03-27',c=c,alpha=alp) # End of snow accumulation
# plt.axvline('2024-04-08',c=c,alpha=alp) # All dry snow disappeared

event_dates = pd.to_datetime([
    '2024-02-09',
    '2024-02-13',
    '2024-02-19',
    '2024-02-29',
    '2024-03-09',
    '2024-03-23',
    '2024-03-27',
    '2024-04-08'
])
ax = plt.gca()

# Copy the existing major formatter
major_formatter = ax.xaxis.get_major_formatter()

# Apply it to the minor ticks
ax.xaxis.set_minor_formatter(major_formatter)

ax.set_xticks(event_dates, minor=True)

ax.tick_params(
    axis='x',
    which='minor',
    bottom=True,
    top=False,
    direction='in',
    length=6,
    width=1,
    labelbottom=True,
    pad=-32,   # This moves labels above the ticks (inside plot)
    rotation=35,
    labelsize=fontsize
)


#
# plt.savefig('../../../HeatBudget_manuscript/Figures_skeleton/Fig2_SIMBAIceSnow.png',dpi=300, bbox_inches='tight')
#

# -------------Fig. 3: Summary of all atmospheric data ---------------------------------
# Load ERA5 climatolgy of air temp
t2m_clim_ERA5 = xr.open_dataset('/Users/maywang/OneDrive - Dalhousie University/data/ERA5/ERA5_t2m_climatology_daily_1979-2021.nc')
t2m_quantiles = xr.open_dataset('/Users/maywang/OneDrive - Dalhousie University/data/ERA5/ERA5_t2m_clim_quantiles.nc')

t2m_quantiles = t2m_quantiles.assign_coords(
    dayofyear=pd.date_range("2024-01-01", periods=366)
).rename(dayofyear="time")

t2m_clim_ERA5 = t2m_clim_ERA5.assign_coords(
    time=pd.date_range("2024-01-01", periods=366, freq="D")
)
t2m_quantiles_ = t2m_quantiles.sel(time=slice(t1,t2)) - 273.15
p20 = t2m_quantiles_.sel(quantile=0.2)
p80 = t2m_quantiles_.sel(quantile=0.8)
t2m_clim = t2m_clim_ERA5.sel(time=slice(t1,t2)) - 273.15

# Weather station
ds_weather = xr.open_dataset('Weather/data/2024/WeatherVars_CR1000X.nc')
# Work with hourly data
ds_hourly = ds_weather.resample(time="1H").mean('time')
# Wind
wind_speed = ds_hourly.WS_ms_Avg
# Wind is in the COMING FROM direction. Change it to GOING TO directing.
wind_dir = (ds_hourly.WindDir + 180) % 360  

x = ds_hourly['time']

fig,axx = plt.subplots(nrows=7,ncols=1,figsize=(10,10),sharex=True, facecolor='w',layout='constrained')
# fig.suptitle('Ice Monitoring Site Data',fontsize=30,y=0.91)
t = ds_hourly['time'].values
ylims=[-0.5, 12]

## WIND VELOCITY
an = 0
axx[an].text(0.01,1.15,'(a)',fontsize=fontsize,fontweight='bold',transform=axx[an].transAxes,
        verticalalignment='top')
axx[an].set_title('Wind velocity',fontsize=fontsize)
# Create a colormap based on direction
norm = mcolors.Normalize(vmin=0, vmax=360)
cmap_wind = plt.get_cmap('twilight_shifted')

# Create segments for the line plot
t_num = mdates.date2num(t)
points = np.array([t_num, wind_speed]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)

# Create a LineCollection with colors based on wind direction
lc = mcoll.LineCollection(segments, cmap=cmap_wind, norm=norm, linewidth=2)
lc.set_array(wind_dir[:-1])
axx[an].add_collection(lc)

# Set x-limits back to datetime format
axx[an].set_xlim([t.min(), t.max()])
axx[an].set_ylim([wind_speed.min(), wind_speed.max()+2])
axx[an].set_ylabel(r"m s$^{-1}$",fontdict={'fontsize':fontsize})
axx[an].yaxis.set_major_locator(MultipleLocator(5))


## Air Pressure
an = 1
axx[an].text(0.01,1.15,'(b)',fontsize=fontsize,fontweight='bold',transform=axx[an].transAxes,
        verticalalignment='top')
axx[an].plot(t,ds_hourly.BP_mbar_Avg,'black')
axx[an].set_ylabel("mbar",fontdict={'fontsize':fontsize})
axx[an].set_title('Barometric pressure',fontsize=fontsize)
#par1.set_ylim([50, 100])

# air temperature
an = 2
axx[an].text(0.01,1.15,'(c)',fontsize=fontsize,fontweight='bold',transform=axx[an].transAxes,
        verticalalignment='top')
axx[an].fill_between(
    p20.time.values,
    p20.t2m,
    p80.t2m,
    alpha=0.3,
    color='grey'
)
axx[an].plot(t2m_clim.time,t2m_clim.t2m,c='grey',alpha=0.8,label='30-year mean')
axx[an].plot(x,ds_hourly.AirT_C_Avg,'m',label='IMS 2024')
axx[an].set_ylabel('$^\circ$C',fontdict={'fontsize':fontsize})
axx[an].set_title('Air temperature',fontsize=fontsize)
axx[an].set_yticks([-30,-20,-10,0])
axx[an].legend(loc='lower right')

# Dew point
# axx[an].plot(x, ds_hourly.DP_C_Avg, 'g',label='Dew point')
# axx[an].legend(loc='upper left')

# Relative humidity
an = 3
axx[an].text(0.01,1.15,'(d)',fontsize=fontsize,fontweight='bold',transform=axx[an].transAxes,
        verticalalignment='top')
axx[an].plot(x,ds_hourly.Humidity,'black')
axx[an].set_ylabel('%',fontdict={'fontsize':fontsize})
axx[an].set_title('Relative humidity',fontsize=fontsize)

# Downwelling radiation
an = 4
axx[an].text(0.01,1.15,'(e)',fontsize=fontsize,fontweight='bold',transform=axx[an].transAxes,
        verticalalignment='top')
axx[an].plot(t,abs(ds_hourly.SWUpper_Avg),'orange',alpha=0.5)
axx[an].plot(t,abs(ds_hourly.LWUpperCo_Avg),'red')
axx[an].legend(['Incoming SWR','Incoming LWR'],loc='upper right')
axx[an].set_ylabel('W m$^{-2}$',fontdict={'fontsize':fontsize})
axx[an].set_title('Incoming radiation',fontsize=fontsize)

# Net radiation
an = 5
axx[an].text(0.01,1.15,'(f)',fontsize=fontsize,fontweight='bold',transform=axx[an].transAxes,
        verticalalignment='top')
hnSW = axx[an].plot(x,ds_hourly.RsNet_Avg,'peru')
hnLW = axx[an].plot(x,ds_hourly.RlNet_Avg,'firebrick')
axx[an].legend(['Net SWR','Net LWR'],loc='upper right')
axx[an].set_ylabel('W m$^{-2}$',fontdict={'fontsize':fontsize});
axx[an].set_title('Net radiation',fontsize=fontsize)

# Albedo
an = 6
axx[an].text(0.01,1.15,'(g)',fontsize=fontsize,fontweight='bold',transform=axx[an].transAxes,
        verticalalignment='top')
axx[an].plot(albedo.time,albedo,c='navy')
axx[an].set_title('Albedo',fontsize=fontsize)
axx[an].set_ylim([0,1])


# Set x-axis and labels
daily_ticks = ds_hourly['time'].resample(time='D').first().values
# axx[6].set_xticks(x)
# axx[6].set_xticklabels([pd.to_datetime(str(t)).strftime('%m-%d') if t in daily_ticks else '' for t in ds_hourly['time'].values], rotation=45, ha='right')
# axx[6].tick_params(axis='x', rotation=30)
axx[6].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
axx[6].tick_params(axis='x',labelsize=fontsize)

# globals
for ax in axx:
    ax.tick_params(axis='y',labelsize=fontsize)
    ax.grid()


plt.xlim(['2024-01-26','2024-04-15'])

#
# plt.savefig('../../../HeatBudget_manuscript/Figures_skeleton/AtmosphereSummary.png',dpi=600, bbox_inches='tight')
#

# -------------- Compass colorbar for wind plot ----------------

fig_leg, ax_leg = plt.subplots(figsize=(4, 4), subplot_kw={'projection': 'polar'})

# Create circular colormap legend
theta = np.linspace(0, 2 * np.pi, 360)  # 0° to 360°
colors = cmap_wind(norm(np.linspace(0, 360, 360)))  # Get corresponding colors

# Create a circular bar (filled polygon) with wind direction colors
ax_leg.bar(theta, np.ones_like(theta), width=0.05, color=colors, edgecolor='none')

# Set the theta offset to rotate the plot so North is at the top
ax_leg.set_theta_offset(np.pi / 2)  # 90 degrees counterclockwise
ax_leg.set_theta_direction(-1)     # Makes angles increase clockwise


# Set labels for compass directions
ax_leg.set_xticks([0, np.pi / 2, np.pi, 3 * np.pi / 2])
ax_leg.set_xticklabels(['N', 'E', 'S', 'W'], fontsize=80, fontweight=5)
ax_leg.tick_params(axis='both', which='major', pad=15)


# Remove radial labels
ax_leg.set_yticklabels([])
ax_leg.set_yticks([])

# Add a title
# ax_leg.set_title("Wind Direction", fontsize=14, fontweight='bold')

#
# plt.savefig('../../../HeatBudget_manuscript/Figures_skeleton/AtmosphereSummary_leg.png',dpi=600, bbox_inches='tight',transparent=True)
#


# -------------- Fig. 4: Summary of all ocean data ----------------
# load_RBR.py


mpl.rcParams.update({
    "font.size": 12,           # base font size
    "axes.titlesize": 12,      # subplot title
    "axes.labelsize": 12,      # axis labels
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 12,
})

ds_ocean = xr.open_dataset('RBR_IMS/PlottingVars_2024.nc')

T_depths = ds_ocean['T_depths_detided']
SA = ds_ocean['SA_surf_detided'].sel(depth=[-1.88,-2.38])
CT = ds_ocean['CT_surf_detided'].sel(depth=[-1.88,-2.38])

tcm_hourly = xr.open_dataset('TCM-1/TCM_currents_hourly.nc').sel(time=slice(t1,'2024-04-15T00:00:00.000'))
tcm_detided = xr.open_dataset('TCM-1/TCM_currents_detided.nc').sel(time=slice(t1,'2024-04-15T00:00:00.000'))
sensors_deep = T_depths.sel(depth=slice(-56,-8.94)).depth
sensors_shallow = T_depths.sel(depth=slice(-8.94,-1.88)).depth

depths = T_depths.depth
t = ds_ocean.time.values

plt.rcParams['figure.constrained_layout.use'] = False
w=18

plt.figure(figsize=(10,9))

# Ocean currents
ax = plt.subplot2grid((5,w), (0,0), rowspan=1, colspan=w-1, facecolor='white',sharex=ax3)
plt.plot(t, tcm_hourly.sel(Depth=1.5)['Speed'],c='navy',alpha=0.5)
plt.plot(t, tcm_hourly.sel(Depth=2)['Speed'],c='royalblue',alpha=0.5)
plt.plot(t, tcm_detided.sel(Depth=1.5)['Speed'],label='-1.5 m',c='royalblue')
plt.plot(t, tcm_detided.sel(Depth=2)['Speed'],label='-2 m',c='navy')
ax.legend(loc='upper left')
ax.set_xticks(t[::24*4])
ax.set_ylabel('m/s')
ax.set_title('Current speed (near-surface)')
ax.text(0.01,1.16,'(a)',fontweight='bold',transform=ax.transAxes,
        verticalalignment='top')

# Salinity
ax1 = plt.subplot2grid((5,w), (1,0), rowspan=1, colspan=w-1, facecolor='white',sharex=ax)
plt.plot(t[19:-19],SA[0,19:-19],label='-1.88 m',c='darkseagreen')
plt.plot(t[19:-19],SA[1,19:-19],label='-2.38 m',c='forestgreen')
ax1.legend(loc='lower left')
ax1.set_ylabel('g/kg')
ax1.set_title('Absolute salinity (near-surface)')
ax1.text(0.01,1.16,'(b)',fontweight='bold',transform=ax1.transAxes,
        verticalalignment='top')

# Surface temp time series
axt = plt.subplot2grid((5,w), (2,0), rowspan=1, colspan=w-1, facecolor='white',sharex=ax)
plt.plot(t[19:-19],CT[0,19:-19],label='-1.88 m',c='indianred')
plt.plot(t[19:-19],CT[1,19:-19],label='-2.38 m',c='darkred')
axt.legend(loc='upper left')
axt.set_ylabel(r'$^\circ$C')
axt.set_title('Conservative temperature (near-surface)')
axt.text(0.01,1.16,'(c)',fontweight='bold',transform=axt.transAxes,
        verticalalignment='top')

plt.subplots_adjust(hspace=0.25)

# Temperature (shallow)
ax2 = plt.subplot2grid((5,w), (3,0), rowspan=1, colspan=w-1, facecolor='0.5')
levels = np.linspace(-1.8,-1.4,9)
T_depths.plot.contourf(cmap=cmocean.cm.thermal,levels=levels,add_colorbar=False)
# # Plot sensor locations
plt.plot(np.repeat(t[0],len(sensors_shallow)),sensors_shallow,c='white',marker='o',markersize=7,markeredgecolor='black',zorder=100,clip_on=False)
ax2.set_title('Temperature (full depth)')
plt.ylabel("")
plt.ylim(-10, -2)
plt.yticks([-2,-4,-6,-8])
bbox1 = ax2.get_position().get_points()
ax2.spines['bottom'].set_visible(False)
ax2.set_xticklabels([])
ax2.text(0.01,1.16,'(d)',fontweight='bold',transform=ax2.transAxes,
        verticalalignment='top')

# plt.subplots_adjust(hspace=0.2)  

# Temperature (deep)
ax3 = plt.subplot2grid((5,w), (4,0), rowspan=1, colspan=w-1, facecolor='0.5')
im = T_depths.plot.contourf(cmap=cmocean.cm.thermal,levels=levels,add_colorbar=False)
# im = plt.contourf(t,da_temps_hourly_detided,cmap=cmocean.cm.thermal,levels=levels,add_colorbar=False)
# Plot sensor locations
ax3.plot(np.repeat(t[0],len(sensors_deep)),sensors_deep,c='white',marker='o',markersize=7,markeredgecolor='black',zorder=100,clip_on=False)
ax3.set_ylabel(r'$z$ (m)')
ax3.yaxis.label.set_y(0.95)
plt.ylim(np.nanmin(depths), -10)
bbox2 = ax3.get_position().get_points()
bbox2[1][1] = bbox1[0][1] + 0.002 # put upper edge of lower plot flush with lower edge of upper plot
ax3.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax3.spines['top'].set_visible(False)
# colorbar
# Get current position of ax3 to align height
pos = ax3.get_position()
cbar_width = 0.012  # Narrow width
cbar_padding = 0.01
cax = plt.axes([
    pos.x1 + cbar_padding,  # x-position (right of ax3)
    pos.y0,                 # y-position (bottom aligned with ax3)
    cbar_width,             # width
    pos.y1 + 0.02        # height
])
cbar = plt.colorbar(im, cax=cax,format=mpl.ticker.FormatStrFormatter('%.2f'))
cbar.set_label(label='Temperature ($^\circ$C)',
                                size=fontsize)
cbar.ax.tick_params(labelsize=fontsize)

# Add line to separate shallow and deep
ax3.axhline(-10,c='white',linestyle='--')
ax.set_xlim([t1,t2])
ax3.set_xlim([t1,t2])


# Get the tick positions and labels from the bottom subplot (ax3)
tick_locs = ax3.get_xticks()
tick_labels = [label.get_text() for label in ax3.get_xticklabels()]

# Apply to other subplots
for a in [ax, ax1, axt,ax2,ax3]:  
    a.set_xticks(tick_locs)
    a.set_xticklabels([])  # hide labels
    # a.tick_params(axis='y',labelsize=fontsize)

for a in [ax, ax1, axt]:  
    a.grid()

ax3.set_xticklabels(tick_labels, rotation=0, ha='center')
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
ax3.set_xlabel('')

#
# plt.savefig('../../../HeatBudget_manuscript/Figures_skeleton/OceanSummary.png',dpi=600, bbox_inches='tight')
#

# -------------- Fig. 4 d,e: Weekly CTD profiles ----------------

#### Add T/S diagram 

ctd = xr.open_dataset('CTD_transect/CTD_IMS_timeseries.nc')
# Density contours
T_range = np.linspace(-2,1)
S_range = np.linspace(0,32)
Tg, Sg = np.meshgrid(T_range,S_range)
sigma_theta = gsw.density.sigma0(Sg, Tg)
cnt = np.linspace(sigma_theta.min(), sigma_theta.max(),156)

# cm = cmaps.haline(np.linspace(0, 1, len(ctd.date)))
cm = cmaps.cool_dark(np.linspace(0, 1, len(ctd.date)))


variables = ['Conservative_Temperature','Absolute_Salinity']
xlabels = [r'Temperature ($^\circ$C)','Salinity (g/kg)']

fig, axs = plt.subplots(1, 3, figsize=(9, 3), gridspec_kw={'width_ratios':[1,1,1]},constrained_layout=True)  # equal width subplots
for i,ax in enumerate([axs[0],axs[1]]):
        ax.set_prop_cycle('color', list(cm)) # color each line in sequential order

        for date in ctd.date:
                ctd_ = ctd.sel(date=date)
                ax.plot(ctd_[variables[i]],-ctd_['Depth'])

        # ax.set_ylabel('Depth [m]',fontsize=fontsize)
        ax.set_xlabel(xlabels[i])
        ax.tick_params(axis='both')
        ax.set_ylim([-10,0])

axs[0].set_ylabel(r'$z$ (m)',fontsize=fontsize)
axs[1].set_yticklabels([])

## COLORBAR
# create a ListedColormap and BoundaryNorm
cmap = ListedColormap(cm)
bounds = np.linspace(0, 1, len(ctd.date) + 1)
norm = BoundaryNorm(bounds, cmap.N)

# Add a discrete colorbar for the entire figure
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
# cbar_ax = fig.add_axes([0.94, 0.12, 0.02, 0.75])  # Adjust these values as needed
cbar = plt.colorbar(sm, ax=axs[1],fraction=1,pad=0.04,boundaries=bounds, ticks=0.5*(bounds[1:] + bounds[:-1]))
# cbar.set_label('Time', fontsize=fontsize)

# Change the tick labels on the colorbar - month day
# new_tick_labels = [pd.to_datetime(str(t)).strftime('%m-%d %H:%M') for t in da_temp['time'].values]
new_tick_labels = [pd.to_datetime(str(t)).strftime('%m-%d') for t in ctd['date'].values]

cbar.set_ticklabels(new_tick_labels)
n = 2  # Keep every nth label
[l.set_visible(False) for (i,l) in enumerate(cbar.ax.yaxis.get_ticklabels()) if i % n != 0]
cbar.ax.tick_params(labelsize=fontsize)


# orig = cmocean.cm.deep 
orig = cmaps.berlin
cmap = pl.custom_cmap_trimmed(orig, skew=1.4, vmin=0, vmax=8)
sc = axs[2].scatter(ctd['Absolute_Salinity'], ctd['Conservative_Temperature'], 
                    c=ctd['Depth'], marker='.', cmap=cmap, vmin=0, vmax=8, zorder=100)
# Contour labels
cs = axs[2].contour(Sg, Tg, sigma_theta, levels=[0,6,12,18,24],colors='lightgrey', zorder=0)
cl = axs[2].clabel(cs, fontsize=10, inline=True, fmt='%.1f')


# Add colorbar without shrinking axs[0]
cbar = fig.colorbar(sc, ax=axs[2], fraction=1, pad=0.04, extend='max')
cbar.set_label('Depth (m)', size=fontsize)
cbar.ax.tick_params(labelsize=fontsize)

axs[2].set_ylabel(r'Temperature ($^\circ$C)')
axs[2].set_xlabel('Salinity (g/kg)')
axs[2].set_ylim([-2, 0])
axs[2].set_xlim([0, 34])

# Apply to other subplots
for a in axs:  
    a.tick_params(axis='both')

# Add labels
axs[0].text(0.01,1.09,'(e)',fontweight='bold',transform=axs[0].transAxes,
        verticalalignment='top')
axs[1].text(0.01,1.09,'(f)',fontweight='bold',transform=axs[1].transAxes,
        verticalalignment='top')
axs[2].text(0.01,1.09,'(g)',fontweight='bold',transform=axs[2].transAxes,
        verticalalignment='top')

#
# plt.savefig('../../../HeatBudget_manuscript/Figures_skeleton/Fig4e_CTDProfiles.png',dpi=600, bbox_inches='tight')
#

# -------------Fig. 5: Heat fluxes at the surface and bottom ---------------------------------


fig,axx = plt.subplots(nrows=3,ncols=1,figsize=(10,8),sharex=True, facecolor='w',layout='constrained')

t = F_net_surf.time
an = 0 # ax number
# SURFACE HEAT FLUXES
axx[an].text(0.01,0.96,'(a)',fontsize=fontsize+4,fontweight='bold',transform=axx[an].transAxes,
        verticalalignment='top')
axx[an].axhline(0,c='dimgrey',alpha=0.8)
axx[an].plot(t,F_sw_net,color='peru',linestyle='-',label=r'$F_\mathrm{netSWR}$')
axx[an].plot(t,F_lw_net_clean,c='firebrick',label=r'$F_\mathrm{netLWR}$')
axx[an].plot(t,F_sens,c='forestgreen',label=r'$F_\mathrm{SH}$')
axx[an].plot(t,F_c_surf,label=r'$F_\mathrm{c,s}$',c='blue',linestyle='-')
axx[an].plot(t,F_lat,label=r'$F_\mathrm{LH}$',c='violet',linestyle='-')
axx[an].plot(t,F_net_surf,label=r'$F_\mathrm{net,s}$',c='black',linestyle='-',linewidth=1.5)
axx[an].grid()
axx[an].set_ylim([-100,115])
axx[an].set_ylabel(r'W m$^{-2}$',fontsize=fontsize)
l1 = axx[an].legend(bbox_to_anchor=(1.001,1.001),fontsize=fontsize)
l1.set_in_layout(False)
axx[an].tick_params(axis='y',labelsize=fontsize)


an = 1
# 2D CONDUCTIVE HEAT FLUX
axx[an].text(0.01,0.96,'(b)',fontsize=fontsize+4,fontweight='bold',transform=axx[an].transAxes,
        verticalalignment='top')
im = axx[an].pcolormesh(t.values,F_c_2d_daily.z+0.024,F_c_2d_daily.T,cmap='RdBu_r', vmin=-40,vmax=40)
axx[an].pcolormesh(t.values,F_c_snow.z,F_c_snow.T,cmap='RdBu_r', vmin=-40,vmax=40)
axx[an].plot(t,snow_ice,c='k',linewidth=1.5)
# Add reference layer
axx[an].plot(F_c_2d.time, ref_layer_lower,linestyle='--',c='grey') 
axx[an].plot(F_c_2d.time, ref_layer_upper,linestyle='--',c='grey')
# Add surface layer
axx[an].plot(F_c_2d_daily.time, surf_layer_lower,linestyle='--',c='grey') 
axx[an].plot(F_c_2d_daily.time, surf_layer_upper,linestyle='--',c='grey')

H_bottom_daily = H_bottom.resample(time='1D').mean()
axx[an].set_ylabel(r'$z$ (m)',fontdict={'fontsize':fontsize})
# axx[an].set_title(r'Conductive heat flux')
axx[an].set_ylim([-0.75, 1])
# divider = make_axes_locatable(axx[an])
# cax = divider.append_axes('right', size="2%", pad=0.05)
# cbar = fig.colorbar(im, cax=cax)
cbar = fig.colorbar(im, ax=axx[an],pad=0.01)

cbar.set_label(label=r"W m$^{-2}$",
                                size=fontsize)
cbar.ax.tick_params(labelsize=fontsize)
axx[an].tick_params(axis='y',labelsize=fontsize)


an = 2

# BOTTOM HEAT FLUXES
axx[an].text(0.01,0.96,'(c)',fontsize=fontsize+4,fontweight='bold',transform=axx[an].transAxes,
        verticalalignment='top')

F_l_daily_sub = F_l_daily.sel(time=slice('2024-02-02',None))
F_c_daily_sub = F_c_daily.sel(time=slice('2024-02-02',None))
F_w_residual_sub = F_w_residual.sel(time=slice('2024-02-02',None))
t=F_l_daily_sub.time
axx[an].plot(t,F_l_daily_sub,label=r'$F_\mathrm{g}$',c='brown') 
axx[an].plot(t,F_c_daily_sub,label=r'$F_\mathrm{c,b}$',c='blue')
# axx[an].plot(t,F_w_daily_quad,label=r'$F_\mathrm{w}$',c='forestgreen')
axx[an].plot(t,F_w_residual_sub,label=r'$F_\mathrm{w}$',c='forestgreen')
# axx[an].plot(t,F_s_daily,label=r'$F_\mathrm{s}$',c='pink')
# axx[an].plot(F_bot.time,F_bot,label=r'$F_\mathrm{net,b}$',c='black',linewidth=1.5)
# Line separating "cut-off" for acceptable F_l based on FDD model
axx[an].axvline('2024-02-02',c='grey')
axx[an].set_ylabel(r'W m$^{-2}$',fontsize=fontsize)
axx[an].set_ylim([-40, 40])
l2 = axx[an].legend(bbox_to_anchor=(1.001,1.001),loc='upper left',fontsize=fontsize)
l2.set_in_layout(False)

# trigger a draw so that constrained layout is executed once
# before we turn it off when printing....
fig.canvas.draw()
# we want the legend included in the bbox_inches='tight' calcs.
l1.set_in_layout(True)
# we don't want the layout to change at this point.
fig.set_layout_engine('none')
axx[an].grid()
axx[an].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
axx[an].set_xlim([t1,t2])
axx[an].tick_params(axis='y',labelsize=fontsize)
axx[an].tick_params(axis='x',labelsize=fontsize)

#
# plt.savefig('../../../HeatBudget_manuscript/Figures_skeleton/Fig5_HeatFluxes_Fwresidual.png',dpi=300, bbox_inches='tight')
#
# plt.savefig('figures/Presentations/Fig5_HeatFluxes.png',dpi=300, bbox_inches='tight')




# -------------Fig. 7: Net surface heat flux components ---------------------------------
# residual_heat.py

fig,axx = plt.subplots(nrows=3,ncols=1,figsize=(10,8),sharex=True,facecolor='w',layout='constrained')
# fig.suptitle('Net surface heat flux',fontsize=16,y=0.92)

t = F_net_surf.time
an = 0 # ax number

# COMPLETE SURFACE HEAT BALANCE AS STACKED PLOT
F_c_surf_pos = F_c_surf.where(F_c_surf > 0, 0)
F_c_surf_neg = F_c_surf.where(F_c_surf < 0, 0)
F_sens_pos = F_sens.where(F_sens > 0, 0)
F_sens_neg = F_sens.where(F_sens < 0, 0)
F_lat_pos = F_lat.where(F_lat > 0, 0)
F_lat_neg = F_lat.where(F_lat < 0, 0)

axx[an].text(0.01,0.96,'(a) ',fontsize=fontsize+4,fontweight='bold',transform=axx[an].transAxes,
        verticalalignment='top')
bar_width = np.timedelta64(22, 'h')
axx[an].bar(t, F_lw_net_clean, width=bar_width, color='firebrick',label=r'$F_{\mathrm{netLWR}}$')
axx[an].bar(t, F_sw_net, width=bar_width, color='peru',label=r'$F_\mathrm{netSWR}$')
axx[an].bar(t, F_c_surf_neg, width=bar_width, bottom=F_sw_net_clean.where(F_c_surf<0,0), color='steelblue',label=r'$F_\mathrm{c,s}$')
axx[an].bar(t, F_c_surf_pos, width=bar_width, bottom=F_lw_net.where(F_c_surf>0,0), color='steelblue')
axx[an].bar(t, F_sens_neg, width=bar_width, bottom=F_c_surf_neg+F_sw_net.where(F_sens<0,0), color='forestgreen',label=r'$F_\mathrm{SH}$')
axx[an].bar(t, F_sens_pos, width=bar_width, bottom=F_c_surf_pos+F_lw_net_clean.where(F_sens>0,0), color='forestgreen')
axx[an].bar(t, F_lat_neg, width=bar_width, bottom=F_c_surf_neg+F_sw_net.where(F_lat<0,0)+F_sens_neg, color='violet',label=r'$F_\mathrm{LH}$')
axx[an].bar(t, F_lat_pos, width=bar_width, bottom=F_c_surf_pos+F_lw_net_clean.where(F_lat>0,0)+F_sens_pos, color='violet')
axx[an].bar(t, F_snowmelt, width=bar_width, bottom=F_c_surf_neg+F_sw_net.where(F_snowmelt<0,0)+F_sens_neg+F_lat_neg, color='lawngreen',label=r'$F_{\mathrm{m,sn}}$')
axx[an].bar(t, F_icemelt, width=bar_width, bottom=F_c_surf_neg+F_sw_net.where(F_icemelt<0,0)+F_sens_neg+F_lat_neg+F_snowmelt, color='gold',label=r'$F_{\mathrm{m,ic}}$')

axx[an].plot(t,DIFF_roll,'k--',label='Residual \n (smoothed)')
axx[an].set_ylabel(r'W m$^{-2}$',fontsize=fontsize)
l2 = axx[an].legend(bbox_to_anchor=(1,1.001),loc='upper left',fontsize=fontsize)
axx[an].grid()
axx[an].tick_params(axis='y',labelsize=fontsize)

an = 1
axx[an].text(0.01,0.96,'(b) ',fontsize=fontsize+4,fontweight='bold',transform=axx[an].transAxes,
        verticalalignment='top')
axx[an].plot(t,F_net_surf,'k-',label=r'$F_{\mathrm{net,s}}$')
axx[an].plot(t,F_icemelt + F_snowmelt,c='red',label=r'$F_{\mathrm{melt}}$')
axx[an].plot(t,DIFF,c='darkgrey',linestyle='--',label='Residual \n (unsmoothed)') 
axx[an].plot(t,DIFF_roll,'k--',label='Residual \n (smoothed)') 
# axx[an].plot(t,F_snowmelt,c='lawngreen',label=r'$F_{\mathrm{snowmelt}}$')
l2 = axx[an].legend(bbox_to_anchor=(1,1.001),loc='upper left',fontsize=fontsize)
axx[an].set_ylabel(r'W m$^{-2}$',fontsize=fontsize)
axx[an].grid()
axx[an].tick_params(axis='y',labelsize=fontsize)

an = 2
# RESIDUAL PLOTTED AGAINST UNCERTAINTY
axx[an].text(0.01,0.96,'(c)',fontsize=fontsize+4,fontweight='bold',transform=axx[an].transAxes,
        verticalalignment='top')
axx[an].plot(t,DIFF_roll,'k--',label='Residual \n (smoothed)') 
axx[an].fill_between(t.values,-sig_F_surf_roll.values,sig_F_surf_roll.values,alpha=0.3,facecolor='black',label='Uncertainty')
# Add rain
rain_days = np.unique(rain_non0['time'].dt.date.astype('datetime64'))
for day in rain_days[:-1]:
    axx[an].axvspan(day,day+np.timedelta64(1,'D'),color='lightblue',alpha=0.3,lw=0)
# Add last one manually for the legend

axx[an].set_xlim([t[0].values,t[-1].values])
axx[an].axvspan(rain_days[-1],rain_days[-1]+np.timedelta64(1,'D'),color='lightblue',alpha=0.3,lw=0, label='Rain days')
axx[an].set_ylabel(r'W m$^{-2}$',fontsize=fontsize)
axx[an].tick_params(axis='both',labelsize=fontsize)
axx[an].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
l3 = axx[an].legend(bbox_to_anchor=(1,1.001),loc='upper left',fontsize=fontsize)

#
# plt.savefig('../../../HeatBudget_manuscript/Figures_skeleton/Fig7_Residual.png',dpi=300, bbox_inches='tight')
#
# plt.savefig('figures/Presentations/Fig7_residual.png',dpi=300, bbox_inches='tight')



# -------------Fig. 8: Model results ---------------------------------

Hi_sf = xr.open_dataset('HeatBudget/Semtner2Fc_ModRuns_snowfrac_Hi_Kirillov.nc')
Hsi_sf = xr.open_dataset('HeatBudget/Semtner2Fc_ModRuns_snowfrac_Hsi_Kirillov.nc')
ds_reg = xr.open_dataset('HeatBudget/Semtner2Fc_ModRuns_Kirillov.nc')
# Hsi_sf_nomelt = xr.open_dataset('HeatBudget/Semtner2Fc_ModRuns_snowfrac_nomelt.nc')
# Hsi_sf_flood = xr.open_dataset('HeatBudget/Semtner2Fc_ModRuns_snowfrac_FloodOnly_updated.nc')


H_i_noFw = ds_reg['H_i_noFw']
H_i_ = ds_reg['H_i_full']
H_si_ = ds_reg['H_si_noFw']
H_i_noFw_noFlood = ds_reg['H_i_noFlood_noFw']
# fb = ds_reg['fb_full1']
H_si_melt = ds_reg['H_si_MeltOnly']
H_bottom_daily = H_bottom.resample(time='1D').mean()

# Snow air interface
begT = np.datetime64('2024-02-03') # 12 days after SIMBA deployment
endT = np.datetime64('2024-04-15')
snow_air_interp = snow_air.sel(time=slice(begT,endT)).resample(time='1H').interpolate('linear')
# # Interpolate the ends to fill nans
snow_air_interp_ = snow_air_interp.interpolate_na(dim='time',method='nearest',fill_value="extrapolate")
H_s_obs = snow_air_interp_.sel(time=slice(begT,endT))


fig, axx = plt.subplots(figsize=(10,7),nrows=2,sharex=True, layout='constrained',height_ratios=[1.5,1])

######## ax1 ########
# Top subplot spans both columns

# Plot ice
an = 0
t = H_i_.time.values
axx[an].plot(t,-H_i_noFw,color="#1f78b4")
hIce = axx[an].fill_between(t,-H_i_noFw,0,color="#1f78b4",alpha=0.5)

# Plot resulting snow
axx[an].plot(t,H_s_obs,color='gray')
hSnow = axx[an].fill_between(t,H_si_,H_s_obs,color='gray',alpha=0.2)
# Plot snow ice
axx[an].plot(t,H_si_,color="#a6cee3")
hFlood = axx[an].fill_between(t,0,H_si_,color="#a6cee3",alpha=0.5)
axx[an].plot(t,H_si_melt,color="cornflowerblue")
hSInomelt = axx[an].fill_between(t,0,H_si_melt,edgecolor='cornflowerblue',facecolor='none',hatch='..',alpha=0.6)
axx[an].set_ylabel('Vertical distance (m)',fontsize=fontsize)
# axx[0].set_title('Evolution of the Snow & Ice')
axx[an].text(0.01,0.97,'(a)',fontsize=fontsize+4,fontweight='bold',transform=axx[an].transAxes,
        verticalalignment='top')

### Plot observations on top 
# Ice bottom 
hObs, = axx[an].plot(H_bottom.time,H_bottom,'r--',label='Ice bottom')
# Add SIMBA derived snow-ice (total ice thickness minus the draft)
H_si_obs = -(H_ice - H_bottom)
hFloodObs, = axx[an].plot(H_si_obs.time,H_si_obs,linestyle='--',c='green',label='Snow-ice \n interface')

# Add individual observations of SLOB bsaed on site visit datasheets
slob, = axx[an].plot(np.datetime64('2024-03-19').astype(datetime),0.05,'k^',label='Slob')
axx[an].plot(np.datetime64('2024-03-26').astype(datetime),0.16,'k^')
axx[an].plot(np.datetime64('2024-04-02').astype(datetime),0.225,'k^')

# Fill beginning area where model does not run 
fill_mask = H_bottom_daily.time<=ds_reg.time[0]
axx[an].fill_between(H_bottom_daily.time.values,H_bottom_daily,snow_air_daily,where=fill_mask,facecolor='none',hatch='xx',edgecolor='darkgrey')
axx[an].set_xlim(t1,t2)

# legends
l1 = axx[an].legend([hSnow,hFlood,hSInomelt,hIce],['Dry snow','Snow ice','SWE + rain','Sea ice'],bbox_to_anchor=(1,0.99),loc='upper left',title=r'Model',fontsize=fontsize,title_fontsize=fontsize)
# l1 = axx[an].legend([hSnow,hFlood,hIce],['Dry snow','Snow ice','Sea ice'],bbox_to_anchor=(1,0.99),loc='upper left',title=r'Model',fontsize=fontsize,title_fontsize=fontsize)
l2 = axx[an].legend(handles=[hObs,hFloodObs,slob],bbox_to_anchor=(1,0.6),loc='upper left',title='Observations',fontsize=fontsize,title_fontsize=fontsize)
# l2 = axx[an].legend(handles=[hObs,hFloodObs],bbox_to_anchor=(1,0.45),loc='upper left',title='Observations',fontsize=fontsize,title_fontsize=fontsize)
l1.get_title().set_fontweight('bold')
l2.get_title().set_fontweight('bold')

axx[an].add_artist(l1)
axx[an].tick_params(axis='y',labelsize=fontsize)


######## ax2 ########
t = ds_reg.time
# Bottom left
an = 1

axx[an].text(0.01,0.97,'(b)',fontsize=fontsize+4,transform=axx[an].transAxes,
        verticalalignment='top',fontweight='bold')
# axx[an].plot(t,ds_reg['H_i_full'],'green',label=r'Derived $F_\mathrm{w}$')
axx[an].plot(t,ds_reg['H_i_noFw'],c='red',label='Control')
# axx[an].plot(t,ds_reg['H_i_noFlood'],c='blue',label=r'$H_\mathrm{si} = 0$')
axx[an].plot(t,ds_reg['H_i_noFlood_noFw'],c='blue',label=r'$H_\mathrm{si} = 0$')
axx[an].plot(H_bottom.time,-H_bottom,'k-',label='Observations')
axx[an].legend(bbox_to_anchor=(1,0.97),fontsize=fontsize)
axx[an].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
axx[an].grid(True,alpha=0.5)
axx[an].set_ylabel('Sea ice thickness (m)',fontsize=fontsize)
axx[an].set_ylim([0.45,0.64])
# axx[an].set_xlim([t.values[0],None])
axx[an].tick_params(axis='both',labelsize=fontsize)


plt.subplots_adjust(hspace=0.12)
plt.subplots_adjust(wspace=0.19)


#
# plt.savefig('../../../HeatBudget_manuscript/Figures_skeleton/Fig8_Model_Fwresidual.png',dpi=600, bbox_inches='tight')
#
# plt.savefig('figures/Presentations/Fig8_model.png',dpi=300, bbox_inches='tight')




# --------Model results: Heatmaps --------------------------------------

def dataset_to_array(ds):
    varnames = list(ds.data_vars)
    snow_fracs = [float(v.split("_")[-1]) for v in varnames]
    sorted_pairs = sorted(zip(snow_fracs, varnames))
    snow_fracs_sorted, varnames_sorted = zip(*sorted_pairs)
    data = np.stack([ds[v].values for v in varnames_sorted], axis=1)
    return xr.DataArray(data,
                        dims=["time", "snow_frac"],
                        coords={"time": ds["time"].values, "snow_frac": list(snow_fracs_sorted)})

Hi_array = dataset_to_array(Hi_sf.resample(time='1D').mean())
Hsi_array = dataset_to_array(Hsi_sf.resample(time='1D').mean())


# Convert to DataFrame (rows: time, columns: snow_frac)
# hi_df = Hi_array.to_pandas().T
hi_df = (Hi_array - -H_bottom.resample(time='1D').mean()).to_pandas().T
# hsi_df = Hsi_array.to_pandas().T
hsi_df = (Hsi_array - snow_ice).to_pandas().T
htot_df = (Hi_array + Hsi_array).to_pandas().T
diff_from_obs = (Hi_array + Hsi_array) - (Hi_array.sel(snow_frac=1) + Hsi_array.sel(snow_frac=1))# -H_ice.resample(time='1D').mean()
diff_df = diff_from_obs.to_pandas().T

# plt.figure(figsize=(10, 5))
fig, axs = plt.subplots(
    nrows=2, ncols=2,
    figsize=(12,8)
)
hm1 = sns.heatmap(hi_df,
            # cmap="Blues",
            cmap='coolwarm',
            center=0,
            cbar_kws={"label": "(m)"},
            xticklabels=False,
            yticklabels=True,
            ax=axs[0,0])  
# axs[0,0].set_title('Sea ice thickness',fontsize=fontsize,fontweight='bold')
axs[0,0].set_title(r'$\Delta H_i$ (Model - Obs)',fontsize=fontsize,fontweight='bold')


hm2 = sns.heatmap(hsi_df,
            # cmap="Purples",
            cmap='coolwarm',
            center=0,
            cbar_kws={"label": "(m)"},
            xticklabels=False,
            yticklabels=True,
            ax=axs[0,1])  
# axs[0,1].set_title('Snow ice thickness',fontsize=fontsize,fontweight='bold')
axs[0,1].set_title(r'$\Delta H_{si}$ (Model - Obs)',fontsize=fontsize,fontweight='bold')


hm3 = sns.heatmap(htot_df,
            cmap="Greens",
            cbar_kws={"label": "(m)"},
            xticklabels=False,
            yticklabels=True,
            ax=axs[1,0])  
axs[1,0].set_title(r'Total thickness ($H_i + H_{si}$)',fontsize=fontsize,fontweight='bold')

hm4 = sns.heatmap(diff_df,
            cmap="RdBu_r",
            center=0,
            cbar_kws={"label": "(m)"},
            xticklabels=False,
            yticklabels=True,
            ax=axs[1,1])  
# axs[1,1].set_title('Difference in total thickness',fontsize=fontsize,fontweight='bold')
axs[1,1].set_title(r'$\Delta H_{tot}$ (Model only)',fontsize=fontsize,fontweight='bold')


# Set colorbar fontsizes
for hm in [hm1, hm2, hm3, hm4]:
    cbar = hm.collections[0].colorbar
    cbar.ax.tick_params(labelsize=fontsize)              # Tick label size
    cbar.set_label(cbar.ax.get_ylabel(), fontsize=fontsize)  # Axis label size


axs[0,0].set_ylabel("Snow Depth Fraction",fontsize=fontsize)
axs[1,0].set_ylabel("Snow Depth Fraction",fontsize=fontsize)
axs[0,1].set_ylabel('')
axs[1,1].set_ylabel('')

axs[1,0].set_xlabel("Time",fontsize=fontsize)
axs[1,1].set_xlabel("Time",fontsize=fontsize)
axs[0,0].set_xlabel('')
axs[0,1].set_xlabel('')


TT = pd.to_datetime(hi_df.columns)
# Every 15th time index (or every 15 days, if spaced daily)
xtick_locs = np.arange(2, len(TT), 15)
xtick_labels = [TT[i].strftime('%m-%d') for i in xtick_locs]
axs[1,0].set_xticks(ticks=xtick_locs, labels=xtick_labels)
axs[1,1].set_xticks(ticks=xtick_locs, labels=xtick_labels)


# Your desired fractions
wanted_fracs = [0.0, 0.4, 0.8, 1.2, 1.6, 2]

# Actual index as numpy array
index_vals = hi_df.index.astype(float).to_numpy()

# Find closest matches
ytick_locs = [np.argmin(np.abs(index_vals - val)) for val in wanted_fracs]
# Format tick labels: no trailing .0 on whole numbers
ytick_labels = [str(int(v)) if v % 1 == 0 else f"{v:.1f}" for v in wanted_fracs]
for ax in [axs[0,0], axs[0,1], axs[1,0], axs[1,1]]:
    ax.yaxis.grid(True,alpha=0.2)   # Enable gridlines on the y-axis
    ax.set_yticks(ytick_locs)
    ax.set_yticklabels(ytick_labels, fontsize=fontsize)
    ax.tick_params(axis='both',labelsize=fontsize)


for ax in axs.flat:
    for spine in ax.spines.values():
        spine.set_visible(True)        # Ensure spine is visible
        spine.set_edgecolor('grey')   # Set color
        spine.set_linewidth(0.7)       # Set thickness
    for im in ax.get_images():
        cbar = im.colorbar
        if cbar is not None:
            cbar.ax.tick_params(labelsize=fontsize)  # Change tick label fontsize
            cbar.set_label(cbar.ax.get_ylabel(), fontsize=fontsize)  # Change label fontsize

plt.tight_layout()


# plt.savefig('figures/HeatBudget/SnowFrac_HeatMaps_diffs.png',dpi=300)






