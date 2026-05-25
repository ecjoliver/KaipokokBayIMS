'''
Run ice growth model for heat budget manuscript using ERA5 data
'''


import numpy as np
from scipy.optimize import root_scalar
import matplotlib.pyplot as plt
import tqdm
import xarray as xr
from datetime import datetime 
from functions import IMS_toolbox as IMS
import matplotlib.pyplot as plt 
import scipy
import pandas as pd
import tqdm
from scipy import stats
import matplotlib.dates as mdates
from pathlib import Path
plt.ion()

# --- Load ERA5 data ---

# yearStart = 2023; yearEnd = 2024; years = np.arange(yearStart,yearEnd+1); #n_years = len(years); months = np.array(['09','10','11','12','01','02','03','04','05','06','07','08']); n_months = len(months);  
# domain = [54.9,-59.8+360,55,-59.6+360] # S,W,N,E

# # Construct list of filepaths to load
# fname = []
# # var_s = ['MSLP','T2M','U10','V10']; varname_s = ['msl','t2m','u10','v10']
# var_s = ['T2M','U10','V10','STRD','SSRD']
# varname_s = ['t2m','u10','v10','strd','ssrd']

# for var in var_s:
#     path = Path('/home/oliver/data/ERA/ERA5/' + var)
#     for yr in years:
# #         print(var, yr)
#         fname.append(path / 'ERA5_{}_{}.nc'.format(var,yr))
        
# ds = xr.open_mfdataset(fname)
# # Slice in time - sept to sept
# # ds = ds.sel(time=slice(datetime(yearStart,1,1), datetime(yearEnd,3,18)))
# # Slice in space - Labrador Sea
# ds = ds.sel(latitude=slice(domain[2],domain[0]), longitude=slice(domain[1],domain[3]))

# # Load dataset into memory. Takes a while but makes plotting much faster
# ds.load()

ds = xr.open_dataset('HeatBudget/ERA5_vars_2024.nc')
ds = ds.rename({'valid_time':'time'})
ds = ds.sel(time=slice('2023-10-01','2024-07-01'))

# ---- Load snow depth from Postville Airport ---- 

filepath = './Weather/data/2024/postville_weather_2020-2024.csv'
file = pd.read_csv(filepath,low_memory=False)
H_s_obs = IMS.load_Rway_station_data(file,'snow_depth').resample(time='1H').mean()


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



# --- Extract variables ---
# Wind speed
U = xr.ufuncs.sqrt(ds['u10']**2 + ds['v10']**2)
# Air temp
T_a = ds['t2m']
# Radiation
LWin = ds['strd'] / 3600 # convert to W/m^2
T_s_obs = T_a 
LWout = sigma*(T_s_obs)**4
albedo = 0.8
SWin = ds['ssrd'] / 3600
SWout = SWin*albedo
# F_w = np.zeros(len(U))
F_w = Fw_quad.mean()

forc=xr.Dataset(coords={"time": ds.time})
forc['U'] = U
forc['T_a'] = T_a 
forc['LWnet'] = -(LWout - LWin)
forc['T_s_obs'] = T_s_obs
forc['SWnet'] = -(SWout - SWin)
forc['H_s_obs'] = H_s_obs 
forc['T_b'] = -0.75 + 273.15
forc['F_ocean'] = F_w

# --- Set up model inputs ---

param=dict()
param['L_ice'] = L_ice 
param['rho_i'] = rho_i 
param['rho_s'] = rho_s 
param['rho_w'] = rho_w 
param['rho_fw'] = rho_fw
param['k_i'] = k_i 
param['k_s'] = k_s 
param['c_p'] = c_p 
param['c_fw'] = c_fw


# 2024: On January 4, Samantha sent an e-mail with a satellite image saying "the bay is starting to freeze". Looks like grey ice starting to form. 
# On January 10 there was over 20 cm in most places along the bay 
# H_i_init = 0.2
H_i_init = 0.001

t_start = '2023-12-01'
t_end = '2024-04-20'

# --- Run model ---

result = Semtner2Fc(forc,param,H_i_init,t_start,t_end,USE_RAIN=False,USE_OCEAN_HEAT=True,p=1)


# Plot results
plt.figure()
(result['H_i']).plot()
(-H_bottom).plot()


plt.savefig('Figures/HeatBudget/ERA5_run2.png',dpi=400,bbox_inches='tight')




# --- MODEL CODE -----

def Semtner2Fc(forcings, parameters, H_i_init, t_start, t_end, USE_OCEAN_HEAT=True,USE_SNOW_ICE=True,USE_RAIN=True,USE_MELT=True,p=1):
	
    forc = forcings.sel(time=slice(t_start,t_end))
    nt = len(forc.time)
    result = xr.Dataset(coords={"time": forc.time})
    dt = 3600 

    # --- Set up variable shortcuts ----

    k_i = param['k_i']
    k_s = param['k_s']
    L_ice = param['L_ice']
    rho_i = param['rho_i']
    rho_s = param['rho_s']
    rho_fw = param['rho_w']
    c_fw = param['c_fw']
    H_s_ = forc['H_s_obs'].values
    T_b = forc['T_b'].values
    T_s_obs = forc['T_s_obs'].values

    # ---- Set up output vars ---
    F_c_ice_ = np.zeros(nt)
    H_i_ = np.zeros(nt) # Ice thickness without snow-ice
    h_i_ = np.zeros(nt) # Ice thickness with snow-ice
    h_si_ = np.zeros(nt)
    h_s_ = np.zeros(nt)
    fb_ = np.zeros(nt)
    H_melt = np.zeros(nt)
    R = np.zeros(nt)

    # ---- Initial conditions ---- 
    H_si = 0  # Initial snow-ice thickness [m]
    T_si = T_s_obs[0] # Initial ice surface temp. 
    F_s = 0 # Initial net surface heat flux
    F_c_s = 0 # Initial conductive heat flux at the surface
    H_s = H_s_*p
    h_s = H_s[0] - H_si # Initial snow thickness for model [m]
    h_i = H_i_init + H_si 
    H_i = H_i_init
    fb = (h_i) - (rho_i*h_i + rho_s*h_s)/rho_w

    snow_ice_factor = 1 # How much to multiply snow-ice production by
    count=0


    for n in tqdm.tqdm(range(nt)):
    	# New condition: since airport weather station tracks snow depth on land, if there is no ice, set snow to zero 
        if h_i < 0.1:
            H_s[n] = 0

        # Compute A and B for conductive flux through snow
        # From substituting eq for T_si into eq. for F_s, then simplifying into a linear function of T_s
        denom = k_s * h_i + k_i * h_s
        A = (k_s / h_s) * (k_i * h_s / denom)
        B = (k_s / h_s) * (k_i * h_s * T_b / denom)
        # Define net surface flux function as function of T_s
        def net_surface_flux(T_s):
            F_s = 0
            F_s += forc['SWnet'][n] # Positive
            # Linearize T^4 term around T = 273.15 K (0 C)
            F_s += forc['LWnet'][n]
            # F_s += F_lw_down[n] - epsilon * sigma * (273.15**4 + 4 * 273.15**3 * (T_s - 273.15))
            F_s += IMS.sensible_heat_flux(forc['U'][n],T_s,forc['T_a'][n])
            # F_s += IMS.latent_heat_flux(U[n], RH[n], P[n], T_s, T_a[n])
            if USE_RAIN == True:
                T_r = forc['T_a'][n]
                # R is the heat input by rain when rain falls on snow at the freezing point
                # For snowpack at the freezing point:
                if T_s >= 273.15:
                    R[n] = rho_fw*c_fw*forc['rain_rate'][n]*(T_r - 273.15)
                # For snowpack below the freezing point:
                if T_s < 273.15:
                    R[n] = rho_fw*c_fw*forc['rain_rate'][n]*(T_r - 273.15) + rho_fw*L_ice*rain_rate[n]
                F_s += R[n]

            # Add conductive flux through snow (linearized)
            F_c_s = -A * T_s + B
            F_s -= F_c_s
            return F_s, F_c_s, R

        fb = (h_i) - (rho_i*(h_i) + rho_s*h_s)/rho_w
        if USE_SNOW_ICE:
            if fb >= 0: 
                H_si += 0 # No additional snow-ice formation

            # Manually set snow-ice formation onset date
            elif fb < 0 and forc.time[n] >= np.datetime64('2024-03-01'):#snow_ice_onset:
                # New freeboard which includes the weight of water
                # fb = 1/(1-vl*df)*((h_i) - (rho_i*(h_i) + rho_s*(h_s))/rho_w) # freeboard with flooding,  including refrozen snow-ice
                # H_sdry = h_s + fb # Dry snow with flooding, Mahoney 2021
                # H_sl = -fb
                # Cumulative snow-ice thickness, Mahoney et al. 2021
                # H_si += snow_ice_factor*(-vl)*dt*(1/(rho_i*L_i))*((H_si + H_sdry)/(H_si/k_i + H_sdry/k_s))*((T_s - T_si)/(H_si + H_sdry)) 
                
                # Snow ice with Fc over slush and dry snow
                # k_eff = k_sl
                # k_eff = (H_sl + H_sdry)/(H_sl/k_sl + H_sdry/k_s)
                # H_si_n = (-vl)*dt*(1/(rho_sl*L_i))*(k_eff)*((T_s - T_si)/(H_sl + H_sdry)) 
                # Snow ice with Fc over dry slush layer only
                # H_si_n = (-vl)*dt*(k_sl/(rho_sl*L_ice))*((T_s - T_si)/(H_s[n] - fb))
                # H_si += H_si_n
                # Kirillov 2015 model 
                H_sdry = (H_i + H_si)*(rho_w - rho_i)/rho_s
                H_si += (h_i*(rho_i - rho_w) + h_s*rho_s)/(rho_w - (1/3)*rho_i)

        T_s = T_s_obs[n]
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
        T_si = (k_s * h_i * T_s + k_i * h_s * T_b) / (k_s * h_i + k_i * h_s)

        # Conductive flux through ice
        F_c_ice = k_i * (T_si - T_b) / h_i

        # Update ice thickness
        F_bot = -F_c_ice - (forc['F_ocean'].values if USE_OCEAN_HEAT else 0)
        dH_i_dt = F_bot / (rho_i * L_i)
        H_i += dH_i_dt * dt

        # Add snow ice to ice thickness
        h_i = H_i + H_si
        h_s = H_s[n] - H_si

        # Save outputs
        H_i_[n] = H_i
        F_c_ice_[n] = F_c_ice
        h_si_[n] = H_si
        h_i_[n] = h_i
        h_s_[n] = h_s
        fb_[n] = fb

    result = IMS.add_to_dataset(result, "H_i",H_i_,attrs={"long_name":"Sea ice thickness (congelation ice)"})
    result = IMS.add_to_dataset(result, "H_si",h_si_,attrs={"long_name":"Snow ice thickness"})
    result = IMS.add_to_dataset(result, "h_i",h_i_,attrs={"long_name":"Total ice thickness (sea ice + snow ice)"})
    result = IMS.add_to_dataset(result, "H_s",h_s_,attrs={"long_name":"Snow depth without snow ice"})
    result = IMS.add_to_dataset(result, "fb",fb_,attrs={"long_name":"Freeboard"})
    result = IMS.add_to_dataset(result, "F_c_ice",F_c_ice_,attrs={"long_name":"Conductive heat flux through ice"})
    result = IMS.add_to_dataset(result, "H_melt",H_melt,attrs={"long_name":"Meltwater (SWE)"})

    return result

