'''

'''


import numpy as np 
import xarray as xr
import pickle
from functions import IMS_toolbox as IMS
import matplotlib.pyplot as plt 
import scipy
import tqdm
import datetime
import time
import pandas as pd
plt.ion()


# -------- Load data ------------------


# Load rain data from Robert Way's weather station


# filepath = '/home/mwang/data/postville_weather_2020-2024.csv'
filepath = './Weather/data/2024/postville_weather_2020-2024.csv'
file = pd.read_csv(filepath,low_memory=False)

# Shortcut to just loading rain data
rain_mm = IMS.load_Rway_station_data(file,'rain').sel(time=slice('2024-01-26','2024-04-15'))


# Weather station
ds_weather = xr.open_dataset('Weather/WeatherVars_CR1000X.nc')
T_a = ds_weather['AirT_C_Avg'].resample(time='1H').mean('time')

# SNOW THICKNESS
with open('./SIMBA/Hsnow_SIMBA.pickle','rb') as f:
    H_snow = pickle.load(f)

# ICE THICKNESS
with open('./SIMBA/H_SIMBA.pickle','rb') as f:
	H_ice = pickle.load(f)

# ICE-WATER INTERFACE
with open('./SIMBA/H_bottom.pickle','rb') as f:
	H_bottom = pickle.load(f)

# SNOW-AIR INTERFACE
with open('./SIMBA/snow-air.pickle','rb') as f:
    snow_air = pickle.load(f)

# Load temperature data
with open('./SIMBA/da_temp_z.pickle','rb') as f:
    da_temp = pickle.load(f)


# ---------Analyze stuff -----------------

# Timeseries of when rainfall != 0
rain_non0 = rain_mm.where(rain_mm>0,drop=True)



# -------- Plot stuff ------------------

# Rainfall, temp, snow depth

t = rain_mm.time.values

fig, ax = plt.subplots(figsize=(10,5))
# p1, = ax.plot(t,rain_mm,'k',label='Rainfall amount')
p1 = plt.bar(rain_non0.time.values,rain_non0,label='Rainfall amount')
# plt.axvspan(a, b, color='y', alpha=0.5, lw=0) # Rain duration
ax2 = ax.twinx()
p2, = ax2.plot(T_a.time,T_a,color='crimson',label='Air temperature')
ax3 = ax.twinx()
ax3.spines["right"].set_position(("axes", 1.1))
p3, = ax3.plot(H_snow.time,H_snow,'b',label='Dry snow depth')

tkw = dict(size=5, width=1.8)
ax.tick_params(axis='y', colors=p1.get_color(), **tkw)
ax2.tick_params(axis='y', colors=p2.get_color(), **tkw)
ax3.tick_params(axis='y', colors=p3.get_color(), **tkw)
# host.tick_params(axis='x', **tkw)

ax.set_ylabel('Rainfall [mm]')
ax2.set_ylabel('Air temperature [deg C]')
ax3.set_ylabel('Dry snow depth [m]')
plt.xlim([t[0],t[-1]])
# plt.savefig('figures/HeatBudget/rain_temp_snow.png',dpi=300,bbox_inches='tight')



# Bar plot of rainfall
plt.figure()
plt.bar(rain_non0.time.values,rain_non0)














