'''WORK IN PROGRESS TO ADAPT SEMTNER MODEL FOR IMS DATA'''


import numpy as np 
import xarray as xr
import pickle
from functions import IMS_toolbox as IMS
import matplotlib.pyplot as plt 
import scipy
import tqdm
plt.ion()


# Weather station
ds_weather = xr.open_dataset('Weather/WeatherVars_CR1000X.nc')


# SNOW THICKNESS
with open('./SIMBA/Hsnow_SIMBA.pickle','rb') as f:
    H_snow = pickle.load(f)

# SNOW-AIR INTERFACE
with open('./SIMBA/snow-air.pickle','rb') as f:
    snow_air = pickle.load(f)

# Observations to compare to
with open('./SIMBA/H_bottom.pickle','rb') as f:
    H_bottom = pickle.load(f)


# Convert to xarray
def convert2da(sol,begT,endT,params=None,time_origin=0):
    # spinup time
    
    """Create a xarray.DataArray from the Semtner model outputs."""
    # Bulk of the function
    ds_sol = xr.Dataset(coords={'time': T_a.sel(time=slice(begT,endT)).time},
                        data_vars={'H_i': ('time',sol)}
                                   
                       )
    # Then assign some attributes to describe the solution
    ds_sol['H_i'].attrs['name'] = 'Thickness'
    ds_sol['H_i'].attrs['long_name'] = 'Sea Ice Thickness'
    ds_sol['H_i'].attrs['units'] = 'm'

    return ds_sol


####  Define constants

# T_day = 86400
# T_year = 365 * T_day
# sigma_b = 5.67 * 10 ** (-8) # Stefan-Boltzmann constant.
# TK2C = 273.15 # To convert from Kelvin to celsius
T_w = -1.75 # Bottom temperature. Could be providing as a forcing as well.
# F_w = 0 # Bottom ice-ocean flux. Could be providing as a forcing as well.
F_w_ = xr.zeros_like(H_s_) #W/m2
# F_w_ = Fw_quad.resample(time='1H').mean('time').isel(time=slice(None,len(H_s_)))


# Parameters
param=dict()
# param['q'] = 334*1e6 # J/m3 # freshwater
param['q'] = 300*1e6 # J/m3 # 300 for sea water
# param['q'] = 330000
param['k_i'] = 2.3 # J/m/K/s
# param['albedo_ice'] = 0.8 #Bare ice
# param['albedo_melt'] = 0.5 #Melt ice
# # Forcing-related constant parameters
# # param['T_w_in'] = -1.75

# Start with the period before the snow storm 
begT = np.datetime64('2024-01-26')
endT = np.datetime64('2024-04-15')

# Input choice for snow forcing
# H_snow_d = H_snow.resample(time='1D').mean('time').sel(time=slice(begT,endT)).values
H_snow_d = snow_air.resample(time='1D').mean('time').sel(time=slice(begT,endT)).values
# H_snow_d = np.zeros_like(H_snow_d)


# HOURLY WEATHER
# T_a = ds_weather['AirT_C_Avg'].resample(time='1D').mean('time')
# # Flip signs of radiaiton - POSITIVE radiation = SNOW TO ATMOSPHERE
# F_lw_net = ds_weather['RlNet_Avg'].resample(time='1D').mean('time')
# F_sw_net = ds_weather['RsNet_Avg'].resample(time='1D').mean('time')
# U_wd = ds_weather['WS_ms_Avg'].resample(time='1D').mean('time') # wind speed

# Forcings
param['F_wind10_in'] = U_wd.sel(time=slice(begT,endT)).values
param['F_lw_net'] = F_lw_net.sel(time=slice(begT,endT)).values
param['F_sw_net'] = F_sw_net.sel(time=slice(begT,endT)).values
param['T_a_in'] = T_a.sel(time=slice(begT,endT)).values
param['F_lh_in'] = np.zeros(param['F_sw_net'].size) # Set latent heat flux to 0 for now


time_steps = len(param['T_a_in'])
dHice_dt = np.zeros(time_steps)
H_ice = np.zeros(time_steps)
F_airice = np.zeros(time_steps)
T_s = np.zeros(time_steps)
F_c = np.zeros(time_steps)
# LWR_out = np.zeros(time_steps)

# Assign parameters:
L_ice = param['q'] # Ice specific latent heat of fusion [J/m^3]
k_i = param['k_i'] # Ice heat conductivity [J/s/m/K]
k_s = 0.47

# initial condition
H_ice[0] = 0.39 # thickness measurement on deploymet day
T_s[0] = T_a[0].values # air temperature on day of deployment


# Surface temperature from longwave radiation
# LWin = ds_weather['LWUpperCo_Avg']
# LWout = ds_weather['LWLowerCo_Avg']
# epsilon = 0.985
# sigma = 5.67e-8
# T_s_obs = (((LWout - (1-epsilon)*LWin)/(epsilon*sigma))**0.25 - 273.15).resample(time='1D').mean('time')


####### MODEL

for t in range(1,time_steps): 

    F_w = F_w_[t]
    
        
    # Need to introduce a condition: if H_ice is negative, I need to put it back as non-nul. 
    if H_ice[t-1]<=1e-3:
        H_i_old = 1e-3
    # Else, I just take the H_ice from previous time stamp
    else:
        H_i_old = H_ice[t-1]

    # Assign the old surface temperature
    T_s_old = T_s[t-1] # [°C]

    
    # Surface Heat Fluxes
    # -------------------
    # Calculate net shortwave radiation by changing albedo according to temperature
    # # F_sw_down = param['F_sw_in'][t] # [W m^{-2}]
    # if T_s_old<0:
    #     F_sw_net = F_sw_down * (1 - param['albedo_ice']) # [W m^{-2}]
    # else:
    #     F_sw_net = F_sw_down * (1 - param['albedo_melt']) # [W m^{-2}]
    F_sw_net = param['F_sw_net'][t]
    # Get longwave radiation
    # F_lw = param['F_lw_in'][t] # [W m^{-2}]
    F_lw_net = param['F_lw_net'][t]
    # Get latent heat flux
    F_lh = param['F_lh_in'][t]
    # Prepare sensible heat flux
    # Need to assign the transfer function for sensible heat flux:
    # f_sh = rho_a * c_{p,a} * c_{sh} * Wind speed
    Wd_10m = param['F_wind10_in'][t]
    f_sh = 1.22 * 1005 * 1.75 * 10**(-3) * Wd_10m # [W m^{-2}]
    # Also assign air temperature
    T_a2m =  param['T_a_in'][t] #+ TK2C # [K]
    
    # Surface Temperature Calculation
    # -------------------------------
    # I try to balance the surface heat budget Fair-ice + Fconduction = 0.
    # Using that, I can calculate a surface temperature:
    # \sigma_b T^4 +(\frac{k_i}{H_i} + f_{sh}) T - F_sw_net - F_lw - f_sh * T_a - \frac{k_i}{H_i} T_b = 0
    # But first, need a condition if there is no ice!
    # if H_i_old<=1e-3:
    #     T_s_new = 0.
    # else:
    
    # set net LW to 0  
    # sigma_b = 0
    
    # roots = np.roots([sigma_b, 
    #                   0., 
    #                   0., 
    #                   f_sh + k_i/H_i_old, 
    #                   -(F_sw_net + F_lw + F_lh + f_sh * T_a2m + k_i/H_i_old * (T_w + TK2C))])
    # Looked at the derivative of this polynomial: it's a simple a T^3 +b, which only has a negative root.
    # So I know that the 4th order polynomial only has two real roots, and only one that might be positive.
    # roots_real = np.real(roots[np.isreal(roots)])
    # T_s_new = np.max(roots_real) - TK2C # Convert back to Celsius


    # Surface temperature
    F_c_denom = H_ice[t-1]/k_i + H_snow_d[t-1]/k_s
    # Solve for T_s
    T_s[t] = (F_c_denom*f_sh*T_a2m + T_w - F_c_denom*(F_sw_net + F_lw_net)) / (F_c_denom*f_sh + 1)
    # T_s[t] = T_s_obs[t]
    # Surface Heat Budget
    # -------------------
    # I need to consider two cases: 
    # - If my surface temperature is positive, it is not realistic. 
    #   So I set it to 0. Using that, I can calculate the new heat conductive flux.
    #   Then, I calculate an outgoing longwave radiative flux (\sigma * (0+273.15)^4) to add to the surface heat budget.
    #   I recalculate my surface heat budget with this new temperature of 0°C, and I know it is supposed to be negative,
    #   since I already calculated the polynomial and it gave me a root above this zero surface temperature. 
    #   So calculating the surface budget with T=0 will necessarily give me a negative residual, which is "used" to melt ice.
    

    if T_s[t]>=0.0:
        # F_c_new = -k_i * (0.0 - T_w) / H_i_old  # New conductive flux with surface ice temperature Tia=0
        T_s[t] = 0
        F_c[t] = (T_s[t] -T_w) / F_c_denom
        
        # F_lw_out = -sigma_b * (0.0 + TK2C)**4  # New upward longwave radiations with Tia=0
        
        # Calculate the residual, divide it by latent heat L_ice
        # dHice_dt_top = (F_sw_net + F_lw_net + F_lh + f_sh * (T_a2m) - F_c[t])/ L_ice
    # - If my surface temperature is negative, I don't have surface melt and I cannot have surface growth.
    #   So I can just calculate the heat conduction with this new temperature and set the surface ice growth-melt rate to 0.

    else:
        # F_c_new = - k_i * (T_s_new - T_w) / H_i_old  # New heat conductivity - 1 layer
        F_c[t] = (T_s[t] - T_w) / F_c_denom
        dHice_dt_top = 0.0  # No ice melt at surface
    # Done with the surface budget

    # Bottom Heat Budget
    # -------------------
    # The bottom budget is much simpler, just the balance between the ice-ocean flux and the conductive flux.
    dHice_dt_bot = -(F_c[t] - F_w) / L_ice  # Negative sign b/c z is positive downwards (neg F_c means ice growth)
    # Done with the bottom budget

    # Total Heat Budget
    # -------------------
    # Just need to sum both budgets
    dHice_dt[t] = dHice_dt_bot + dHice_dt_top

    # Calculate the ice surface temperature rate
    # dT_dt = (T_s_new - T_s_old) / max(dt,1)
    
    
    # Need to introduce another condition: if I don't have ice, I cannot have a negative growth rate. So put it back to 0
    if (dHice_dt[t]<0.0) & (H_ice[t-1]<=0.0):
        dHice_dt[t]=0.0
    
    # Update thickness
    H_ice[t] = H_ice[t-1] + dHice_dt[t]*(60*60*24) # multiply by dt (1 day in seconds)
    
    # ## Restart thickness every season
    # if datetime_array[t].month==8:
    #     H_ice[t] = H_ice[0]
        



ds = convert2da(H_ice,begT,endT)

plt.figure()
ds['H_i'].plot()
(-H_bottom).plot()
plt.legend(['Model','Obs'])
