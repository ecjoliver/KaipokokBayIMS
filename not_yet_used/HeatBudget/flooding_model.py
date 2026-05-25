
'''
Ice growth model with flooding and snow-ice growth

Based on Mahoney et al. 2021

'''

import numpy as np 
import xarray as xr
import pickle
from functions import IMS_toolbox as IMS
import matplotlib.pyplot as plt 
import scipy
import tqdm
from datetime import datetime
import time
plt.ion()


# Weather station
ds_weather = xr.open_dataset('Weather/WeatherVars_CR1000X.nc')

# SNOW THICKNESS
# with open('./SIMBA/Hsnow_SIMBA.pickle','rb') as f:
#     H_snow = pickle.load(f)

# ICE THICKNESS
with open('./SIMBA/H_SIMBA.pickle','rb') as f:
	H_ice = pickle.load(f)

# ICE-WATER INTERFACE
with open('./SIMBA/H_bottom.pickle','rb') as f:
	H_bottom = pickle.load(f)

# SNOW-AIR INTERFACE
with open('./SIMBA/snow-air.pickle','rb') as f:
    H_snow = pickle.load(f)

# Load temperature data
with open('./SIMBA/da_temp_z.pickle','rb') as f:
    da_temp = pickle.load(f)

#---------Constants------------

# sea ice latent heat capacity
L_i = 330000 # J/kg - specific latent heat of fusion of sea ice, 330 kJ/kg (Mahoney paper is a typo)
rho_i = 910 #kg/m3 - sea ice density
rho_s = 330 #kg/m3 - snow density
rho_w = 1027 #kg/m3 - seawater density
# T_f = -1.5
T_f = -0.75 # Water temp right below the ice, based on SIMBA
k_i = 2.09 #W/m*K, Sea ice heat conductivity, (Pringle et al. 2006)
k_s = 0.3 #W/m*K, snow heat conductivity
vl = 0.65 # liquid volume fraction of flooded snow
df = 1 # Fractional flooded depth of negative freeboard

fontsize=12

#------Observations---------

# Observation period
# begT = np.datetime64('2024-01-26')
begT = np.datetime64('2024-01-26')
endT = np.datetime64('2024-04-15')


# Snow thickness, upsample to hourly
H_s_ = H_snow.sel(time=slice(begT,endT)).resample(time='1H').interpolate('linear')
# Interpolate the ends to fill nans
H_s_ = H_s_.interpolate_na(dim='time',method='nearest',fill_value="extrapolate")

# H_i_obs = np.abs(H_bottom)

# Assume surface temperature is at the air temperature
T_s_ = ds_weather['AirT_C_Avg'].sel(time=slice(H_s_.time[0].values,H_s_.time[-1].values)).resample(time='1H').mean('time')

# Surface temp
# T_s_ = da_temp.sel(z=snow_air,method='nearest').sel(time=slice(begT,endT)).resample(time='1H').interpolate('linear') # daily mean
# first value is nan, fill it with the second value
# T_s_[0] - T_s_[1]

#--------- Set up the variables--------

time_steps = len(T_s_)

H_i_ = xr.zeros_like(H_s_)
H_si_ = xr.zeros_like(H_s_)
fb_ = xr.zeros_like(H_s_)
H_sdry_ = xr.zeros_like(H_s_)
dH_i_ = xr.zeros_like(H_s_)
dH_si_ = xr.zeros_like(H_s_)

F_w = 0 #W/m2

#### Initial conditions

H_i_[0] = 0.39
H_si_[0] = 0
H_sdry_[0] = H_s_[0]

dt = 60*60 # 1 hour

fb_[0] = H_i_[0] - (rho_i*H_i_[0] + rho_s*H_s_[0])/rho_w

#--------- Model ------------

for t in tqdm.tqdm(range(1,time_steps)): 
	H_i = H_i_[t-1]
	H_s = H_s_[t-1]
	H_si = H_si_[t-1]
	H_sdry = H_sdry_[t-1]
	T_s = T_s_[t]
	fb = fb_[t-1]

	# If freeboard is negative, flooding
	if fb < 0:
		H_sdry = H_s + fb
		dH_si = -vl*(dt/(rho_i*L_i))*((H_si + H_sdry)/(H_si/k_i + H_sdry/k_s))*((T_s - T_f)/(H_si + H_sdry))
		T_s = T_f 
		# Ice cannot grow from the bottom, but can still melt if F_w is positive
		if F_w > 0:
			dH_i = -dt/(rho_i*L_i)*(0 + F_w)
		else: 
			dH_i = 0
		fb = 1/(1-vl*df)*((H_i+H_si) - (rho_i*(H_i+H_si) + rho_s*H_s)/rho_w)
	else: 
		H_sdry = H_s
		dH_si = 0 # no flooding layer development
		dH_i = -dt/(rho_i*L_i)*( ((H_i + H_si + H_s)/((H_i + H_si)/k_i + H_s/k_s))*((T_s - T_f)/((H_i + H_si) + H_s)) + F_w )
		# Calculate the freeboard
		fb = (H_i+H_si) - (rho_i*(H_i+H_si) + rho_s*H_s)/rho_w


	# Save outputs
	H_i_[t] = H_i + dH_i 
	H_si_[t] = H_si + dH_si
	fb_[t] = fb
	dH_i_[t] = dH_i
	dH_si_[t] = dH_si
	H_sdry_[t] = H_sdry


#----- Plot the results---------

t = H_s_.time.values

fig,axx = plt.subplots(nrows=2,sharex=True,figsize=(10,10), facecolor='w')


axx[0].plot(t,-H_i_,color='mediumblue')
hIce = axx[0].fill_between(t,-H_i_,0,color='mediumblue',alpha=0.2)

# axx[0].errorbar(x=mbs_snow.index,y=mbs_snow.Mean,yerr=mbs_snow.Std,color='gray',capsize=capsz,fmt='o')
# axx[0].plot(mbs_snow.Min,color='gray',linestyle='--')
# axx[0].plot(mbs_snow.Max,color='gray',linestyle='--')
axx[0].plot(t,H_sdry_+H_si_,color='gray')
hSnow = axx[0].fill_between(t,H_si_,H_sdry_+H_si_,color='gray',alpha=0.2)

axx[0].plot(t,H_si_,color='cornflowerblue')
hFlood = axx[0].fill_between(t,0,H_si_,color='cornflowerblue',alpha=0.2)
# hSlush = axx[0].fill_between(mbs_flood.index[5:],np.zeros(len(mbs_flood.index[5:])),np.zeros(len(mbs_flood.index[5:]))+[0,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015],color='midnightblue',alpha=0.5)

# axx[0].plot(mbs_ice.index,np.zeros(len(mbs_ice.index)),'k',linewidth=0.5)

axx[0].set_ylabel('Vertical distance [m]')
axx[0].set_title('Evolution of the Snow & Ice')

# l2 = axx[0].legend([hSnow,hFlood,hIce],['Dry Snow','Snow-Ice','Sea Ice'],bbox_to_anchor=(1.001,0.6),fontsize=fontsize-4)


#----- Plot observations on top ---------

# Ice bottom 
hObs, = axx[0].plot(H_bottom.time,H_bottom,'r--',label='Ice bottom')

# Add individual observations of SLOB bsaed on site visit datasheets
slob, = axx[0].plot(np.datetime64('2024-03-19').astype(datetime),0.05,'k^',label='Slob thickness')
axx[0].plot(np.datetime64('2024-03-26').astype(datetime),0.16,'k^')
axx[0].plot(np.datetime64('2024-04-02').astype(datetime),0.225,'k^')

# Add SIMBA derived snow-ice (total ice thickness minus the draft)
H_si_obs = -(H_ice - H_bottom)
hFloodObs, = axx[0].plot(H_si_obs.time,H_si_obs,'g--',label='Surface freezing (SIMBA)')

# rand, = axx[0].plot(H_bottom.time,H_bottom,'g-',label='bb')
l1 = axx[0].legend([hSnow,hFlood,hIce],['Dry Snow','Snow-Ice','Sea Ice'],bbox_to_anchor=(1.18,0.9),title=r'Model (F$_w$=0)')
l2 = axx[0].legend(handles=[hObs,slob,hFloodObs],bbox_to_anchor=(1.01,0.4),title='Observations')
axx[0].add_artist(l1)


# Load the weekly snow time series, and adjust the values to represent FRESH snow (not snow stakes)
weekly_ice = xr.open_dataset('SiteVisits/weekly_ice.nc')

# Observed freeboard
fb_obs = weekly_ice['Hice'] - weekly_ice['Waterlvl'] 

aa=axx[1].plot(t,fb_,'b-')
bb=axx[1].plot(fb_obs.time, fb_obs,'r^-')
axx[1].set_title('Freeboard comparisons')
l3 = axx[1].legend([aa,bb],labels=['model','observations'],fontsize=fontsize)
axx[1].set_ylabel('Freeboard [m]')
plt.xlim(['2024-01-26','2024-04-15'])


# plt.savefig('figures/HeatBudget/FloodModel_Fw0.png',dpi=300, bbox_inches='tight')



#----- Calculate Fw using the residual method ---------


# If Fw is negative, implies that the ocean is a heat sink - this is not physical. So Hmod must be > Hobs

dt = 60*60*24 # daily time step

H_i_mod = H_i_.resample(time='1D').mean('time')
H_i_obs = -H_bottom.resample(time='1D').mean('time')

dH_i_mod = H_i_mod.diff('time')
dH_i_obs = H_i_obs.diff('time')

F_w_res = (H_i_mod - H_i_obs)*L_i*rho_i/(dt) 

F_w_res2 = (dH_i_mod - dH_i_obs)*L_i*rho_i/(dt) 










