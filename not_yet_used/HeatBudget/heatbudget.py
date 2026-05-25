'''
Process surface and basal heat flux variables out of IMS data and plot them

SIGN CONVENTION (UPDATED MARCH 11, 2025): POSITIVE INTO THE ICE, NEGATIVE AWAY FROM THE ICE
Conductive heat flux is always negative relative to the temperature gradient
'''

import numpy as np 
import xarray as xr
import pickle
from functions import IMS_toolbox as IMS
import matplotlib.pyplot as plt 
import scipy
import pandas as pd
import tqdm
from scipy import stats
import matplotlib.dates as mdates
# import sympy as sp

plt.ion()
fontsize=12


## ---------- Load data -----
t1,t2 = '2024-01-26','2024-04-15'


# Weather station
ds_weather = xr.open_dataset('Weather/data/2024/WeatherVars_CR1000X.nc')
# Work with hourly data
ds_weather = ds_weather.resample(time="1H").mean('time')

# weekly ice and snow thicknesses
weekly_ice = xr.open_dataset('SiteVisits/weekly_ice_2024.nc')

# SIMBA ice thickness and temp
with open('./SIMBA/temp_ice_z.pickle','rb') as f:
	temp_ice = pickle.load(f)

# ICE THICKNESS
with open('./SIMBA/H_SIMBA.pickle','rb') as f:
	H_ice = pickle.load(f)

# # ICE-WATER INTERFACE
# with open('./SIMBA/H_bottom.pickle','rb') as f:
# 	H_bottom = pickle.load(f)

with open('./SIMBA/ice_water_spline_clamped.pickle','rb') as f:
    H_bottom = pickle.load(f)

H_bottom = H_bottom.sel(time=slice(t1,t2))

# SNOW-AIR INTERFACE
with open('./SIMBA/snow-air.pickle','rb') as f:
    snow_air = pickle.load(f)

# SNOW ICE INTERFACE
with open('./SIMBA/snow-ice.pickle','rb') as f:
    snow_ice = pd.read_pickle(f)

# SNOW ICE INTERFACE - SMOOTHED
with open('./SIMBA/snow-ice-smoothed.pickle','rb') as f:
    snow_ice_smoothed = pd.read_pickle(f)

# SNOW THICKNESS
with open('./SIMBA/Hsnow_SIMBA.pickle','rb') as f:
    H_snow = pickle.load(f)

# Load temperature data
with open('./SIMBA/da_temp_z.pickle','rb') as f:
    da_temp = pd.read_pickle(f)

# Load ocean heat flux 
with open('./HeatBudget/Fw_quad_hourly.pickle','rb') as f:
    Fw_quad = pickle.load(f)

# Detided Fw
# De-tide using Doodson filter
Fw_quad_detided = xr.zeros_like(Fw_quad)
Fw_quad_detided[:] = IMS.DoodsonX0(Fw_quad)

# Fw_fit_detided = xr.zeros_like(Fw_fit)
# Fw_fit_detided[:] = IMS.DoodsonX0(Fw_fit) # WEird amount of nans...

# Subset SIMBA data to match weather station
da_temp = da_temp.sel(time=slice(t1,t2))

da_temp_daily = da_temp.resample(time='1D').mean('time')
snow_ice_daily = snow_ice.resample(time='1D').mean('time')
snow_air_daily = snow_air.resample(time='1D').mean('time') # snow-air is already daily but resample it to get the timestamps to match up 
# Snow temperature
temp_snow = da_temp_daily.where((da_temp_daily.z > snow_ice_daily) & (da_temp_daily.z < snow_air_daily),other=np.nan)

## ---------- Define a reference layer through the ice -----

# Calculate over reference layer only to fit the model (timeseries)
# Reference layer is 0.08 m from the ice base, following Lei et al. [2010] for ice with H ~ 0.5 m

ref_layer_lower = H_bottom+0.08
ref_layer_upper = H_bottom+0.2
# Negative sign b/c Positive upwards
temp_ice_ref = temp_ice.where((temp_ice.z < ref_layer_upper) & (temp_ice.z > ref_layer_lower), other=np.nan)

###-------------- Define variables---------------

# Ice temperature 
# T_i = temp_ice_ref.mean('z')
# DAILY
T_a = ds_weather['AirT_C_Avg'].resample(time='1D').mean('time') # Air temperature
# Flip signs of radiaiton - POSITIVE radiation = SNOW TO ATMOSPHERE
F_lw_net = -ds_weather['RlNet_Avg'].resample(time='1D').mean('time') # net LW should be positive
F_sw_net = -ds_weather['RsNet_Avg'].resample(time='1D').mean('time') # net SW should be negative
U_wd_hourly = ds_weather['WS_ms_Avg']
U_wd = U_wd_hourly.resample(time='1D').mean('time') # wind speed
# Wind at 10 m (Peterson and Hennessey 1977) (u_z/u_zref = (z/z_ref)^1/7)
U_wd_10m = U_wd*(10/2)**(1/7)
U_wd_10m_hourly = U_wd_hourly*(10/2)**(1/7)
RH = ds_weather['Humidity'].resample(time='1D').mean('time')
P = ds_weather.BP_mbar_Avg.resample(time='1D').mean('time') # mbar



# Resample Hice and Hsnow to daily 
Hice_d = H_ice.resample(time='1D').mean('time')
Hsnow_d = H_snow.resample(time='1D').mean('time')

############ Define constants #################

dz = 0.02       # SIMBA node spacing
c_i = 2100      #J/kgC - specific heat capacity of pure (fresh) sea ice 
L_ice = 333000           # latent heat of fusion for sea ice [J/kg] / sea ice latent heat capacity
rho_i = 910 #kg/m3 - sea ice density
rho_fi = 917 # - fresh ice density
rho_a = 1.22 # kg/m3 - atmospheric density
rho_s = 330 # kg/m3 - snow density
# Snow and ice density time series
rho_s_i = xr.zeros_like(T_a)*np.nan
rho_s_i = rho_s_i.where(H_snow < 0.02, rho_s).fillna(rho_i)
# k_i = 2.09 #W/m*K, Sea ice heat conductivity, (Pringle et al. 2006)
S_i = 5 # Ice salinity, PSU, based on IMS ice core estimate from 2025
# k_i = (rho_i/rho_fi)*(2.11 - 0.011*T_i + 0.09*(S_i/T_i) - (rho_i - rho_fi)/1000)
# k_i_surf = (rho_i/rho_fi)*(2.11 - 0.011*T_s_obs + 0.09*(S_i/T_s_obs) - (rho_i - rho_fi)/1000)
k_i = 2.3
k_s = 0.3 #W/m*K, snow heat conductivity
# Snow and ice density k_i timeseries
k_s_i = xr.zeros_like(T_a)*np.nan
k_s_i = k_s_i.where(H_snow < 0.05, k_s).fillna(k_i)
S_i_per = S_i/1000 #ice salinity in %
alpha = -0.0182 # degC^-1
c_w = 4229 #J/kgC 
# For latent heat
rho_a = 1.22 # kg/m3 - atmospheric density
L_v = 2.5e6 # J/kg - latent heat of evaporation
L_s = 2.83e6 # J/kg - latent heat of sublimation (or vaporization)
c_E = 1.6e-3 # Latent heat transfer coefficient (value from Vihma et al. 2009)


###-------------- Albedo ----------------

# Calculate albedo - outgoing/incoming SWR
# SWR should always be entering the ice (positive)
SWin = ds_weather.SWUpper_Avg#.resample(time='1D').mean('time')
SWout = ds_weather.SWLower_Avg#.resample(time='1D').mean('time')

SWin_clean = SWin.where(SWin > 0, 0).resample(time='1D').mean('time')
SWout_clean = SWout.where(SWout > 0, 0).resample(time='1D').mean('time')
albedo = SWout_clean/SWin_clean



#------------------ CONDUCTIVE HEAT FLUX --------------------
# (direct parametrization from SIMBA data based on Semtner 1976) 
# Fc is positive towards the ice surface (positive up at the surface)
# the gradient should be relative to the temperature flow (cold to warm), which is down (negative)

##### Fc through the ice slab
dT_dz = temp_ice.differentiate('z')
F_c_2d = -k_i * (dT_dz)
F_c_2d_daily = F_c_2d.resample(time='1D').mean('time')

dT_dz_ref = temp_ice_ref.differentiate('z')
F_c_ref = -k_i * (dT_dz_ref) 
F_c = F_c_ref.mean('z')
F_c_daily = F_c.resample(time='1D').mean('time')


##### Fc through the full snow-ice slab

# Temperature through the full snow and ice layers
temp_ice_snow = da_temp_daily.where(
    (da_temp_daily.z < snow_air) &  
    (da_temp_daily.z > H_bottom.resample(time='1D').mean('time'))
    )
dT_dz_full = temp_ice_snow.differentiate('z') 
F_c_full = -k_s * (dT_dz_full) # Assume most of it is snow

##### Fc through the surface layer

z1 = 0.1 # Surface layer depth, m
surf_layer_lower = snow_air-z1 # Bottom of the layer is 20 cm below the snow surface, doesn't matter if it's snow or ice
surf_layer_upper = snow_air

# snow temperature 
temp_snow = da_temp_daily.where(
    (da_temp_daily.z<=snow_air) & 
    (da_temp_daily.z >= snow_ice_daily)
    )
# Fc through snow
dT_dz_snow = temp_snow.differentiate('z')
F_c_snow = -k_s*dT_dz_snow

# Fc through the surface layer
dT_dz_surf = dT_dz_full.where(
    (dT_dz_full.z < surf_layer_upper) & 
    (dT_dz_full.z > surf_layer_lower), 
    other=np.nan
    )

F_c_surf_2d = -k_s_i*dT_dz_surf
F_c_surf = F_c_surf_2d.mean('z')


# check that reference level looks good
plt.figure(figsize=(10,5),facecolor='white')
plt.pcolormesh(F_c_2d.time.values,F_c_2d.z,F_c_2d.T,cmap='RdBu_r',vmin=-40,vmax=40)
# plt.plot(F_c_.time, )
plt.plot(F_c_2d.time, ref_layer_lower,'k--') 
plt.plot(F_c_2d.time, ref_layer_upper,'k--')
plt.legend(['Reference layer (8-20 cm above ice bottom)'])
plt.xticks(rotation=15)
plt.colorbar(label=r'Conductive Heat Flux [W/m$^2$]')
plt.ylim([-1,1])
#
# plt.savefig('figures/HeatBudget/Fc_reference_layer.png',dpi=300)
#

###-------------- shortwave radiation  ----------------
## Shortwave radiation that gets exported to the ocean (remove it from the surface balance)

# Persson (2012)
kxs = 10 # m^-1; solar extinction coefficient in snow
kxin = 4.6 # in ice, near-infrared 
kxiv = 0.72 # in ice, visible
I0v = 0.95 # Ice surface transmission parameters
I0n = 0.37
fv = 0.6 # 60% visible
fn = 0.4 # 40% near-infrared

D_i = -Hice_d
D_s = Hsnow_d
fD = np.exp(-kxs*D_s)*(fv*I0v*np.exp(-kxiv*D_i)+fn*I0n*np.exp(-kxin*D_i))
SW_t = SWin_clean*(1-albedo)*fD

## Absorbed SWR (internal heat source), remove it from the surface balance

# Flux of penetrating solar radiation, Beer's law:
I0 = 0.18 # Clear sky conditions. I0 = 0.35 for cloudy conditions
k_i_ = 1.38
# k_i_daily = k_i.resample(time='1D').mean()

F_I0 = I0*(1-albedo)*SWin_clean*np.exp(-k_i_*z1)
F_I0 = F_I0.where(H_snow < 0.05,0) # only when ice is not snow covered!

# Only when ice is not snow covered
I0_ = xr.zeros_like(SWin_clean).where(H_snow > 0.05, I0)

F_sw_net = -(1-albedo)*(1-I0_)*SWin_clean


###-------------- Surface energy balance ----------------

# Identify the surface and take the SIMBA temperature for Ts
# T_s_obs = da_temp.resample(time='1D').mean('time').sel(z=snow_air.resample(time='1D').mean('time')-0.02,method='nearest')

# Try using T_s calculated from net longwave radiation
LWin = ds_weather['LWUpperCo_Avg']
LWout = ds_weather['LWLowerCo_Avg']
epsilon = 0.975
sigma = 5.67e-8
T_s_obs = (((LWout - (1-epsilon)*LWin)/(epsilon*sigma))**0.25 - 273.15).resample(time='1D').mean('time')

# For now, "clean" LWR and SWR by setting unrealistic (pos/neg) values to 0
# POSITIVE radiation = SNOW TO ATMOSPHERE
F_lw_net_clean = F_lw_net.where(F_lw_net > 0, 0) # net LW should always be pos 
F_sw_net_clean = F_sw_net.where(F_sw_net < 0, 0) # net SW should always be neg

# Net SWR including transmitted component 
# F_sw_net_tot = F_sw_net_clean - SW_t

#For now set water temp as constant
T_w = -0.75 # ESTIMATE BASED ON SIMBA DATAx

F_c_denom = np.abs(Hice_d)/k_i + Hsnow_d/k_s 



###-------------- Error estimates ----------------


# Weather station: 
sig_Ta = xr.zeros_like(T_a)+0.3 # deg. C
sig_RH = RH*0.02 # 2%
sig_Uwd_10m = U_wd_10m*0.05 # 5%
sig_P = P*0.04

# SIMBA 
# sig_Tobs = xr.zeros_like(T_s_obs)+0.0625 # deg. C on SIMBA temp nodes
# Relative uncertainty propogation - assume emissivity has uncertainty of 0.005 (Miller et al. 2017)
sig_Tobs_relative = np.sqrt((LWout*0.1/LWout)**2 +(LWin*0.1/LWin)**2 +(0.005/epsilon)**2)
sig_Tobs = T_s_obs*sig_Tobs_relative

# Ice/snow thickness from SIMBA... let's just say +/- 0.02 m for now
sig_Hice = xr.zeros_like(H_ice)+0.02
sig_Hsnow = xr.zeros_like(H_ice)+0.02

# CNR4: +/- 10%
sig_netLW = F_lw_net_clean*0.1
sig_netSW = F_sw_net_clean*0.1


### Turbulent fluxes ###
# Sensible
F_sens,sig_Fsens = IMS.sensible_heat_flux(U_wd_10m,T_s_obs,T_a,sig_Uwd_10m,sig_Tobs,sig_Ta)

# sig_Fsens_relative = np.sqrt((sig_Uwd_10m/U_wd_10m)**2 + (sig_Tobs/T_s_obs)**2 + (sig_Ta/T_a)**2)
# sig_Fsens = sig_Fsens_relative*F_sens

# Latent
F_lat = IMS.latent_heat_flux(U_wd_10m, RH, P, T_s_obs, T_a)

# Latent heat uncertainty
# assume 20% of latent heat flux, Vickers 2010 as cited in Else et al. 2014
sig_Fl = F_lat*0.2 

sig_Fl_relative = np.sqrt(
    (sig_Uwd_10m/U_wd_10m)**2 +
    (sig_RH/RH)**2 +
    (sig_P/P)**2 +
    (sig_Tobs/T_s_obs)**2 +
    (sig_Ta/T_a)**2
    ) 

sig_Fl = sig_Fl_relative*F_lat

# Conductive heat uncertainty
# k_i_daily = k_i.resample(time='1D').mean()
dFc_dki = -dT_dz_surf.mean('z')
dFc_ddT = -k_i/dz
dFc_ddz = k_i*dT_dz_surf.mean('z')/dz

sig_ki = 0.1 # W/mK - Miller et al. 2017
sig_dT = 0.0625
N = 10 # Number of sensors we average over
sig_dT_avg = np.sqrt(sig_dT**2 + sig_dT**2)/np.sqrt(N)
# sig_dT_relative = np.sqrt(9*0.00625**2 + 9*0.00625**2) # Temp difference between 2 sensors. 10 sensors in total, so T appears 18 times in the mean calculation 

sig_dz = 0

# sig_Fc = np.sqrt(
#     (dFc_dki*sig_ki)**2 +
#     (dFc_ddT*sig_dT)**2 +
#     (dFc_ddz*sig_dz)**2 
#     )

dz = 0.02
dT = (dT_dz_surf*dz).mean('z')
sig_Fc_relative = np.sqrt(
    (sig_ki/k_s)**2 +
    (sig_dT_avg/dT)**2 +
    (sig_dz/dz)**2 
    ) 

sig_Fc = sig_Fc_relative*F_c_surf



###-------------- Net heat flux at the surface ----------------

# Sum of surface fluxes
F_surf = F_lw_net_clean + F_sw_net + F_sens + F_lat

# Net energy flux at the surface
F_net_surf = F_surf - F_c_surf

# Split up turbulent vs radiative components
# F_turb = F_lat + F_sens
# F_rad = F_lw_net_clean + F_sw_net_tot

# Net surface heat flux uncertainty estimate
sig_F_surf = np.sqrt(sig_netLW**2 + sig_netSW**2 + sig_Fsens**2 + sig_Fl**2 + sig_Fc**2)

# rolling average
i = 5
sig_F_surf_roll = sig_F_surf.rolling(time=i,center='True').mean()


############### BASAL HEAT BALANCE ###################

###-------------- Calculate Fw as a residual from F_c + F_l + F_s - F_w = 0 (positive=warming, melting, heat going into the ice) based on Lei et al. (2014) and Mcphee & Untersteiner (1982) ----------------


# bottom growth rate 
# dH_dt_bot = H_bottom.diff(dim='time')/(6*60*60) # m/s
dH_dt_bot = H_bottom.differentiate('time',datetime_unit="s") # m/s

# latent heat from ice growth and decay at the bottom as in Semtner (1976)
F_l = L_ice*rho_i*dH_dt_bot # where dH_dt is the BOTTOM ice growth rate; negative F_l means heat is being released from the ice to the ocean (ice growth)

# temp from reference layer to ice bottom
# T_bot = temp_ice[1:].where((temp_ice[1:].node > ice_bottom[1:]-5) & (temp_ice[1:].node < ice_bottom[1:]), other=np.nan).mean('node')
T_bot = temp_ice.where((temp_ice.z < ref_layer_lower) & (temp_ice.z > H_bottom), other=np.nan).mean('z')


# Temporal variation of ice temp below the reference layer to the ice bottom
# dT_dt_bot = T_bot.diff('time')/(6*60*60)
dT_dt_bot = T_bot.differentiate('time',datetime_unit="s") 


# dT_dt_bot = dT_dt.where((dT_dt.node > ice_bottom[1:]-5) & (dT_dt.node < ice_bottom[1:]), other=np.nan)#.mean('node')
dH = (ref_layer_upper - ref_layer_lower) # reference layer thickness
F_s = rho_i*c_i*dT_dt_bot*dH
# F_s = 0

# Calculate F_w as a residual 
F_w_lei = F_c + F_l #- F_s


###-------------- Calculate Fw as a residual from F_c + F_l + F_s - F_w = 0 (positive=warming, melting, heat going into the ice) based on Perovich and Elder (2002) ----------------
### F_w = 1/delta(t) (Qf + Qs + Ql)


# ------ Schwerdtfeger 1961 values and equation for, units cal/gC------
# L_ice = 79.67
# c_i = 0.48
# c_w = 1.01
# S_i = 8/1000
# T_bot = -2

# c_s = -L_ice*(S_i/(alpha*T_bot*T_bot)) + (S_i/(alpha*T_bot))*(c_w - c_i) + c_i

# q_m = (L_ice - c_i*T_bot)*(1-S_i/(alpha*T_bot)) + S_i*(c_w-c_i)/alpha*np.log(S_i/(alpha*T_bot))


# ------    ------------   ------

# Specific heat, Schwerdtfeger (1961), J/kgC
S_i_per = 5/1000
c_s = -L_ice*alpha*(S_i_per/(T_bot*T_bot)) + alpha*(S_i_per/(T_bot))*(c_w - c_i) + c_i
# Heat needed to melt a parcel of ice, Schwerdtfeger (1961), J/K
S_i_bot = 12/1000 # saltier at the bottom, folliwing Lei et al (value from IMS ice core)
q_m = (L_ice - c_i*T_bot)*(1-alpha*S_i_bot/T_bot) + S_i_bot*alpha*(c_w-c_i)*np.log(S_i_bot*alpha/(T_bot))
Qs = rho_i*c_s*dT_dt_bot
Ql = rho_i*q_m*dH_dt_bot # Negative sign to make growth rate positive
F_w_perov = F_c - Qs - Ql


###-------------- Daily (best) basal fluxes and residual flux ----------------


F_l_daily = F_l.resample(time='1D').mean()
F_s_daily = F_s.resample(time='1D').mean()
F_w_daily_quad = Fw_quad_detided.resample(time='1D').mean('time')#.rolling(time=7,center='True').mean()
# F_w_daily_fit = Fw_fit.resample(time='1D').mean('time')#.rolling(time=7,center='True').mean()

# Residual
F_w_residual = F_l_daily + F_c_daily # Equal to Fw
F_bot = F_l_daily + F_c_daily - F_w_daily_quad

# Plot the different ways to getting Fw

plt.figure(figsize=(8,5))
F_w_daily_quad.plot(c='r',label='Quadratic drag law')
# (F_w_daily_fit/10).plot(c='b',label='Semi-log fit (x10)')
F_w_residual.plot(c='k',label='Residual method')
# Line separating "cut-off" for acceptable F_l based on FDD model
plt.axvline('2024-02-02',c='grey')
plt.axhline(0,c='grey',linestyle='--')
plt.legend()
plt.ylim([-5,10])
plt.ylabel('W/m^2')
plt.title('Comparison of Fw estimates')
#
# plt.savefig('figures/HeatBudget/compare_Fw.png',dpi=400,bbox_inches='tight')
#

##----------------- Calculate k_i as a functi on Salinity  ---------------


T_i = temp_ice_ref.mean('z')
S_i = 5 # ppt (PSU)

k_i_2 = (rho_i/rho_fi)*(2.11 - 0.011*T_i + 0.09*(2/T_i) - (rho_i - rho_fi)/1000)
k_i_4 = (rho_i/rho_fi)*(2.11 - 0.011*T_i + 0.09*(4/T_i) - (rho_i - rho_fi)/1000)
k_i_5 = (rho_i/rho_fi)*(2.11 - 0.011*T_i + 0.09*(S_i/T_i) - (rho_i - rho_fi)/1000)
k_i_6 = (rho_i/rho_fi)*(2.11 - 0.011*T_i + 0.09*(6/T_i) - (rho_i - rho_fi)/1000)

# plt.figure()
# k_i_2.plot(label=r'$S_i = 2$ PSU')
# k_i_4.plot(label=r'$S_i = 4$ PSU')
# k_i_5.plot(label=r'$S_i = 5$ PSU')
# k_i_6.plot(label=r'$S_i = 6$ PSU')
# plt.title(r'$k_i = (\frac{\rho_i}{\rho_{fi}})*(2.11 - 0.011*T_i + 0.09*(\frac{S_i}{T_i}) - \frac{\rho_i - \rho_{fi}}{1000}$')
# plt.legend()

#
# plt.savefig('figures/HeatBudget/k_i.png',dpi=400,bbox_inches='tight')
#

