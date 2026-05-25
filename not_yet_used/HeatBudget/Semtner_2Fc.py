'''
Best ice growth model based on Semtner (1976) with Mahoney et al. 2021 and/or Kirillov et al. 2015 snow-ice formation. 

'''


import numpy as np
from scipy.optimize import root_scalar
import matplotlib.pyplot as plt
import tqdm
from datetime import datetime 
from functions import IMS_toolbox as IMS
import matplotlib.pyplot as plt 
import scipy
import pandas as pd
import tqdm
from scipy import stats
import matplotlib.dates as mdates
from pathlib import Path


# Convert to xarray
def convert2da(sol,begT,endT,params=None,time_origin=0):
    # spinup time
    
    """Create a xarray.DataArray from the Semtner model outputs."""
    # Bulk of the function
    ds_sol = xr.Dataset(coords={'time': T_air.sel(time=slice(begT,endT)).time},
                        data_vars={'H_i': ('time',sol)}
                                   
                       )
    # Then assign some attributes to describe the solution
    ds_sol['H_i'].attrs['name'] = 'Thickness'
    ds_sol['H_i'].attrs['long_name'] = 'Sea Ice Thickness'
    ds_sol['H_i'].attrs['units'] = 'm'

    return ds_sol


# ----- Prepare data -----
# begT = np.datetime64('2024-01-26')
begT = np.datetime64('2024-02-03') # 12 days after SIMBA deployment
endT = np.datetime64('2024-04-15')

filepath = './Weather/data/2024/postville_weather_2020-2024.csv'
file = pd.read_csv(filepath,low_memory=False)
# Shortcut to just loading rain data
rain_m = IMS.load_Rway_station_data(file,'rain').resample(time='1H').mean('time').sel(time=slice(begT,endT)).fillna(0)/1000
rain_mm = IMS.load_Rway_station_data(file,'rain').sel(time=slice('2024-01-26','2024-04-15'))
rain = rain_mm/1000 # in meters
# rain_rate = rainfall rate
rain_rate = (rain/(60*60)).fillna(0) # convert from m/h to m/s 


# Load the weekly snow time series, and adjust the values to represent FRESH snow (not snow stakes)
weekly_ice = xr.open_dataset('SiteVisits/weekly_ice_2024.nc')

# Load temperature data
with open('./SIMBA/da_temp_z.pickle','rb') as f:
    da_temp = pd.read_pickle(f)


F_sw_net = ds_weather['RsNet_Avg'].resample(time='1H').mean('time').sel(time=slice(begT,endT))
F_lw_net = ds_weather['RlNet_Avg'].resample(time='1H').mean('time').sel(time=slice(begT,endT))
LWin = ds_weather['LWUpperCo_Avg'].resample(time='1H').mean('time').sel(time=slice(begT,endT))
LWout = ds_weather['LWLowerCo_Avg'].resample(time='1H').mean('time').sel(time=slice(begT,endT))
U_wd = ds_weather['WS_ms_Avg'].resample(time='1H').mean('time').sel(time=slice(begT,endT)) # wind speed
T_air = ds_weather['AirT_C_Avg'].resample(time='1H').mean('time').sel(time=slice(begT,endT))
RH = ds_weather['Humidity'].resample(time='1H').mean('time').sel(time=slice(begT,endT))
P = ds_weather['BP_mbar_Avg'].resample(time='1H').mean('time').sel(time=slice(begT,endT))
epsilon = 0.985
sigma = 5.67e-8
T_s_obs = (((LWout - (1-epsilon)*LWin)/(epsilon*sigma))**0.25 - 273.15)

# Get the under-ice ocean tmperature from SIMBA data
valid = H_bottom.dropna(dim='time').resample(time='1D').mean() # Hacky - resample daily so time indices work out
da_temp_h = da_temp.resample(time='1D').mean()
DD = da_temp_h.where(da_temp_h.time==valid.time)
oce_surf = DD.sel(z=valid-0.04,method='nearest') # surface temp - 2 nodes below the ice bottom
oce_surf_1h = oce_surf.sel(time=slice(begT,endT)).resample(time='1H').interpolate('linear')

# # Snow thickness, upsample to hourly
snow_air_interp = snow_air.sel(time=slice(begT,endT)).resample(time='1H').interpolate('linear')
# # Interpolate the ends to fill nans
snow_air_interp_ = snow_air_interp.interpolate_na(dim='time',method='nearest',fill_value="extrapolate")
# # Dry snow observations
# H_sdry_obs = (snow_air - snow_ice).resample(time='1H').interpolate('linear')
# Timing of when snow-ice formation begins in the SIMBA data. Use this date later to manually begin snow-ice formation
arg = snow_ice.where(snow_ice>0).argmin()
snow_ice_onset = snow_ice[arg].time

# --- Constants ---
L_ice = 333000           # latent heat of fusion for sea ice [J/kg]
sigma = 5.67e-8          # Stefan-Boltzmann constant [W/m²/K⁴]
epsilon = 0.98           # Emissivity of surface
rho_i = 917              # Ice density [kg/m³]
rho_s = 330              # kg/m3 - snow density
rho_w = 1027             # kg/m3 - seawater density
rho_fw = 1000            # kg/m3 - freshwater density
rho_sl = 1.5*rho_s       # kg/m3 - infiltrated snow (slush) density; Eicken (1995)
c_fw = 4186              # J/kgC - heat capacity of freshwater
L_i = 3.3e5              # Latent heat of fusion [J/kg]
k_s = 0.39               # Thermal conductivity of snow [W/m/K], Sledd et al. (2024)
k_i = 2.3                # Thermal conductivity of ice [W/m/K]
k_sl = 2.03              # Thermal conductivity of snow-ice with 900 density [W/m/K], Schwerdtfecer(1963)
c_p = 1005               # Specific heat of air [J/kg/K]
L_v = 2.5e6              # Latent heat of vaporization [J/kg]
vl = 0.65                # liquid volume fraction of flooded snow (Mahoney et al. 2021; typically 0.65)
df = 1                   # Fractional flooded depth of negative freeboard
q_ice = 300*1e6          # Ice specific latent heat of fusion [J/m^3] 

# --- Model parameters ---
C_H = 0.0015             # Sensible heat exchange coefficient
C_E = 0.0010             # Latent heat exchange coefficient
rho_air = 1.3            # Air density [kg/m³]

# --- Forcing (can be time series) ---
T_a = T_air + 273.15     # Air temperature [K]
F_sw = F_sw_net          # Shortwave radiation [W/m²]
F_lw_down = LWin         # Downwelling longwave [W/m²]
U = U_wd*(10/2)**(1/7)   # 10m Wind speed [m/s]

#---- Outputs to save ---

nt = len(T_a)
T_s_ = np.zeros(nt)
T_si_ = np.zeros(nt)
F_c_ice_ = np.zeros(nt)
H_i_ = np.zeros(nt) # Ice thickness without snow-ice
h_i_ = np.zeros(nt) # Ice thickness with snow-ice
dh_i_ = np.zeros(nt)
h_si_ = np.zeros(nt)
h_s_ = np.zeros(nt)
fb_ = np.zeros(nt)
dHsif_dt_ = np.zeros(nt)
F_net = np.zeros(nt)
H_melt = np.zeros(nt)
F_c_surf_ = np.zeros(nt)
R = np.zeros(nt)
H_slush_ = np.zeros(nt)

# --- Initial conditions ---
H_s_obs = snow_air_interp_.sel(time=slice(begT,endT))
# H_s[:600] = snow_air_interp_[:600]*0.5
# T_b = -0.75 + 273.15     # Ice bottom temperature (seawater freezing)
T_b = oce_surf_1h.sel(time=slice(begT,endT)) + 273.15
dt = 3600                # Time step [s]
nt = len(T_a)            # Number of time steps
time = np.arange(nt) * dt / 3600  # in days
# h_i = np.zeros(nt)
H_i = 0.36              # Initial ice thickness [m]
H_si = 0                # Initial snow-ice thickness [m]
T_s = T_air[0] # initial condition for T_s
T_si = T_s
h_i = H_i + H_si 
h_s = H_s_obs[0] - H_si # Initial snow thickness for model [m]
fb = (H_i) - (rho_i*H_i + rho_s*h_s)/rho_w 
F_s = 0

# --- Flux toggles ---  
USE_SW = True
USE_LW = True
USE_SENS = True
USE_LAT = True
USE_OCEAN_HEAT = True
USE_SNOW_ICE = False
USE_MELT = True
USE_RAIN = True


F_ocean = Fw_quad.resample(time='1H').mean('time').sel(time=slice(begT,endT))  # W/m^2
F_ocean[0] = F_ocean[1]

# percents = np.linspace(0.1,1,10)
# percents = [0.6,0.8,1,1.2,1.4]#,1.6,1.8,2]
percents = [0,0.2,0.4,0.6,0.8,1,1.2,1.4,1.6,1.8,2]

# p=1

# Fraction of snow cover
# for i,p in enumerate(percents):
#     print('Running for fraction', p)
    # --- Initial conditions ---

    # H_i = 0.36            # Initial ice thickness on Jan. 26 [m]
    H_i = 0.48              # Initial ice thickness on Feb. 3 [m]
    H_si = 0                # Initial snow-ice thickness [m]
    T_si = T_s
    F_s = 0
    F_c_s = 0

    H_s = H_s_obs*p
    h_s = H_s[0] - H_si # Initial snow thickness for model [m]
    h_i = H_i + H_si 
    fb = (H_i) - (rho_i*H_i + rho_s*h_s)/rho_w
    H_sl = 0

    H_i_ = np.zeros(nt) # Ice thickness without snow-ice
    h_si_ = np.zeros(nt)

    snow_ice_factor = 1 # How much to multiply snow-ice production by
    count=0
    for n in tqdm.tqdm(range(nt)):


        # Compute A and B for conductive flux through snow
        # From substituting eq for T_si into eq. for F_s, then simplifying into a linear function of T_s
        denom = k_s * h_i + k_i * h_s
        A = (k_s / h_s) * (k_i * h_s / denom)
        B = (k_s / h_s) * (k_i * h_s * T_b[n] / denom)
        # Define net surface flux function as function of T_s
        def net_surface_flux(T_s):
            F_s = 0
            if USE_SW:
                F_s += F_sw[n] # Positive
            if USE_LW:
                # Linearize T^4 term around T = 273.15 K (0 C)
                F_s += F_lw_net[n]
                # F_s += F_lw_down[n] - epsilon * sigma * (273.15**4 + 4 * 273.15**3 * (T_s - 273.15))
            if USE_SENS:
                F_s += IMS.sensible_heat_flux(U[n],T_s,T_a[n])
            if USE_LAT:
                # F_s += rho_air * L_v * C_E * U[n] * (q_a - q_s)
                F_s += IMS.latent_heat_flux(U[n], RH[n], P[n], T_s, T_a[n])
            if USE_RAIN:
                T_r = T_a[n]
                # R is the heat input by rain when rain falls on snow at the freezing point
                # For snowpack at the freezing point:
                if T_s >= 273.15:
                    R[n] = rho_fw*c_fw*rain_rate[n]*(T_r - 273.15)
                # For snowpack below the freezing point:
                if T_s < 273.15:
                    R[n] = rho_fw*c_fw*rain_rate[n]*(T_r - 273.15) + rho_fw*L_ice*rain_rate[n]
                F_s += R[n]

            # Add conductive flux through snow (linearized)
            F_c_s = -A * T_s + B
            F_s -= F_c_s
            return F_s, F_c_s, R

        fb = (h_i) - (rho_i*(h_i) + rho_s*h_s)/rho_w
        if USE_SNOW_ICE:
            if fb >= 0: 
                H_si += 0 # No additional snow-ice formation
                H_slush = 0

            # Manually set snow-ice formation onset date
            elif fb < 0 and T_a.time[n] >= np.datetime64('2024-03-01'):#snow_ice_onset:
                # New freeboard which includes the weight of water
                # fb = 1/(1-vl*df)*((h_i) - (rho_i*(h_i) + rho_s*(h_s))/rho_w) # freeboard with flooding,  including refrozen snow-ice
                # H_sdry = h_s + fb # Dry snow with flooding, Mahoney 2021
                # H_sl += -fb
                # # Cumulative snow-ice thickness, Mahoney et al. 2021
                # H_si += snow_ice_factor*(-vl)*dt*(1/(rho_i*L_i))*((H_si + H_sdry)/(H_si/k_i + H_sdry/k_s))*((T_s - T_si)/(H_si + H_sdry)) 
                
                # Snow ice with Fc over slush and dry snow
                # k_eff = k_sl
                # k_eff = (H_sl + H_sdry)/(H_sl/k_sl + H_sdry/k_s)
                # H_si_n = (-vl)*dt*(1/(rho_sl*L_i))*(k_eff)*((T_s - T_si)/(H_sl + H_sdry)) 
                # Snow ice with Fc over dry slush layer only
                # H_si_n = (-vl)*dt*(k_sl/(rho_sl*L_ice))*((T_s - T_si)/(H_s[n] - fb))
                # H_si += H_si_n
                # Kirillov 2015 model 
                h_s_p = h_s + fb
                H_sdry = (H_i + H_si)*(rho_w - rho_i)/rho_s
                H_si += (h_i*(rho_i - rho_w) + h_s*rho_s)/(rho_w - (1/3)*rho_i)

                # H_slush = (-fb) - H_si_n

        T_s = T_s_obs[n] + 273.15
        F_s, F_c_s, R = net_surface_flux(T_s)
        if T_s > 273.15: #and F_s > 0:
            T_s = 273.15
        # if F_s > 0:
            if USE_MELT:
                H_m = F_s/(rho_s*L_ice)*dt
                if H_s[n] > H_si:# and F_s > 0: # only when there is snow to melt
                    # Snow-ice formed from meltwater
                    # H_m = F_s/(rho_s*L_ice)*dt
                    H_m = F_s/(rho_fw*L_ice)*dt # SWE
                    H_melt[n] = min(H_m,H_s[n] - H_si) # Max amount of melt is the amount of snow available
                    H_si += H_melt[n]
                if H_s[n] <= H_si: # If the top of the dry snow is lower than snow ice, melt snow ice
                    H_m = F_s/(rho_i*L_ice)*dt
                    H_si -= H_m # Melt snow-ice 
                    H_melt[n] = H_m  

        if USE_MELT and USE_RAIN:
            if T_s < 273.15 and R[n] > 0:
                if H_s[n] > H_si:
                    H_m = R[n]/(rho_s*L_ice)*dt 
                    H_melt[n] = min(H_m,H_s[n] - H_si) # Max amount of melt is the amount of snow available
                    # H_si += H_melt[n]
                if H_s[n] <= H_si:
                    H_m = R[n]/(rho_s*L_ice)*dt 
                    H_si -= H_m
                    H_melt[n] = H_m

        if T_s < 273.15 and R[n] < 0:
            # F_s = 0
            H_melt[n] = 0
            H_si += 0

        # Snow-ice formed from rain
        if USE_RAIN:
            H_si += rain_m[n]

        # Compute T_si (snow/snow-ice interface temperature)
        T_si = (k_s * h_i * T_s + k_i * h_s * T_b[n]) / (k_s * h_i + k_i * h_s)

        # Conductive flux through ice
        F_c_ice = k_i * (T_si - T_b[n]) / h_i

        # Update ice thickness
        F_bot = -F_c_ice - (F_ocean[n] if USE_OCEAN_HEAT else 0)
        dH_i_dt = F_bot / (rho_i * L_i)
        H_i += dH_i_dt * dt

        # Add snow ice to ice thickness
        h_i = H_i + H_si
        h_s = H_s[n] - H_si

        # Save outputs
        H_i_[n] = H_i
        T_s_[n] = T_s
        T_si_[n] = T_si
        F_c_ice_[n] = F_c_ice
        dh_i_[n] = dH_i_dt
        h_si_[n] = H_si
        h_i_[n] = h_i
        h_s_[n] = h_s
        fb_[n] = fb
        F_net[n] = F_s
        F_c_surf_[n] = F_c_s
        # H_slush_[n] = H_slush

    ds_H_si = IMS.add_to_dataset(ds_H_si, f"H_si_{p}",h_si_,attrs={"long_name":f"H_si with snow fraction: {p}"})
    ds_H_i = IMS.add_to_dataset(ds_H_i, f"H_i_{p}",H_i_,attrs={"long_name":f"H_i with snow fraction: {p}"})

   # ds_H_i = IMS.add_to_dataset(ds_H_i, f"H_i_{p}",H_i_,attrs={"long_name":f"H_i with snow fraction: {p}"})
    # ds_H_si = IMS.add_to_dataset(ds_H_si, f"H_si_{p}",h_si_,attrs={"long_name":f"H_si with snow fraction: {p}"})

ds = xr.Dataset(coords={"time": T_air.time})
# From IMS_toolbox
# ds = IMS.add_to_dataset(ds, "H_i_full",H_i_,attrs={"long_name":"H_i full model"})
# ds = IMS.add_to_dataset(ds, "H_si_full",h_si_,attrs={"long_name":"H_si full model"})
# ds = IMS.add_to_dataset(ds, "H_si_noFw",h_si_,attrs={"long_name":"H_si with no Fw"})
# ds = IMS.add_to_dataset(ds, "H_i_noFw",H_i_,attrs={"long_name":"H_i with no Fw"})
ds = IMS.add_to_dataset(ds, "H_i_noFlood",H_i_,attrs={"long_name":"H_i with no snow ice"})
# ds = IMS.add_to_dataset(ds,"H_si_noFlood",h_si_,attrs={"long_name":"H_si with no flooding"})
# ds = IMS.add_to_dataset(ds, "H_si_noRain",h_si_,attrs={"long_name":"H_si with no rain"})
# ds = IMS.add_to_dataset(ds, "H_si_MeltOnly",h_si_,attrs={"long_name":"H_si from melt and rain only"})
ds_reg = IMS.add_to_dataset(ds_reg, "H_i_noFlood_noFw",H_i_,attrs={"long_name":"H_i with no snow ice and no Fw"})



ds_H_i = xr.Dataset(coords={"time": T_air.time})
ds_H_si = xr.Dataset(coords={"time": T_air.time})


ds_reg.to_netcdf('HeatBudget/Semtner2Fc_ModRuns_Kirillov.nc')

ds_H_i.to_netcdf('HeatBudget/Semtner2Fc_ModRuns_snowfrac_Hi_Kirillov.nc')
ds_H_si.to_netcdf('HeatBudget/Semtner2Fc_ModRuns_snowfrac_Hsi_Kirillov.nc')


#----- Plot the results---------

# plt.close('all')

t = H_s.time.values
fig,axx = plt.subplots(nrows=2,sharex=True,figsize=(10,10), facecolor='w')

# Plot ice
axx[0].plot(t,-H_i_,color='mediumblue')
hIce = axx[0].fill_between(t,-H_i_,0,color='mediumblue',alpha=0.2)
# Plot resulting snow
axx[0].plot(t,h_s_+h_si_,color='gray')
hSnow = axx[0].fill_between(t,h_si_,h_s_+h_si_,color='gray',alpha=0.2)
# axx[0].plot(t,H_s_new_,color='magenta')
# Plot snow ice
axx[0].plot(t,h_si_,color='cornflowerblue')
hFlood = axx[0].fill_between(t,0,h_si_,color='cornflowerblue',alpha=0.2)
axx[0].set_ylabel('Vertical distance [m]')
axx[0].set_title('Evolution of the Snow & Ice')

### Plot observations on top 
# Ice bottom 
hObs, = axx[0].plot(H_bottom.time,H_bottom,'r--',label='Ice bottom')

# Add individual observations of SLOB bsaed on site visit datasheets
H_si_obs = -(H_ice - H_bottom)
slob = axx[0].vlines(np.datetime64('2024-03-19').astype(datetime),H_si_obs.sel(time='2024-03-19').mean(),H_si_obs.sel(time='2024-03-19').mean() + 0.05, color='k',label='Slob thickness')
axx[0].vlines(np.datetime64('2024-03-26').astype(datetime),H_si_obs.sel(time='2024-03-26').mean() - 0.16, H_si_obs.sel(time='2024-03-26').mean(),color='k')
axx[0].vlines(np.datetime64('2024-04-02').astype(datetime),H_si_obs.sel(time='2024-04-02').mean() - 0.225, H_si_obs.sel(time='2024-04-02').mean(),color='k')

# Add SIMBA derived snow-ice (total ice thickness minus the draft)
hFloodObs, = axx[0].plot(H_si_obs.time,H_si_obs,'g--',label='Surface freezing (SIMBA)')

# Snow stakes
hSnowStakes, = axx[0].plot(snow_air.time,snow_air,c='yellow',label='Snow-air interface (SIMBA)')
# rand, = axx[0].plot(H_bottom.time,H_bottom,'g-',label='bb')
l1 = axx[0].legend([hSnow,hFlood,hIce],['Dry Snow','Snow-Ice','Sea Ice'],bbox_to_anchor=(1.17,0.9),title=r'Model')
l2 = axx[0].legend(handles=[hObs,slob,hFloodObs,hSnowStakes],bbox_to_anchor=(1.32,0.5),title='Observations')
axx[0].add_artist(l1)

# Observed freeboard
fb_obs = weekly_ice['Hice'] - weekly_ice['Waterlvl'] 

aa=axx[1].plot(t,fb_,'k-')
bb=axx[1].plot(fb_obs.time, fb_obs,'r^-')
axx[1].set_title('Freeboard comparisons')
l3 = axx[1].legend([aa,bb],labels=['model','observations'],fontsize=fontsize)
axx[1].set_ylabel('Freeboard [m]')
plt.xlim(['2024-01-26','2024-04-15'])

#
# plt.savefig('figures/HeatBudget/Semtner2Fc_Kirillov_noFw.png',dpi=300, bbox_inches='tight')
#