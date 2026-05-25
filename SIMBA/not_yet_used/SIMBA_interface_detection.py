
'''
Detect SIMBA interfaces - first run the load_SIMBA.py script to load the heating rate data
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

# Load temperature data
with open('./SIMBA/da_temp_z.pickle','rb') as f:
    da_temp = pickle.load(f)


# Load the weekly snow time series
weekly_ice = xr.open_dataset('SiteVisits/weekly_ice_2024.nc')


# da_temp = da_temp.sel(time=slice(t1,t2))

z = da_temp.z

########### Thermal proxy ratios

T_0_30 = da_del0/da_del1 # T @ 0s / T @ 30 s
T_30_120 = da_del1/da_del4
T_0_120 = da_del0/da_del4

offset = 176 

####---------------------  For snow-ice interface - use HT30/HT120


# Only look at nodes 0-100 (take out ocean)
T_30_120_icesnow = T_30_120.sel(node=slice(0,100))
T_30_120_grad = T_30_120_icesnow.differentiate('node') 

# Take the position of the max gradient value at each time step
snow_ice = T_30_120_grad.argmax('node') + 1
# plot result on top of the contour plot
# snow_ice.plot(marker='o')

# Manual fixing
snow_ice[:30] = snow_ice[0]
snow_ice[-9] = snow_ice[-10] # random dip 
# snow_ice[-18] = snow_ice[-17]
# snow_ice[-19] = snow_ice[-20]


# interpolate to match length of regular temperature array, then smoooth using 7-day running mean
snow_ice_m = (-snow_ice*node_spacing + offset)/100 # convert to m from node 
# Shift everything up by one node - it should start with snow-ice = 0. Probably a menifest of the gradient detection
snow_ice_m = snow_ice_m.where(snow_ice_m > 0, 0)

# Check
fig = plt.figure(figsize=(18,8),facecolor='white')
ax = fig.add_subplot(111)
# im = plt.contourf(hours_temp, z, da_temp.T, cmap=cmocean.cm.thermal)#,levels=[-10,-5,-2,-1.8,-1.6,-1.4,-1.2,-1,-0.8,-0.6,-0.4,-0.2,0])
im = plt.pcolormesh(time_del, z, T_30_120.T, cmap='jet')
cbar = plt.colorbar(pad=0.02)
cbar.set_label(label='Thermal proxy (HT30/HT120)',fontsize=fontsize)
plt.plot(time_del, snow_ice_m,'k.-')

im = plt.pcolormesh(da_temp.time, z, da_temp.T, cmap='RdBu_r')


# Diagnose individual profiles

t = '2024-04-15'
# plt.figure()
da_temp.sel(time=t)[1].plot()
# bb = snow_air_z.sel(time=t).values
cc = snow_ice_m.sel(time=t).values
# plt.axvline(bb)
plt.axvline(cc,c='r')



snow_ice_m.loc["2024-03-27"] = 0.38
snow_ice_m.loc["2024-03-30"] = 0.38
snow_ice_m.loc["2024-03-31"] = 0.38
snow_ice_m.loc["2024-04-01"] = 0.38
snow_ice_m.loc["2024-04-02"] = 0.38
snow_ice_m.loc["2024-04-03"] = 0.38
snow_ice_m.loc["2024-04-04"] = 0.38
snow_ice_m.loc["2024-04-05"] = 0.38
snow_ice_m.loc["2024-04-06"] = 0.38
snow_ice_m.loc["2024-04-07"] = 0.38
snow_ice_m.loc["2024-04-08"] = 0.38
snow_ice_m.loc["2024-04-09"] = 0.38
snow_ice_m.loc["2024-04-10"] = 0.38
snow_ice_m.loc["2024-04-11"] = 0.38
snow_ice_m.loc["2024-04-12"] = 0.36
snow_ice_m.loc["2024-04-13"] = 0.34
snow_ice_m.loc["2024-04-14"] = 0.32
snow_ice_m.loc["2024-04-15"] = 0.28

# Make time indices consistent with others
snow_ice_m = snow_ice_m.resample(time='1D').mean() 

# Interpolate and smooth for plotting

snow_ice_6h = snow_ice_m.interp(time=da_temp.time,method='linear')
# snow_ice_smooth = snow_ice_6h.rolling(time=4*7,center='True',min_periods=4).mean() #NOTE: by setting min_periods=1 introduces boundary effects, but fills edges
snow_ice_smooth = snow_ice_6h.rolling(time=4,center='True').mean()


# Fill in values at the edges. Start from where they intersect. For the end, this is April 10
fill_vals = snow_ice_6h.sel(time=slice('2024-04-10',None))

tt = snow_ice_smooth.sel(time=slice('2024-04-10',None)).time.values
snow_ice_smooth.data[snow_ice_smooth.time.isin(tt)] = fill_vals

# Fill early values with 0
first_notnan = np.where(~np.isnan(snow_ice_smooth))[0][0]
snow_ice_smooth[:100] = snow_ice_smooth[:100].fillna(snow_ice_smooth[first_notnan])


####--------------------- For ice-water - use HT0/HT30


T_0_30_icewater = T_0_30.sel(node=slice(80,125))
T_0_30_grad = T_0_30_icewater.differentiate('node')
# Zooom in on ice-water interface
# im = plt.pcolormesh(time_del,T_0_30_grad.node, T_0_30_grad.T,cmap='RdBu_r')
# plt.clim(-0.2,0.2)

def last_nonzero(arr, axis, invalid_val=np.nan):
    mask = arr!=0
    val = arr.shape[axis] - np.flip(mask, axis=axis).argmax(axis=axis) - 1
    return xr.where(mask.any(axis=axis), val, invalid_val)

# First instance where the gradient > 0.2, starting from the bottom
max_grads = T_0_30_grad.where(T_0_30_grad > 0.1, other=0)
# (ice_water!=0).argmax(axis=0) # first instance
ice_water = last_nonzero(max_grads,axis=1) + 80 # offset node 80 from slicing


# Check
fig = plt.figure(figsize=(18,8),facecolor='white')
ax = fig.add_subplot(111)
im = plt.pcolormesh(time_del, z, T_0_30.T,cmap='RdBu_r')
plt.colorbar()
plt.clim(-2,0)
plt.plot(time_del,(-ice_water*2 + offset)/100,'ro')
plt.legend(['Ice-water'])
# plt.savefig('figures/SIMBA_temp_interfaces.png',dpi=300)

## Some manual filtering

# hump at Feb 28 - ice could not have grown 4 cm in 6 hours. At most one node (2cm) every 6h
tt = ice_water.sel(time=slice('2024-02-27','2024-02-28')).time.values
tt2 = ice_water.sel(time=('2024-03-11')).time.values
tt3 = ice_water.sel(time=('2024-02-22')).time.values

ice_water[ice_water.time.isin(tt)] = 117
ice_water[ice_water.time.isin(tt2)] = 118
ice_water[ice_water.time.isin(tt3)] = 116


#### Smooth interface 

# Ice bottom relative to z=0
ice_water_m = (-ice_water*node_spacing + offset)/100
# ice_water_smooth = ice_water_6h.rolling(time=4*7,center='True').mean()

with open('./SIMBA/ice_water_m.pickle','wb') as f:
    pickle.dump(ice_water_m, f)


######## Smooth with runnnig mean - TWICE
ice_water_roll = ice_water_m.rolling(time=5,center='True').mean()
ice_water_roll_ = ice_water_roll.rolling(time=5,center='True').mean()
# interp to match 6H length
ice_water_smooth = ice_water_roll_.interp(time=da_temp.time,method='linear')


# We know that the last few days are the same, so fill in the values that were dropped from the rolling average 
ice_water_smooth[100:] = ice_water_smooth[100:].fillna(-0.62)
# Fill in the early part (from Jan. 26)
ice_water_smooth[14] = ice_water_m[3]+0.015 #add some offset, doing this by eye
ice_water_smooth[14:20] = ice_water_smooth[14:20].interpolate_na(dim='time')



plt.figure(figsize=(8,5),facecolor='white')
plt.plot(ice_water_m.time,ice_water_m,'k.-')
# plt.plot(x_smooth,spl,'r-')
# plt.plot(ice_water_m.time,ice_water_roll,'m-')
plt.plot(ice_water_smooth.time,ice_water_smooth,'m-')
plt.legend(['Before smoothing','After smoothing and filling ends'])
plt.ylabel('z [m]',fontsize=fontsize)
plt.xlabel('Time',fontsize=fontsize)
plt.title('Ice-ocean interface',fontsize=fontsize+2)
#
# plt.savefig('figures/SIMBA/ice-ocean_smoothing_5day.png',dpi=400,bbox_inches='tight')
#




####---------------------  SNOW-AIR INTERFACE : Nov 14 updates -----------

# Only grab interfaces from the nighttime profiles, which are the smoothest
# So we only get ONE interface location per day 
da_temp_night = da_temp.sel(time=da_temp.time.dt.hour.isin([3,1,11,10,0]))

## Manually select some dates where profile look better at a different hour
# Drop the weird dates first
dropped = da_temp_night.drop_sel(time=['2024-02-15T03:00:16.000000000',
										'2024-02-18T03:00:16.000000000',
										'2024-02-19T03:00:16.000000000',
										'2024-03-03T03:00:16.000000000'])
# replace weird dates with good hours
da_temp_night = xr.concat([dropped, da_temp.loc[dict(time=['2024-02-15T09:00:16.000000000',
															'2024-02-18T09:00:16.000000000',
															'2024-02-19T09:00:16.000000000',
															'2024-03-03T09:00:16.000000000'])]],dim='time').sortby('time')


T_snowair = da_temp_night.sel(z=slice(1,0))

## Call the first deviation from the air temp average the snow interface
# Calculate the above-snow air temp average

# Tair_top = da_temp_night.sel(z=slice(1.5,1))
# Tair_mean = Tair_top.mean('z')
# ans = diff.where(abs(diff) > 5*Tair_top.std('z'), other=0)
# snow_air = (ans!=0).argmax(axis=1)
# snow_air_z = T_snowair.z[snow_air]
# # snow-air_z is already daily, but resample and average to fix the timestamps
# snow_air_z = snow_air_z.resample(time='1D').mean('time')


Tair_mean = T_snowair.sel(z=slice(1.4,1)).mean('z')
diff = T_snowair - Tair_mean
# snow_air = diff.where(diff > 0.5, other=0) # where the temp 

ans = diff.where(abs(diff) > 0.7, other=0)
snow_air = (ans!=0).argmax(axis=1)

snow_air_z = T_snowair.z[snow_air]
# snow-air_z is already daily, but resample and average to fix the timestamps
snow_air_z = snow_air_z.resample(time='1D').mean('time')
snow_ice_z_ = snow_ice_m.resample(time='1D').mean('time') # same for snow-ice

# Manually fix dates

Hsnow = weekly_ice['Hsnow']
Hsnow_interp = Hsnow.interp(time=da_temp.time,method='linear')

# Dates to adjust manually - These periods should match the observed snow depths, minus a gap
tt = snow_air_z.sel(time='2024-02-04').time.values
tt2 = snow_air_z.sel(time='2024-02-14').time.values
tt3 = snow_air_z.sel(time=slice('2024-02-26','2024-02-27')).time.values
tt4 = snow_air_z.sel(time=slice('2024-03-11','2024-03-15')).time.values
# tt5 = snow_air_z.sel(time=slice('2024-03-23',None)).time.values # replace with weekly obs, interpolated
tt5 = snow_air_z.sel(time=slice('2024-04-07','2024-04-15')).time.values 


# Replace these with the observations
snow_air_z.data[snow_air_z.time.isin(tt)] = snow_air_z.sel(time='2024-02-03')
snow_air_z.data[snow_air_z.time.isin(tt2)] = Hsnow.sel(time=tt2,method='nearest').values
snow_air_z.data[snow_air_z.time.isin(tt3)] = Hsnow.sel(time='2024-02-26',method='nearest').values
snow_air_z.data[snow_air_z.time.isin(tt4)] = Hsnow.sel(time='2024-3-12',method='nearest').values
# snow_air_z.data[snow_air_z.time.isin(tt5)] = Hsnow_interp.sel(time=tt5).values
snow_air_z.data[snow_air_z.time.isin(tt5)] = snow_ice_m.data[snow_ice_m.time.isin(tt5)] # no snow

# NOV. 25 - UPDATE - DON'T SMOOTH/INTERPOLATE. The temperature profiles are really good for snow/air so smoothing change the position of the real interface
# snow_air_6h = snow_air_z.interp(time=da_temp.time,method='linear')
# snow_air_z_smooth = snow_air_6h.rolling(time=3,center='True').mean()
# snow_air_z_smooth = snow_air_z

# # Fill the edges - zoom in on where the smoothed and unsmoothed line start to diverge
# tt6 = snow_air_z_smooth.sel(time=slice('2024-04-12',None)).time.values # replace with snow_ice interface, no snow
# snow_air_z_smooth.data[snow_air_z_smooth.time.isin(tt6)] = Hsnow_interp.sel(time=tt6).values


### MANUAL FIXING

plt.figure()
t = '2024-03-13'
da_temp.sel(time=t)[0].plot()
bb = snow_air_z.sel(time=t).values
cc = snow_ice_m.sel(time=t).values
plt.axvline(bb)
plt.axvline(cc,c='r')

snow_air_z.loc["2024-02-14"] = 0.2
snow_air_z.loc["2024-02-20"] = 0.85
snow_air_z.loc["2024-02-20"] = 0.9
snow_air_z.loc["2024-02-21"] = 0.9
snow_air_z.loc["2024-02-22"] = 0.8
snow_air_z.loc["2024-02-26"] = 0.7
snow_air_z.loc["2024-02-27"] = 0.79
snow_air_z.loc["2024-02-28"] = 0.64
snow_air_z.loc["2024-02-29"] = 0.8
snow_air_z.loc["2024-03-10"] = 0.42
snow_air_z.loc["2024-03-11"] = 0.45
snow_air_z.loc["2024-03-12"] = 0.39
snow_air_z.loc["2024-03-23"] = 0.7
snow_air_z.loc["2024-03-29"] = 0.48
snow_air_z.loc["2024-03-30"] = 0.46
snow_air_z.loc["2024-03-31"] = 0.46
snow_air_z.loc["2024-04-01"] = 0.46
snow_air_z.loc["2024-04-03"] = 0.46
snow_air_z.loc["2024-04-04"] = 0.46
snow_air_z.loc["2024-04-05"] = 0.46
snow_air_z.loc["2024-04-06"] = 0.46
snow_air_z.loc["2024-04-07"] = 0.44
# snow_air_z.loc["2024-04-09"] = 0.46
# snow_air_z.loc["2024-04-10"] = 0.46
# snow_air_z.loc["2024-04-11"] = 0.44
# snow_air_z.loc["2024-04-12"] = 0.42


# snow_air_z.loc["2024-04-03":"2024-04-04"] = 0.58
# snow_air_z.loc["2024-04-01":"2024-04-02"] = 0.5
# snow_air_z.loc["2024-04-14"] = 0.5

### Snow air cannot ever be less than snow ice! 
snow_ice_daily = snow_ice.resample(time='1D').mean('time')
# snow_air_z = xr.where(snow_air_z<snow_ice_z_,snow_ice_z_+0.02,snow_air_z) 




####

# Plot to check
plt.figure(figsize=(10,5),facecolor='white')
ax = plt.subplot(111)
# im = plt.contourf(hours_temp, z, da_temp.T, cmap=cmocean.cm.thermal)#,levels=[-10,-5,-2,-1.8,-1.6,-1.4,-1.2,-1,-0.8,-0.6,-0.4,-0.2,0])
im = plt.pcolormesh(da_temp.time.values, da_temp.z, da_temp.T, cmap=cmocean.cm.thermal)
plt.clim(-15, 0) # colorbar limits

plt.plot(snow_air_z.time, snow_air_z,'k.-',label='Detection algorithm')

plt.plot(weekly_ice.time, Hsnow,'co--',label='Weekly observations - dry snow')
# plt.plot(da_temp.time, snow_air_z_smooth_1,'r-',label='First smoothing (before adjusting)')
# plt.plot(da_temp.time, snow_air_6h,'g.-',label='Adjusted to obs before smoothing')
# plt.plot(da_temp.time, snow_air_z_smooth,'k-',label='After smoothing')
plt.legend()
plt.colorbar(label='Temperature [deg. C]')
plt.ylabel('z [m]')
plt.ylim([-1,None])
plt.xticks(rotation=15)
plt.xlim(['2024-01-26','2024-04-15'])
#
# plt.savefig('figures/SIMBA/snow_ice.png',dpi=300,bbox_inches='tight')
#




####---------------------  For snow air, use regular temp plot and see when air temp changes, since air temp is quite uniform



# # Load the weekly snow time series, and adjust the values to represent FRESH snow (not snow stakes)
# weekly_ice = xr.open_dataset('SiteVisits/weekly_ice.nc')

# # Hsnow is array of z position of the DRY snow, so add the observation to the snow ice interface
# Hsnow = weekly_ice.Hsnow 
# Hsnow = xr.where(Hsnow.time==Hsnow.sel(time='2024-02-27').time,0.61 + snow_ice_m.sel(time='2024-02-27').values,Hsnow) # Feb 27: 61 cm of snow
# Hsnow = xr.where(Hsnow.time==Hsnow.sel(time='2024-03-05').time,0.39 + snow_ice_m.sel(time='2024-03-05').values,Hsnow) # March 5: 39 cm of snow
# Hsnow = xr.where(Hsnow.time==Hsnow.sel(time='2024-03-12').time,0.33 + snow_ice_m.sel(time='2024-03-12').values,Hsnow) # March 12: 33 cm of snow
# Hsnow = xr.where(Hsnow.time==Hsnow.sel(time='2024-03-26').time,Hsnow.sel(time='2024-03-26').values - 0.16, Hsnow) # March 26: 16cm of total slob on top of ice (under the snow)
# Hsnow = xr.where(Hsnow.time==Hsnow.sel(time='2024-04-02').time,0.01 + snow_ice_m.sel(time='2024-04-02').values,Hsnow) # April 2: 22.5cm of slob on top of ice. Very little snow now. 
# Hsnow = xr.where(Hsnow.time==Hsnow.sel(time='2024-04-09').time,0 + snow_ice_m.sel(time='2024-04-09').values,Hsnow) # April 9: 0 cm of snow during CTD transect
# Hsnow = xr.where(Hsnow.time==Hsnow.sel(time='2024-04-16').time,0 + snow_ice_m.sel(time='2024-04-15').values,Hsnow) # April 15: 0 cm of snow during CTD transect


# T_snowair = da_temp.sel(z=slice(1.4,0))

# ## Call the first deviation from the air temp average the snow interface
# # Calculate the above-snow air temp average

# Tair_mean = T_snowair.sel(z=slice(1.4,1)).mean('z')
# diff = T_snowair - Tair_mean
# # snow_air = diff.where(diff > 0.5, other=0) # where the temp 

# ans = diff.where(diff > 0.5, other=0)
# snow_air = (ans!=0).argmax(axis=1)

# snow_air_z = T_snowair.z[snow_air]

# # smooth it out: (1) the first few points look good. If point n+1 > x*n, then set the value at n+1 to the value at n
# for i in range(0,len(snow_air_z.time)-1):
# 	# if snow_air_z[i+1] > snow_air_z[i]+0.1*3: 
# 	if np.abs(snow_air_z[i+1] - snow_air_z[i]) > 0.2: # assume no more than 20 cm of snow diff in one 6=h period
# 		# print(i, snow_air_z.data[i-1], snow_air_z.data[i],snow_air_z.data[i+1])
# 		snow_air_z.data[i+1] = snow_air_z[i]

# # Smooth out with rolling mean - 2 day instead of 7 day since snow is more variable than ice
# snow_air_z_smooth_1 = snow_air_z.rolling(time=2,center='True').mean()

# ### MANUALLY ADJUST 
# gap = 0.05 # between true snow surface and snow touching highest sensor

# # Dates to adjust manually - These periods should match the observed snow depths, minus a gap
# tt = snow_air_z.sel(time=slice('2024-03-25','2024-03-30')).time.values
# tt2 = snow_air_z.sel(time=slice('2024-03-30',None)).time.values 
# tt3 = snow_air_z.sel(time=slice('2024-03-09','2024-03-15')).time.values 
# tt4 = snow_air_z.sel(time=slice('2024-02-01','2024-02-08')).time.values 
# tt5 = snow_air_z.sel(time=slice('2024-03-15','2024-03-21')).time.values 
# tt6 = snow_air_z.sel(time=slice('2024-02-25','2024-03-01')).time.values 
# tt7 = snow_air_z.sel(time=slice('2024-03-22','2024-03-24')).time.values 

# # Replace these with the observations
# snow_air_z.data[snow_air_z.time.isin(tt)] = Hsnow.sel(time='2024-03-26').values - gap
# snow_air_z.data[snow_air_z.time.isin(tt2)] = snow_ice_smooth.data[snow_ice_smooth.time.isin(tt2)] # no snow
# snow_air_z.data[snow_air_z.time.isin(tt3)] = Hsnow.sel(time='2024-03-12').values - gap
# snow_air_z.data[snow_air_z.time.isin(tt4)] = Hsnow.sel(time='2024-02-07').values - gap
# snow_air_z.data[snow_air_z.time.isin(tt5)] = Hsnow.sel(time='2024-03-19').values - gap
# snow_air_z.data[snow_air_z.time.isin(tt6)] = Hsnow.sel(time='2024-02-27').values - gap
# snow_air_z.data[snow_air_z.time.isin(tt7)] = Hsnow.sel(time='2024-03-26').values - gap

# # Try overlapping with all snow stake measurements (+ offset), then smooth 
# # times_valid = snow_air_z.sel(time=weekly_dates,method='nearest').time
# # for t, d in zip(times_valid, weekly_Hsnow_cm/100):
# #     snow_air_z.data[snow_air_z.time==t] = d - offset 

#  # Smooth out with rolling mean
# snow_air_z_smooth_2 = snow_air_z.rolling(time=4*3,center='True').mean()


# # Plot to check

# plt.figure(figsize=(10,5),facecolor='white')
# ax = plt.subplot(111)
# # im = plt.contourf(hours_temp, z, da_temp.T, cmap=cmocean.cm.thermal)#,levels=[-10,-5,-2,-1.8,-1.6,-1.4,-1.2,-1,-0.8,-0.6,-0.4,-0.2,0])
# im = plt.pcolormesh(da_temp.time, z, da_temp.T, cmap=cmocean.cm.thermal)
# plt.clim(-15, 0) # colorbar limits

# # plt.plot(da_temp.time, snow_air_z,'m.-')

# plt.plot(weekly_ice.time, Hsnow,'co--',label='Weekly observations - dry snow')
# # plt.plot(da_temp.time, snow_air_z_smooth_1,'r-',label='First smoothing (before adjusting)')
# plt.plot(da_temp.time, snow_air_z,'g.-',label='Adjusted to obs before smoothing')
# plt.plot(da_temp.time, snow_air_z_smooth_2,'k.-',label='After smoothing')
# plt.legend()
# plt.colorbar(label='Temperature [deg. C]')
# plt.ylabel('z [m]')
# plt.ylim([-1,None])

# plt.savefig('figures/SIMBA/snow_ice.png',dpi=300,bbox_inches='tight')




#### ----------------- Save ice temperature and thickness into pickle files -----------------



# Subset the dates 
t1 = '2024-01-26'
t2 = '2024-04-15'
# temp_ice = temp_ice.sel(time=slice(t1,t2))
ice_water_smooth = ice_water_smooth.sel(time=slice(t1,t2))
H_ice = H_ice.sel(time=slice(t1,t2))
# snow_air_smooth = snow_air_z_smooth.sel(time=slice(t1,t2))
snow_air_z_ = snow_air_z.sel(time=slice(t1,t2))
snow_ice_smooth_ = snow_ice_smooth.sel(time=slice(t1,t2))
snow_ice_m_ = snow_ice_m.sel(time=slice(t1,t2))


da_temp_sub = da_temp.sel(time=slice(t1,t2))

# extract and save ice temperature
temp_ice = da_temp_sub.where((da_temp_sub.z < snow_ice_smooth) & (da_temp_sub.z > ice_water_smooth),other=np.nan)

# Snow thickness
H_snow = snow_air_z_ - snow_ice_m
H_snow = H_snow.where(H_snow > 0.01,0)
# Ice thickness
H_ice = (ice_water_smooth - snow_ice_smooth)




import pickle
with open('./SIMBA/temp_ice_z.pickle','wb') as f:
	pickle.dump(temp_ice, f)


# ICE THICKNESS
with open('./SIMBA/H_SIMBA.pickle','wb') as f:
	pickle.dump(H_ice, f)

# ICE BOTTOM
with open('./SIMBA/H_bottom.pickle','wb') as f:
	pickle.dump(ice_water_smooth, f)

# SNOW TOP
with open('./SIMBA/snow-air.pickle','wb') as f:
	pickle.dump(snow_air_z_, f)

# SNOW THICKNESS
with open('./SIMBA/Hsnow_SIMBA.pickle','wb') as f:
	pickle.dump(H_snow, f)

# SNOW ICE INTERFACE - SMOOTHED
with open('./SIMBA/snow-ice-smoothed.pickle','wb') as f:
	pickle.dump(snow_ice_smooth_, f)

# SNOW ICE INTERFACE 
with open('./SIMBA/snow-ice.pickle','wb') as f:
	pickle.dump(snow_ice_m_, f)

####------------ Plot all interfaces on the tempertaure contour plot------------

# Load temperature data
with open('./SIMBA/da_temp_z.pickle','rb') as f:
    da_temp = pd.read_pickle(f)

# SNOW-AIR INTERFACE
with open('./SIMBA/snow-air.pickle','rb') as f:
    snow_air = pickle.load(f)

# SNOW ICE INTERFACE
with open('./SIMBA/snow-ice-smoothed.pickle','rb') as f:
    snow_ice_smoothed = pd.read_pickle(f)

# ICE-WATER INTERFACE
with open('./SIMBA/H_bottom.pickle','rb') as f:
	H_bottom = pickle.load(f)


time_temp = da_temp_sub.time 

plt.figure(figsize=(10,5),facecolor='white')
ax = plt.subplot(111)
# im = plt.contourf(hours_temp, z, da_temp.T, cmap=cmocean.cm.thermal)#,levels=[-10,-5,-2,-1.8,-1.6,-1.4,-1.2,-1,-0.8,-0.6,-0.4,-0.2,0])
im = plt.pcolormesh(time_temp.values, da_temp.z, da_temp_sub.T, cmap='rainbow',alpha=0.8)

plt.clim(-15, 0) # colorbar limits
plt.ylim(-3, 1.8)
cbar = plt.colorbar(pad=0.02)
cbar.set_label(label='T [deg. C]',
                                size=fontsize)
cbar.ax.tick_params(labelsize=fontsize)

plt.ylabel('z [m]',fontsize=fontsize)
plt.xlabel('Time',fontsize=fontsize)
ax.tick_params(axis='both',labelsize=fontsize)

# Interfaces
# plt.plot(snow_air.time,snow_air,'w-',label='Air-snow')
snow_air.plot(c='w',label='Air-snow')
# plt.plot(time_temp,snow_ice,'k-',label='Snow-ice')
# snow_ice.plot(c='k',label='Snow-ice')
snow_ice_smoothed.plot(c='k',linestyle='-',label='Snow-ice')


plt.plot(time_temp,H_bottom,'b-',label='Ice-water')
plt.legend(loc='lower left')
plt.xlim(['2024-01-26','2024-04-15'])
plt.xticks(rotation=15)
#
# plt.savefig('figures/SIMBA/smoothed_interfaces_jet.png',dpi=500)
#


# Plot the difference in smoothing

plt.figure(figsize=(8,6))
plt.subplot(211)
snow_ice_m.plot(color='c',linestyle='--',alpha=0.5,label='Original')
snow_ice_smooth.plot(color='c',linestyle='-',label='Smoothed')
plt.xticks([])
plt.xlabel('')
plt.ylabel('z [m]')
plt.legend()
plt.suptitle('Effect of smoothing interfaces (7-day mean)')
plt.title('Snow-ice interface')
plt.xlim(['2024-01-26','2024-04-15'])
plt.subplot(212)
ice_water_m.plot(color='k',linestyle='--',alpha=0.5)
ice_water_smooth.plot(color='k',linestyle='-')
plt.xlim(['2024-01-26','2024-04-15'])
plt.ylim([-0.65,-0.34])
plt.ylabel('z [m]')
plt.title('Ice-ocean interface')

#
# plt.savefig('figures/SIMBA/smoothing_effects.png',dpi=300)
#














'''Detect interfaces using Gough et al. 2012 method - BAD!'''

from scipy import stats

# 1. Slice the vertical to "zoom in" in the ice and upper ocean

# 2. Make a "fake" temperature profile using linear regression over groups of 4 nodes starting from the bottom. 

# 3. At each time step, calculate the mean ocean temperature from averaging the "ocean" thermistors 

nodes_ocean = 
T_ocean = 

# 4. Find where the "fake" profile intersects with the real profile within +/-0.01m, and save that node as the ice bottom 


da_temp_cut = da_temp.isel(node=slice(20,230))
node_cut = da_temp_cut.node
node_r = np.flip(node)
da_temp_r = np.flip(da_temp_cut)

dTdz_slopes = xr.zeros_like(da_temp_cut)
node_slopes = xr.zeros_like(node)

for t in range(len(da_temp_r.time)):
	for i in range(len(node)-4):
		regressions = stats.linregress(node_r[i:i+4], da_temp_r.isel(time=t,node=slice(i,i+4)))
		slope = regressions[0]
		
		if slope <= -0.009: # deg. C/cm
			print(slope)
			dTdz_slopes[t,i] = regressions[0]
			node_slopes[i] = node_r[i+2]
			break

	# plt.plot(node[i],s,'o')






### Test one profile



# test_prof = T_0_120_r.isel(time=10)

test_prof = da_temp_r.isel(time=15)
node_r = np.flip(test_prof.node) 

dTdz_slope = xr.zeros_like(test_prof)
b = xr.zeros_like(test_prof)

# recons=xr.zeros_like(test_prof)
recons = np.array([])

for i in range(0,len(node_r)-4,4):
	regressions = stats.linregress(node_r[i:i+4], test_prof.isel(node=slice(i,i+4)))
	# slope = regressions[0]
	
	# if slope <= -0.009: # deg. C/cm
		# print(slope)
	dTdz_slope[i] = regressions[0]
	b[i] = regressions[1] # intercept
	recons = np.concatenate([recons,regressions[0]*np.arange(i,i+4) + regressions[1]])
		# node_slope = node_r[i+2]
		# break'

# plt.plot(T_0_120_r.node[:-4],recons)
plt.plot(test_prof.node[:-2],recons) # reconstructed temperature profile


# Plot them together

plt.figure()
test_prof.plot()

dTdz_slope_na = dTdz_slope.where(dTdz_slope!=0,np.nan)
(dTdz_slope_na*node+b).plot()



######### Try using thermal proxies and just rely on gradients


T_0_120_r = np.flip(T_0_120)
node_r = np.flip(T_0_120_r.node)

test_prof = T_0_120_r.isel(time=10)

dTdz_slope = xr.zeros_like(test_prof)
b = xr.zeros_like(test_prof)

for i in range(0,len(node_r)-4,4):
	regressions = stats.linregress(node_r[i:i+4], test_prof.isel(node=slice(i,i+4)))
	# slope = regressions[0]
	
	# if slope <= -0.009: # deg. C/cm
		# print(slope)
	dTdz_slope[i] = regressions[0]
	b[i] = regressions[1] # intercept
	# node_slope = node_r[i+2]







