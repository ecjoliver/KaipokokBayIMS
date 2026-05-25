
'''
Ice growth model with flooding and snow-ice growth

Based on Kirillov et al. 2015

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
ds_weather = xr.open_dataset('Weather/data/2024/WeatherVars_CR1000X.nc')

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
begT = np.datetime64('2024-02-03')
endT = np.datetime64('2024-04-15')


# Snow thickness, upsample to hourly
H_s_ = H_snow.sel(time=slice(begT,endT)).resample(time='1H').interpolate('linear')
# Interpolate the ends to fill nans
H_s_ = H_s_.interpolate_na(dim='time',method='nearest',fill_value="extrapolate")

# H_i_obs = np.abs(H_bottom)

# Assume surface temperature is at the air temperature
T_s_ = ds_weather['AirT_C_Avg'].sel(time=slice(H_s_.time[0].values,H_s_.time[-1].values)).resample(time='1H').mean('time')

F_sw_net = ds_weather['RsNet_Avg'].resample(time='1H').mean('time').sel(time=slice(begT,endT))
F_lw_net = ds_weather['RlNet_Avg'].resample(time='1H').mean('time').sel(time=slice(begT,endT))
U_wd = ds_weather['WS_ms_Avg'].resample(time='1H').mean('time').sel(time=slice(begT,endT)) # wind speed
T_air = ds_weather['AirT_C_Avg'].resample(time='1H').mean('time').sel(time=slice(begT,endT))

Wd_10m = U_wd*(10/2)**(1/7)

#--------- Set up the variables--------

time_steps = len(T_s_)

H_i_ = xr.zeros_like(H_s_)
H_si_ = xr.zeros_like(H_s_)
fb_ = xr.zeros_like(H_s_)
H_sdry_ = xr.zeros_like(H_s_)
dHice_dt_ = xr.zeros_like(H_s_)

F_w = 0 #W/m2

#### Initial conditions

H_i_[0] = 0.48
H_si_[0] = 0
H_sdry_[0] = H_s_[0]

dt = 60*60 # 1 hour


#--------- The model --------

for t in tqdm.tqdm(range(1,time_steps)): 

    ## Define the variables used in the mdel equations here
    # -------------------

    H_i = H_i_[t-1] # Ice thickness from prev time step to be used to calculate ice growth rate for this time step
    H_s = H_s_[t-1] # Measured snow depth
    H_si = H_si_[t-1] # Snow-ice layer thickness
    H_sdry = H_sdry_[t-1] # Dry snow (calculated)
    # T_s = T_s_[t] # Surface temperature
    fb = fb_[t-1] # Freeboard
    # fb = H_i - (rho_i*H_i + rho_s*H_s)/rho_w 

    # Forcings

    # F_sw_net = param['F_sw_net'][t]
    # Get longwave radiation
    # F_lw_net = param['F_lw_net'][t]
    # Get latent heat flux
    # F_lh = param['F_lh_in'][t]
    # Prepare sensible heat flux
    # Need to assign the transfer function for sensible heat flux:
    # f_sh = rho_a * c_{p,a} * c_{sh} * Wind speed
    # Wd_10m = param['F_wind10_in'][t]
    f_sh = 1.22 * 1005 * 1.75 * 10**(-3) * Wd_10m # [W m^{-2}]
    # Also assign air temperature
    # T_a2m =  param['T_a_in'][t] #+ TK2C # [K]


    fb = H_i - (H_i*rho_i - H_s*rho_s)/rho_w

    if fb >= 0:
        H_sdry = H_s 
        # fb = H_i - (rho_i*H_i + rho_s*H_sdry)/rho_w 
        dHsi_dt = 0 # no flooding layer development
        H_si = H_si_[t-1]

      # Semtner model begins here
        # -------------------------------

        # Conductive heat flux denominator (2-layer ice and snow)
        # F_c_denom = H_i/k_i + H_s/k_s
        F_c_denom = (H_i+H_si)/k_i + H_sdry/k_s
        # Solve for T_s using surface flux balance and conductive heat flux
        # T_s = (F_c_denom*f_sh*T_a2m + T_w - F_c_denom*(F_sw_net + F_lw_net)) / (F_c_denom*f_sh + 1)
        T_s = T_air[t]

        ########### Surface heat budget
       
        # Case 1: Snow surf temp > 0 - not physical, so set it to 0. This causes an imbalance between the net upward fluxes and the conductive heat flux in the snow, leading to surface melt
        if T_s>0.0:
            T_s = 0
            # Calculate the new conductive heat flux
            F_c = (T_s - T_w) / F_c_denom # New conductive flux with surface ice temperature Tia=0
            # F_s = ()
            F_surf = (F_sw_net[t] + F_lw_net[t] + f_sh[t] * (T_air)[t])

            # If there is no snow on the ice, the snow-ice surface will melt by amount given bu the residual flux balance
            # if H_sdry <0.005:
                # dHsi_dt = (F_surf - F_c)/q_ice

            # If there is no snow-ice, then the ice surface will melt by the rest of the residual
            # if (H_si + dHsi_dt*dt) <= 0:
                # dHice_dt_top = (H_si + dHsi_dt*dt)/dt

        else:
            F_c = (T_s - T_w) / F_c_denom
            dHice_dt_top = 0.0  # No ice melt at surface


        ####### Bottom Heat Budget
        # The balance between the ice-ocean flux and the conductive flux.
        dHice_dt_bot = -(F_c - F_w) / q_ice  # Negative sign b/c z is positive downwards (neg F_c means ice growth)
        # Done with the bottom budget

        ####### Total Heat Budget
        # Sum top and bottom growths
        dHice_dt = dHice_dt_bot + dHice_dt_top

        # Recalculate fb for this time step
        fb = (H_i + H_si) - (rho_i*(H_i + H_si) + rho_s*H_sdry)/rho_w 

        H_i = H_i + dHice_dt*dt


    if fb < 0:
        H_sdry = (H_i + H_si)*(rho_w - rho_i)/rho_s
        H_si = (H_i*(rho_i - rho_w) + H_s*rho_s)/(rho_w - (1/3)*rho_i)

    # Assign outputs
    # -------------------
    # F_c_[t] = F_c
    # T_s_[t] = T_s 
    H_i_[t] = H_i 
    H_si_[t] = H_si 
    # H_s_new_[t] = H_s_new
    fb_[t] = fb
    dHice_dt_[t] = dHice_dt 
    # dHsnow_dt_[t] = dHsnow_dt
    H_sdry_[t] = H_sdry



# plt.close('all')

t = H_s_.time.values

fig,axx = plt.subplots(nrows=2,sharex=True,figsize=(10,10), facecolor='w')


axx[0].plot(t,-H_i_,color='mediumblue')
hIce = axx[0].fill_between(t,-H_i_,0,color='mediumblue',alpha=0.2)

# axx[0].errorbar(x=mbs_snow.index,y=mbs_snow.Mean,yerr=mbs_snow.Std,color='gray',capsize=capsz,fmt='o')
# axx[0].plot(mbs_snow.Min,color='gray',linestyle='--')
# axx[0].plot(mbs_snow.Max,color='gray',linestyle='--')
axx[0].plot(t,H_sdry_+H_si_,color='gray')
hSnow = axx[0].fill_between(t,H_si_,H_sdry_+H_si_,color='gray',alpha=0.2)
# axx[0].plot(t,H_s_new_,color='magenta')


axx[0].plot(t,H_si_,color='cornflowerblue')
hFlood = axx[0].fill_between(t,0,H_si_,color='cornflowerblue',alpha=0.2)
# hSlush = axx[0].fill_between(t,0,H_slush_,color='midnightblue',alpha=0.5)

# axx[0].plot(mbs_ice.index,np.zeros(len(mbs_ice.index)),'k',linewidth=0.5)

axx[0].set_ylabel('Vertical distance [m]')
axx[0].set_title('Evolution of the Snow & Ice')











