'''
    Plot weather station data
'''

# Some globals
exec(open('../globals.py').read()) # modules, year, pathroot

# Load data
#ds = xr.open_dataset('Weather/data/2024/WeatherVars_CR1000X.nc') # Logger data
ds = xr.open_dataset('../../data/' + year + '/WeatherStation/WeatherVars_SD.nc') # SD card data
resampled_data_vars = {var: ds[var].resample(time='1H').mean() for var in ds.data_vars}
ds_hourly = xr.Dataset(resampled_data_vars) # make xr dataset from resampled data
hours = ds_hourly.time.values # For plotting

# Process albedo
# To plot albedo, get rid of points when solar elevation is less than 10 degrees above the horizon
# For now, just manually remove albedo values that are not within 0 and 1
Albedo_Avg = ds.Albedo_Avg
albedo_hourly = Albedo_Avg.resample(time='1H').mean('time')
albedo_hourly_clean = albedo_hourly.where((albedo_hourly >= 0) & (albedo_hourly <=1), other=np.nan)

# Wind
wind_speed = ds_hourly.WS_ms_Avg
# wind_dir = (ds_hourly.WindDir + 180) % 360 # Change wind to GOING TO directing
wind_dir = 1.*ds_hourly.WindDir # Wind is in the COMING FROM direction

#
# Main plot
#

fontsize = 14
labelfontsz=14

plt.rcParams.update({'font.size': fontsize})
fig,axx = plt.subplots(nrows=8,ncols=1,figsize=(15,18),sharex=True, facecolor='w')
# fig.suptitle('Ice Monitoring Site Data',fontsize=30,y=0.91)

ylims=[-0.5, 12]

x = ds_hourly['time']

axx[0].plot(x,wind_speed,color='black')
axx[0].set_ylabel('m/s',color='black',fontdict={'fontsize':labelfontsz})
axx[0].set_title('Wind Speed & Direction', y=0.95)
axx[0].set_ylim([0, 20])
# plot wind direction on same subplot
par1 = axx[0].twinx()
par1.plot(x, wind_dir, 'darkred')
par1.set_ylabel('Wind direction',color='darkred',fontdict={'fontsize':labelfontsz})
par1.set_yticks([0,90,180,270,360])
par1.yaxis.set_ticklabels(['N','E','S','W','N'])
par1.tick_params(axis='y', colors='darkred')
par1.set_ylim([0, 360])

# Air Pressure
axx[1].plot(x,ds_hourly.BP_mbar_Avg,'black')
axx[1].set_ylabel("mbar",fontdict={'fontsize':labelfontsz})
axx[1].set_title('Barometric Pressure', y=0.95)
#par1.set_ylim([50, 100])

# air temperature
axx[2].plot(x,ds_hourly.AirT_C_Avg,'m',label='Air temperature')
axx[2].set_ylabel('$^\circ$C',fontdict={'fontsize':labelfontsz})
axx[2].set_title('Air Temperature', y=0.95)
axx[2].set_yticks([-30,-20,-10,0])

# Dew point
axx[2].plot(x, ds_hourly.DP_C_Avg, 'g',label='Dew point')
axx[2].legend(loc='upper left')

# Relative humidity
#axx[3].plot(x,ds_hourly.Humidity,'black')
axx[3].plot(x,ds_hourly.RH,'black')
axx[3].set_ylabel('%',fontdict={'fontsize':labelfontsz})
axx[3].set_title('Relative humidity', y=0.95)

# Longwave radiation
axx[4].plot(x,abs(ds_hourly.LWUpper_Avg),'teal',alpha=0.5)
axx[4].plot(x,abs(ds_hourly.LWLower_Avg),'brown')
axx[4].legend(['Incoming LWR','Outgoing LWR'],loc='upper left')
axx[4].set_ylabel('$W/m^2$',fontdict={'fontsize':labelfontsz})
axx[4].set_title('Longwave Radiation', y=0.95)

# Shortwave Radiation
axx[5].plot(x,ds_hourly.SWUpper_Avg,'teal',alpha=0.5)
axx[5].plot(x,ds_hourly.SWLower_Avg,'brown')
axx[5].legend(['Incoming SWR','Outgoing SWR'])
axx[5].set_ylabel('$W/m^2$',fontdict={'fontsize':labelfontsz})
axx[5].set_title('Shortwave Radiation', y=0.95)

# Net radiation
hnSW = axx[6].plot(x,ds_hourly.RsNet_Avg,'orange')
hnLW = axx[6].plot(x,ds_hourly.RlNet_Avg,'forestgreen')
axx[6].legend(['Net SW','Net LW'],loc='upper left')
axx[6].set_ylabel('$W/m^2$',fontdict={'fontsize':labelfontsz});
axx[6].set_title('Net Radiation', y=0.95)

# Albedo
axx[7].plot(x, albedo_hourly,'navy',label='Raw albedo')
axx[7].plot(x, albedo_hourly_clean,'red',linewidth=4,label='Clean albedo') # "Cleaned" albedo
axx[7].legend(loc='lower left')
#axx[7].set_ylabel('Albedo',fontdict={'fontsize':labelfontsz});
axx[7].set_title('Albedo', y=0.95)
axx[7].set_ylim([0,1])

# Set x-axis and labels
daily_ticks = ds_hourly['time'].resample(time='D').first().values
# axx[6].set_xticks(x)
# axx[6].set_xticklabels([pd.to_datetime(str(t)).strftime('%m-%d') if t in daily_ticks else '' for t in ds_hourly['time'].values], rotation=45, ha='right')
axx[6].tick_params(axis='x', rotation=30)
#plt.xlim(['2024-01-26','2024-04-12'])
plt.xlim([ds.time[0], ds.time[-1]])

#
# plt.savefig('../../figures/' + year + '/WeatherStation/Weather_StackedTimeSeries.png', dpi=600, bbox_inches='tight')
#

#
# Wind rose
#

# Start on Jan. 26
#ds = ds.sel(time=slice("2025-02-19","2025-04-11")) # Sort files by datetime
#ds = ds.sel(time=slice("2026-02-10","2025-04-15")) # Sort files by datetime

plt.figure()
ax = WindroseAxes.from_ax()
# ax.bar(ds.WindDir_D1_WVT, ds.WS_ms_Avg, bins=np.arange(0,15,2), normed=True, opening=0.8, edgecolor='white')
ax.bar(wind_dir, wind_speed, bins=np.arange(0,15,2), normed=True, opening=0.8, edgecolor='white')

ax.set_legend(title='Wind speed (m/s)', loc='lower right')

#
# plt.savefig('../../figures/' + year + '/WeatherStation/WindRose.png', dpi=600, bbox_inches='tight')
#

