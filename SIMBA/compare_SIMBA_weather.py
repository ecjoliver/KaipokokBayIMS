'''
    Compare the SIMBA temeprature to the weather station air temperature - quality control
'''

# Some globals
exec(open('../globals.py').read()) # modules, year, pathroot
fontsize=12

# Load weather data
ds_weather = xr.open_dataset(pathroot + '/data/' + year + '/WeatherStation/WeatherVars_SD.nc')
ds_weather = ds_weather.resample(time="1H").mean('time')
weath_temp = ds_weather['AirT_C_Avg']

# Load SIMBA temperature data
ds = xr.open_dataset(pathroot + '/data/' + year + '/SIMBA/SIMBA_temp.nc')

# Subset SIMBA data to match weather station
#simba_temp = da_temp_.sel(time=slice('2024-01-26','2024-04-15'))
#simba_temp = da_temp_.sel(time=slice('2026-02-06','2026-04-15'))

# 2m air temperature
#simba_t2m = simba_temp.sel(z=1.4).resample(time='1D').mean('time')
simba_t2m = ds.sel(z=1.5).temp

plt.figure(figsize=(15,5),facecolor='white')
plt.clf()
plt.plot(weath_temp.time, weath_temp.data, 'r-')
plt.plot(simba_t2m.time, simba_t2m.data, 'k-')
#plt.plot(simba_t2m.time + np.timedelta64(94368, 'h'), simba_t2m.data)
plt.legend(['Weather Station','SIMBA'],fontsize=fontsize)
plt.title('Air temperature comparison',fontsize=fontsize)
plt.ylabel(r'Air temperature ($^\circ$C)',fontsize=fontsize)

# plt.savefig(pathroot + '/figures/' + year + '/SIMBA/SIMBA_compareWeatherStation.png', dpi=600, bbox_inches='tight')

