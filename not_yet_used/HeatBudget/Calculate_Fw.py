

###-------------- Calculate Fw from parametrization - law of the wall (based on Witte et al. 2021) ----------------


import numpy as np 
import xarray as xr
import pickle
from functions import IMS_toolbox as IMS
import matplotlib.pyplot as plt 
import scipy
from scipy import stats
import tqdm
import cmocean as cmo
import gsw
import pandas as pd
plt.ion()


t1,t2 = '2024-01-26','2024-04-15'

###------------------- Load TCM speed ---------------------

tcm = xr.open_dataset('TCM-1/TCM_currents.nc')
tcm_speed = tcm.sel(Depth=1.5)['Speed']
U = tcm_speed.resample(time='1H').mean().sel(time=slice(t1,t2))

###------------------- Load ADCP data from uppermost bin (BIN 34)---------------------


# Load ADCP currents
aqdXr = xr.open_dataset('ADCP/data/adp.nc')
# Swap real time and distance dims
aqdXr = aqdXr.swap_dims({'TIME':'time','DISTANCE':'distance'})
aqdXr = aqdXr.sel(time=slice('2024-01-26','2024-4-15')) # cut time to match other IMS data
v_N = aqdXr.v.sel(BEAM=1)
v_E = aqdXr.v.sel(BEAM=2)
adcp_speed = np.sqrt(v_N**2 + v_E**2)

### Define log layer

# find where the speed increases (this is the ice bottom in theory) - see compare_ADCP_TCM.py 
speed_adcp_avgbin = adcp_speed.mean('time')
loc = np.where(speed_adcp_avgbin>0.15)[0][0]
# loc gives 35, so uppermost valid bin is 34


###------------------- Calculate delta T ---------------------

# %load RBR_IMS/code/load_RBR.py

# load surface ocean temperature from SIMBA

# Load temperature data
with open('./SIMBA/da_temp_z.pickle','rb') as f:
    simba = pd.read_pickle(f)
    # simba = pickle.load(f)

# Ice bottom
with open('./SIMBA/H_bottom.pickle','rb') as f:
    H_bottom = pickle.load(f)

# Weekly CTD casts
ctd = xr.open_dataset('CTD_transect/CTD_IMS_timeseries.nc')

# Get the under-ice ocean tmperature from SIMBA data
valid = H_bottom.dropna(dim='time')
simba_ = simba.where(simba.time==valid.time)
oce_surf = simba_.sel(z=valid-0.04,method='nearest') # surface temp - 2 nodes below the ice bottom
oce_surf_1h = oce_surf.resample(time='1H').interpolate('linear')


### Calculate the under-ice salinity from weekly CTD T/S relationships


# Fit through the top layer only - based on IMS timeseries 
tt = ctd.where(((ctd.Depth > 0.8) & (ctd.Depth < 1.2)), drop=True) 
# tt = ctd.where(((ctd.Depth > 0.2) & (ctd.Depth < 0.8)), drop=True) 
y = tt['Absolute_Salinity']
A = tt['Conservative_Temperature']
s,b,r_value,p_value,st_err = IMS.fit_linear_2d(A,y)

# Get surface salinity from SIMBA temp data
# Based on the IMS timeseries, the surface salinity should be between 10 and 30
SA_1h = oce_surf_1h*s + b

# Calculate deltaT
begT,endT = oce_surf_1h.time[0],oce_surf_1h.time[-1]
# Calculate freezing temperature
# SA_1h = SA.resample(time='1H').mean('time').sel(time=slice(begT,endT),depth=-1.88)
T_freeze = gsw.t_freezing(SA_1h,0,0)

deltaT = oce_surf_1h.values - T_freeze.values

# Check the fit
plt.figure()
plt.scatter(ctd['Conservative_Temperature'],ctd['Absolute_Salinity'],c=ctd['Depth'],label='Data')
# plt.scatter(tt['Conservative_Temperature'],tt['Absolute_Salinity'],c=tt['Depth'],label='Data')
mock_T = np.linspace(-1.6,0,10)
plt.plot(mock_T,mock_T*s + b,'k-',label='Fit')
plt.legend()
plt.xlabel('Temperature [deg. C]')
plt.ylabel('Salinity [g/kg]')
plt.title('Fit through 1.2 m < z < 0.8 m')
#
# plt.savefig('figures/HeatBudget/salinity_fit.png',dpi=400,bbox_inches='tight')
#


## Diagnostic plots for calculating u_star and Fw
fig,ax = plt.subplots(figsize=(8,5))
ax.plot(SA_1h.time,SA_1h,'b-')
ax.set_ylabel('Salinity [g/kg]')
ax2 = ax.twinx()
ax2.plot(oce_surf_1h.time,oce_surf_1h,'m-')
ax2.set_ylabel('Temperature [deg. C]')
fig.legend(['salinity','temperature'],bbox_to_anchor=[0.9,0.97])
#
# plt.savefig('figures/HeatBudget/under-ice_salinity_temperature.png',dpi=400,bbox_inches='tight')
#

## Diagnostic plots for calculating u_star and Fw
fig,axx = plt.subplots(nrows=2,ncols=1,figsize=(8,5))
ax = axx[0]
# ax.plot(T_freeze.time,T_freeze,'b-')
ax.plot(T_freeze.time,deltaT,'b-',zorder=150)
ax.set_ylabel('Temperature [deg. C]')
ax_ = ax.twinx()
ax_.plot(U.time,U,'r-',zorder=1)
ax_.set_ylabel('Speed [m/s]')
fig.legend(['delta(T)','U'],bbox_to_anchor=[0.92,0.99])
ax.set_xlim(begT.values,endT.values)
ax2 = axx[1]
ax2.plot(T_freeze.time,T_freeze)
ax2.plot(oce_surf_1h.time,oce_surf_1h)
ax2.legend(['T_freeze','Under-ice temperature'])
ax2.set_ylabel('Temperature [deg. C]')
ax2.set_xlim(begT.values,endT.values)
#
# plt.savefig('figures/HeatBudget/ustar_diagnostics.png',dpi=400,bbox_inches='tight')
#

###------------------- Calculate ustar from quadratic drag law (Kirillov et al. 2015)---------------------

c_w = 0.0055
ustar_quad = np.sqrt(c_w*U**2) 


###------------------- # Calculate u_star from direct param ---------------------


def calculate_ustar(adcp_speed, roll):
    '''
    '''
    k = 0.4 #dimensionless von karman constant

    deeper_bin = 33
    shallower_bin= 34
    icedepth=0.5
    deepdepth = aqdXr.distance[deeper_bin].values.item()
    shallowdepth = aqdXr.distance[shallower_bin].values.item()

    # u(z)
    u_z = adcp_speed.isel(distance=deeper_bin).rolling(time=roll,center=True,min_periods=1).mean() 
    # u(z0)
    u_z0 = adcp_speed.isel(distance=shallower_bin).rolling(time=roll,center=True,min_periods=1).mean()

    ustar = k*(u_z - u_z0)/np.log((deepdepth-icedepth)/(shallowdepth-icedepth))
    ustar = ustar.where(ustar>0)

    return ustar


roll= 5 #number of 10-minute periods to calculate the rolling mean over
#calculate ustar
ustar = calculate_ustar(adcp_speed, roll)

###------------------- Calculate ustar from semi-log fit  ---------------------


# dates = aqdXr.time[0:10]


#define bins to be used in fit
# bins = aqdXr.distance[loc-4:loc] # loc is the ice bottom
# bins = aqdXr.distance[loc-6:loc-2]
# #loglayer = aqdXr.speed.resample({'time':'1H'}).mean(dim='time').sel(bindepth=bins) #for if you want to resample to 1H
# loglayer = adcp_speed.sel(distance=bins) #to keep the initial 15min period

# Plot to check log layer

# plt.figure(figsize=(10,5),facecolor='white')
# adcp_speed.plot(vmin=0,vmax=3,cmap=cmo.cm.speed) 
# plt.axhline(loglayer.distance[0],label='Log layer')
# plt.axhline(loglayer.distance[-1])
# plt.ylabel('Bin distance [m]')
# plt.legend()


# Loglayer from TCMs
loglayer = tcm.Speed.resample(time='1H').mean().sel(time=slice(begT,endT))
kappa = 0.4

dn=[]
#for every date, fit the profile and fill out a pandas dataframe with slope, yint, r_value, p_value, and std_err
for ind in tqdm.tqdm(np.arange(0,len(loglayer.time))):
    x = loglayer.isel(time = ind) # u(z) - u(z0), u(z0) = 0
    y = np.log(x.Depth) # ln(z) 

    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
    df1 = pd.DataFrame(data = {'ustar': kappa/slope,
                              'z0':np.exp(intercept),
                              'r':r_value,
                              'p':p_value,
                              'stderr':std_err,
                              'upper':x[0].values.item(),
                              'lower':x[0].values.item()},
                       index = {x.time.values})
    dn.append(df1)

logfit = pd.concat(dn)



rmin = 0.9
logfit_good = logfit.where(logfit.r > rmin)
ustar_fit = logfit_good.ustar

###------------------- Calculate Fw ---------------------


St = 0.0056
cp =  gsw.cp_t_exact(SA_1h,oce_surf_1h,0)
rho = gsw.rho_t_exact(SA_1h,oce_surf_1h,0) #in-situ density, NOT density anomaly

Fw_quad = rho*cp*St*ustar_quad*deltaT
Fw_fit = rho*cp*St*ustar_fit*deltaT

plt.figure(figsize=(10,5),facecolor='white')
plt.title('u_star')
plt.plot(loglayer.time,ustar_fit/10,'k-',alpha=0.5) 
ustar_fit_daily = ustar_fit.rolling(4*24,center=True,min_periods=2).mean()
plt.plot(loglayer.time,ustar_fit_daily/10,'k-',label='Semi-log fit method (x10)') 

plt.plot(ustar_quad.time,ustar_quad,'maroon',alpha=0.5)
ustar_quad_daily = ustar_quad.rolling(time=4*24,center=True,min_periods=2).mean()
plt.plot(ustar_quad_daily.time,ustar_quad_daily,c='maroon',label='Quadratic drag law')

plt.ylabel('m/s')
plt.xticks(rotation=15)
plt.xlim(t1,t2)
plt.legend()

#
# plt.savefig('figures/HeatBudget/ustar_compare.png',dpi=500,bbox_inches='tight')
#

plt.figure(figsize=(10,5),facecolor='white')
plt.title('F_w')
plt.plot(loglayer.time,Fw_fit/10,'darkblue',alpha=0.5) 
Fw_fit_daily = Fw_fit.rolling(time=4*24,center=True,min_periods=2).mean()
plt.plot(loglayer.time,Fw_fit_daily/10,'darkblue',label='Semi-log fit method (x10)') 

plt.plot(Fw_quad.time,Fw_quad,'orange',alpha=0.5)
Fw_quad_daily = Fw_quad.rolling(time=4*24,center=True,min_periods=2).mean()
plt.plot(Fw_quad.time,Fw_quad_daily,c='orange',label='Quadratic drag law')

plt.ylabel(r'W/m$^2$')
plt.xticks(rotation=15)
plt.xlim(t1,t2)
plt.legend()


#
# plt.savefig('figures/HeatBudget/Fw_from_ustar.png',dpi=500,bbox_inches='tight')
#

# Save daily ocean heat flux
with open('./HeatBudget/Fw_quad_daily.pickle','wb') as f:
    pickle.dump(Fw_quad_daily,f)

# Save daily ocean heat flux
with open('./HeatBudget/Fw_quad_hourly.pickle','wb') as f:
    pickle.dump(Fw_quad,f)

with open('./HeatBudget/Fw_fit_hourly.pickle','wb') as f:
    pickle.dump(Fw_fit,f)

###------------------- Plot Fw over a range of St values---------------------


plt.figure(figsize=(10,5),facecolor='white')
plt.title('F_w with varying St')

for i,St in enumerate(np.linspace(0.0005,0.006,11)):
    Fw_quad = rho*cp*St*ustar_quad*deltaT
    Fw_fit = rho*cp*St*ustar_fit*deltaT

    Fw_fit_daily = Fw_fit.rolling(time=24,center=True,min_periods=2).mean()
    l1, = plt.plot(ustar_quad.time,Fw_fit_daily/10,'darkblue',alpha=1-(i/10)) 
    Fw_quad_daily = Fw_quad.rolling(time=24,center=True,min_periods=2).mean()
    l2, = plt.plot(Fw_quad.time,Fw_quad_daily,c='crimson',alpha=1-(i/10))


plt.ylabel(r'W/m$^2$')
plt.xticks(rotation=15)
plt.xlim(begT.values,endT.values)
plt.legend([l1,l2],labels=['Semi-log fit method (x10)','Quadratic drag law'],loc='upper right')

#
# plt.savefig('figures/HeatBudget/Fw_varying_St.png',dpi=500,bbox_inches='tight')
#

