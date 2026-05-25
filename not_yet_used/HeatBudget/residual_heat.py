'''
Some analyses on determining the residual heat flux components
First run heatbudget.py to load all variables

'''

# --------- Residual heat components ------------

##############################################
# 1) heat used to melt ice and snow (F_snowmelt) 
##############################################

# Total amount of snow loss over the seson 
# Li & Pomeroy (1997): threshold for snow transport by wind: 10 m/s for wet snow, 7.7 m/s for dry snow
U_wd_thresh = 7.7 # m/s
U_wd_daily_max = U_wd_10m_hourly.resample(time='1D').max()
dH_snow_loss = snow_air.diff(dim='time').where(H_snow.diff(dim='time') < 0,other=0)
# Assume most of snow loss is wind swept, so only a fraction is actually from melt
melt_frac = 0.12


# If the wind is blowing harder than the threshold, then only a fraction is melted. Ths fraction is a guess..
melt_frac_bool = xr.where(U_wd_daily_max >= U_wd_thresh,melt_frac,1)
# Index melt_frac_bool so the winds are in line with the day that melting is happening
# And say that only melt occurs when F_net < 0 
dH_snow_melt = dH_snow_loss.where(F_net_surf[0:-1].values < 0, 0)*(melt_frac_bool)#[0:-1].values)

# How much melt would occur if no residual?
dHs_dt = -F_net_surf/(rho_s*L_ice)


# Ice loss (100% due to melting) at the surface only
# Use smoothed snow-ice surface for melt rate
dH_ice_melt = snow_ice_smoothed.diff(dim='time').where(snow_ice_smoothed.diff(dim='time') < 0,other=0)

dt_ice = (6*60*60)
dt_snow = (24*60*60)

# Make up a density for snow-ice: say it's in between rho_i and rho_s
rho_si = 600

# Fluxes for snow and ice melt
# Should be positive (I think) 
# Li & Pomeroy (1997): threshold for snow transport by wind: 10 m/s for wet snow, 7.7 m/s for dry snow
F_snowmelt = xr.zeros_like(snow_air)
F_snowmelt[0:-1] = (rho_s*L_ice*dH_snow_melt/dt_snow).resample(time='1D').mean('time').values


# Assume the ice melted is snow-ice, and can only occur if there is no snow
F_icemelt = (rho_si*L_ice*dH_ice_melt/dt_ice).resample(time='1D').mean('time').where(H_snow == 0, 0)

# -------- Calculate the residual ------------

# Snowmelt is sketchy, probably most of the snow was blown away from wind. Can't quantify how much was actually melted..
DIFF = F_net_surf - F_icemelt - F_snowmelt 

# ROlling average
i = 5
DIFF_roll = F_net_surf.rolling(time=i,center='True').mean() - F_icemelt.rolling(time=i,center='True').mean() - F_snowmelt.rolling(time=i,center='True').mean() 


# ------ Fraction of residual heat that coincide with rain events --------#

# Load rain data
filepath = './Weather/data/2024/postville_weather_2020-2024.csv'
file = pd.read_csv(filepath,low_memory=False)

# Shortcut to just loading rain data
rain_mm = IMS.load_Rway_station_data(file,'rain').sel(time=slice('2024-01-26','2024-04-15'))
# Timeseries of when rainfall != 0
rain_non0 = rain_mm.where(rain_mm>0,drop=True)


# Times where the residual falls outside uncertainty range
outside_residual = DIFF_roll.where(DIFF_roll < -sig_F_surf_roll.values)

rain_residual = outside_residual.sel(time=rain_days)

# Percent of time that rain lines up with residual that falls outside uncertainty
frac_rain_residual = rain_residual.dropna('time').size/outside_residual.dropna('time').size

# Convert the fraction to heat (MJ/m^2)
heat_rain_MJ = np.sum(rain_residual*(86400/1000000)) # 86,4000 s/day/1,000,000 J/MJ

heat_residual_MJ = np.sum(outside_residual*(86400/1000000)) # 86,4000 s/day/1,000,000 J/MJ

frac_rain_residual_MJ = heat_rain_MJ/heat_residual_MJ


