'''
    Load and plot variables from Robert Way's weather station and
    ERA5, and compare with IMS weather station
'''

# Globals
exec(open('../globals.py').read()) # modules, year, pathroot

#
# Load in Robert Way station data
#

RW = xr.open_dataset(pathroot + '/data/Robert_Way/Postville.nc')
RW = RW.swap_dims({'row': 'time'}) # Make time a coordinate, not variable

#
# Load in ERA5 data
#

ERA5 = xr.open_dataset(pathroot + '/data/ERA5/IMS.nc')

# Wing magnitude and direction
ERA5['u10_mag'] = np.sqrt(ERA5.u10**2 + ERA5.v10**2)
ERA5['u10_dir'] = (np.arctan2(ERA5.u10, ERA5.v10)*180./np.pi + 180.) % 360. # Wind direction, adjusted to "Coming From" direction instead of "Going to" direction

# Relative Humidity calculation from Dew point and air temp
RH = 100*(np.exp((17.625*(ERA5.d2m-273.15))/(243.04+(ERA5.d2m-273.15)))/np.exp((17.625*(ERA5.t2m-273.15))/(243.04+(ERA5.t2m-273.15)))) # Relative humidity
ERA5['rh'] = RH

# Daily, for climatology calculation
ERA5_daily = ERA5.resample(valid_time='1D').mean()
ERA5_daily_datetime = [pd.Timestamp(ERA5_daily.valid_time.values[tt]).to_pydatetime() for tt in range(len(ERA5_daily.valid_time.values))]
ERA5_daily_time = [ERA5_daily_datetime[tt].toordinal() for tt in range(len(ERA5_daily_datetime))]
# CONSIDER BIAS CORRECTING ERA5 (mean, var) TO IMS

ERA5_clim_90 = IMS.climatology(ERA5_daily_time, ERA5_daily.t2m.values, climatologyPeriod=[1991,2020])
ERA5_clim_10 = IMS.climatology(ERA5_daily_time, ERA5_daily.t2m.values, pctile=10, climatologyPeriod=[1991,2020])

#
# Load in IMS weather station data
#

IMSW = xr.open_dataset(pathroot + '/data/' + year + '/WeatherStation/WeatherVars_SD.nc') # SD card data
resampled_data_vars = {var: IMSW[var].resample(time='1H').mean() for var in IMSW.data_vars}
IMSW_hourly = xr.Dataset(resampled_data_vars) # make xr dataset from resampled data
hours = IMSW_hourly.time.values # For plotting

#
# Compare stations
#

# Time series

RW_time = RW.time - np.timedelta64(4, 'h') # Convert AST to UTC

# CHECK TIME ZONE OFFSET

plt.figure(figsize=(12,11))

ax = plt.subplot(6,1,1)
plt.fill_between(ERA5_daily.valid_time, ERA5_clim_10['thresh'] - 273.15, ERA5_clim_90['thresh'] - 273.15, color='0.75')
plt.plot(ERA5_daily.valid_time, ERA5_clim_90['seas'] - 273.15, '--', color='0.25')
plt.plot(ERA5.valid_time, ERA5.t2m - 273.15, 'r-')
plt.plot(RW_time, RW.air_temp_avg, 'b-')
plt.plot(IMSW_hourly.time, IMSW_hourly.AirT_C_Avg, 'k-')
plt.xlim(IMSW_hourly.time[0], IMSW_hourly.time[-1])
ax.set_xticklabels([])
plt.ylabel(r'Air temp. ($^\circ$C)')
plt.legend(['ERA5 (10-90)', 'ERA5 Climatology', 'ERA5', 'NEGL', 'IMSW'], ncols=3)

ax = plt.subplot(6,1,2)
plt.plot(ERA5.valid_time, ERA5.u10_mag, 'r-')
plt.plot(RW_time, RW.wind_spd_avg, 'b-')
plt.plot(IMSW_hourly.time, IMSW_hourly.WS_ms_Avg, 'k-')
plt.xlim(IMSW_hourly.time[0], IMSW_hourly.time[-1])
plt.ylim(0, 20)
ax.set_xticklabels([])
plt.ylabel('Wind speed (m/s)')
plt.legend(['ERA5', 'NEGL', 'IMSW'])

ax = plt.subplot(6,1,3)
plt.plot(ERA5.valid_time, ERA5.rh, 'r-')
plt.plot(RW_time, RW.rel_humidity, 'b-')
plt.plot(IMSW_hourly.time, IMSW_hourly.RH, 'k-')
plt.xlim(IMSW_hourly.time[0], IMSW_hourly.time[-1])
ax.set_xticklabels([])
plt.ylabel('Relative humid. (%)')
plt.legend(['ERA5', 'NEGL', 'IMSW'])

ax = plt.subplot(6,1,4)
plt.plot(ERA5.valid_time, 0.01*ERA5.msl, 'r-')
plt.plot(RW_time, RW.air_pressure_avg_sea_level, 'b-')
plt.plot(IMSW_hourly.time, IMSW_hourly.BP_mbar_Avg, 'k-')
plt.xlim(IMSW_hourly.time[0], IMSW_hourly.time[-1])
ax.set_xticklabels([])
plt.ylabel('MSLP (mbar)')
plt.legend(['ERA5', 'NEGL', 'IMSW'])
plt.ylim(IMSW_hourly.BP_mbar_Avg.min(), IMSW_hourly.BP_mbar_Avg.max())

ax = plt.subplot(6,1,5)
plt.plot(ERA5.valid_time, ERA5.ssrd/(60*60), 'r-') # Convert from J in 1 hour to W
plt.plot(RW_time, RW.pyr_solar, 'b-')
plt.plot(IMSW_hourly.time, IMSW_hourly.SWUpper_Avg, 'k-')
plt.xlim(IMSW_hourly.time[0], IMSW_hourly.time[-1])
ax.set_xticklabels([])
plt.ylabel(r'SWR (W/m$^2$)')
plt.legend(['ERA5', 'NEGL', 'IMSW'])

ax = plt.subplot(6,1,6)
plt.plot(ERA5.valid_time, ERA5.strd/(60*60), 'r-') # Convert from J in 1 hour to W
plt.plot(IMSW_hourly.time, IMSW_hourly.LWUpper_Avg, 'k-')
plt.xlim(IMSW_hourly.time[0], IMSW_hourly.time[-1])
plt.ylabel(r'LWR (W/m$^2$)')
plt.legend(['ERA5', 'IMSW'])

plt.tight_layout()

plt.savefig('../../figures/' + year + '/WeatherStation/Compare_IMS_NEGL_ERA5.png', dpi=600, bbox_inches='tight')

# Wind Rose

# Wind roses
N = 3 # Number of subplots (IMS, RW, ERA5)
# Determine axes locations for windrose plots
rect = {}
plt.figure()
for i in range(N):
    ax = plt.subplot(1,N,i+1)
    rect[i] = ax.get_position()
plt.close()
# Create windrose plots
fig = plt.figure(figsize=(15,5))
# IMS
wa = WindroseAxes(fig, rect[0])
ax = fig.add_axes(wa)
wa.bar(IMSW_hourly.WindDir, IMSW_hourly.WS_ms_Avg, bins=np.arange(0,15,2), normed=True, opening=0.8, edgecolor='white')
ax.set_legend(title='Wind speed (m/s)', loc='lower right')
wa.set_title('IMSW')
# RW
wa = WindroseAxes(fig, rect[1])
ax = fig.add_axes(wa)
wa.bar(RW.wind_dir_avg.sel(time=slice(IMSW_hourly.time[0], IMSW_hourly.time[-1])), RW.wind_spd_avg.sel(time=slice(IMSW_hourly.time[0], IMSW_hourly.time[-1])), bins=np.arange(0,15,2), normed=True, opening=0.8, edgecolor='white')
ax.set_legend(title='Wind speed (m/s)', loc='lower right')
wa.set_title('NEGL')
# ERA5
wa = WindroseAxes(fig, rect[2])
ax = fig.add_axes(wa)
wa.bar(ERA5.u10_dir.sel(valid_time=slice(IMSW.time[0], IMSW.time[-1])), ERA5.u10_mag.sel(valid_time=slice(IMSW.time[0], IMSW.time[-1])), bins=np.arange(0,15,2), normed=True, opening=0.8, edgecolor='white')
ax.set_legend(title='Wind speed (m/s)', loc='lower right')
wa.set_title('ERA5')

plt.savefig('../../figures/' + year + '/WeatherStation/WindRose_IMS_NEGL_ERA5.png', dpi=600, bbox_inches='tight')

# Precipitation from Robert's station

plt.figure()
plt.clf()
plt.plot(ERA5.valid_time, ERA5.tp*1000., 'r-') # Hourly precip m -> mm
plt.plot(RW_time, RW.precip_tb, 'b-')
#plt.plot(RW_time, RW.rain)
plt.plot(RW_time, RW.snow, 'k-')
plt.xlim(IMSW_hourly.time[0], IMSW_hourly.time[-1])
plt.legend(['ERA5 precip', 'NEGL precip', 'NEGL snow'])

plt.savefig('../../figures/' + year + '/WeatherStation/Compare_RWay_ERA5_Precip.png', dpi=600, bbox_inches='tight')

plt.clf()
plt.plot(RW_time, RW.snow_depth, 'b-')
plt.xlim(IMSW_hourly.time[0], IMSW_hourly.time[-1])

plt.savefig('../../figures/' + year + '/WeatherStation/Compare_RWay_ERA5_SnowDepth.png', dpi=600, bbox_inches='tight')

