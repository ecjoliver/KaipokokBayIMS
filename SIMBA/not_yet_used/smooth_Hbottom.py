'''
Smooth the ice-water interface using smoothing spline
'''


import xarray as xr
from scipy.interpolate import splrep, splev
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib as mpl

# Load the pickle files
with open('SIMBA/ice_water_m.pickle','rb') as f:
    ice_water_m = pd.read_pickle(f)
with open('SIMBA/da_temp_z.pickle','rb') as f:
    da_temp = pd.read_pickle(f)

######## Smooth with runnnig mean - TWICE
ice_water_roll = ice_water_m.rolling(time=5,center='True').mean()
ice_water_roll_ = ice_water_roll.rolling(time=5,center='True').mean()
# interp to match 6H length
ice_water_smooth = ice_water_roll_.interp(time=da_temp.time,method='linear')

# Make ice_water_m variable that is on the same time axis as the ice_water_smooth
ice_water_m_interp = ice_water_roll_.copy()
ice_water_m_interp.data = ice_water_m
ice_water_m_interp = ice_water_m_interp.interp(time=da_temp.time,method='linear')


# Eric's alternative
from scipy.interpolate import make_smoothing_spline
x = np.arange(len(ice_water_m))
f = make_smoothing_spline(x, ice_water_m, lam=1000)
ice_water_spline = ice_water_roll_.copy()
ice_water_spline.data = f(x)
ice_water_spline_smooth = ice_water_spline.interp(time=da_temp.time,method='linear')

from scipy.interpolate import splrep, splev
ice_water_splrep = ice_water_roll_.copy()
f = splrep(x, ice_water_m, task=0, s=0.004) # 0.004 parameter tuned to remove osc's
ice_water_splrep.data = splev(x, f)
ice_water_splrep_smooth = ice_water_splrep.interp(time=da_temp.time,method='linear')

# And for calculating the latent heat of ice growth:
dH_dt_bot_m = ice_water_m_interp.differentiate('time',datetime_unit="s") # m/s
dH_dt_bot_roll_ = ice_water_smooth.differentiate('time',datetime_unit="s") # m/s
dH_dt_bot_spline = ice_water_spline_smooth.differentiate('time',datetime_unit="s") # m/s
dH_dt_bot_splrep = ice_water_splrep_smooth.differentiate('time',datetime_unit="s") # m/s

# latent heat from ice growth and decay at the bottom as in Semtner (1976)
L_ice = 333000  # J/m3 
rho_i = 910 #kg/m3 - sea ice density
F_l_spl = L_ice*rho_i*dH_dt_bot_splrep # where dH_dt is the BOTTOM ice growth rate; negative F_l means heat is being released from the ice to the ocean (ice growth)

## ---------- Clamped boundaries


# Convert time to seconds since epoch
x_dt = ice_water_m.time.values
x_all = pd.to_datetime(x_dt).astype(np.int64) / 1e9
y_all = ice_water_m.values

# Identify flat value and where it starts
clamp_value = -0.62
flat_start_idx = np.argmax(y_all == clamp_value)

# Taper region: how many points to blend spline into flat
taper_len = 20  # try 5–10 for smoothest effect
fit_end_idx = flat_start_idx + taper_len

# Split regions
x_fit = x_all[:fit_end_idx]
y_fit = y_all[:fit_end_idx]
x_flat = x_all[fit_end_idx:]
y_flat = np.full_like(x_flat, clamp_value)

# Fit smoothing spline to variable region + taper
f_smooth = splrep(x_fit, y_fit, s=0.004)
y_spline = splev(x_fit, f_smooth)

# Create taper weights: 1 → 0 over taper_len
# taper_weights = np.linspace(1, 0, taper_len)
# Cosine-shaped weights: smooth drop from 1 → 0
taper_weights = 0.5 * (1 + np.cos(np.linspace(0, np.pi, taper_len)))


# Apply taper to blend spline to flat
y_blended = y_spline.copy()
y_blended[-taper_len:] = (
    taper_weights * y_spline[-taper_len:] +
    (1 - taper_weights) * clamp_value
)

# Combine with final flat region
y_smooth_full = np.concatenate([y_blended, y_flat])

# Save to xarray
clamped = xr.DataArray(
    y_smooth_full,
    coords={"time": x_dt},
    dims=["time"],
    name="ice_water_smooth"
)

# Hard clamp boundaries
clamped_ = clamped.where(clamped>=-0.62,-0.62) 
# Rolling mean to smooth it out
clamped_roll = clamped_[40:70].rolling(time=5,center='True').mean()
clamped_[45:65] = clamped_roll[5:-5]

# Interpolate to 6H time grid
clamped_interp = clamped_.interp(time=da_temp.time, method='linear')

with open('./SIMBA/ice_water_spline_clamped.pickle','wb') as f:
    pickle.dump(clamped_interp, f)




dH_dt_bot_clamped = clamped_interp.differentiate('time',datetime_unit="s") # m/s

# latent heat from ice growth and decay at the bottom as in Semtner (1976)
L_ice = 333000  # J/m3 
rho_i = 910 #kg/m3 - sea ice density
F_l_clamped = L_ice*rho_i*dH_dt_bot_clamped # where dH_dt is the BOTTOM ice growth rate; negative F_l means heat is being released from the ice to the ocean (ice growth)
F_l_clamped.plot()



# #####


# import numpy as np
# import pandas as pd
# import xarray as xr
# from scipy.interpolate import splrep, splev

# # Convert time to float (seconds since epoch)
# x_dt = ice_water_m.time.values
# x_all = pd.to_datetime(x_dt).astype(np.int64) / 1e9
# y_all = ice_water_m.values

# # Step 1: Identify where -0.62 starts (first flat point)
# clamp_value = -0.62
# flat_start_idx = np.argmax(y_all == clamp_value)

# # Step 2: Define taper length and taper *before* clamp
# taper_len = 20  # Increase taper length for smoother transition
# taper_start_idx = max(flat_start_idx - taper_len, 0)

# # Step 3: Define fit region (up to clamp start)
# x_fit = x_all[:flat_start_idx]
# y_fit = y_all[:flat_start_idx]

# # Step 4: Fit smoothing spline with s=0.006 for smoothness
# f_smooth = splrep(x_fit, y_fit, s=0.004)  # Increase s for smoother spline
# y_spline = splev(x_all[:flat_start_idx], f_smooth)

# # Step 5: Create a smoother transition that doesn’t exceed 0 or overshoot
# # Cosine-shaped taper curve, ensuring smooth transition to clamp_value
# # taper_weights = 0.5 * (1 + np.cos(np.linspace(0, np.pi, taper_len)))
# # Step 5: Create logistic (sigmoid) taper weights
# x_taper = np.linspace(-3, 3, taper_len)  # More range = sharper transition
# taper_weights = 1 / (1 + np.exp(x_taper))  # Logistic curve from ~1 to ~0

# y_blended = y_spline.copy()

# # Ensure no overshoot: tapering is confined within the valid range.
# y_blended[-taper_len:] = np.minimum(
#     (taper_weights * y_spline[-taper_len:] + (1 - taper_weights) * clamp_value), 0
# )

# # Step 6: Create flat extension at -0.62 (clamp point) and maintain <= 0
# x_flat = x_all[flat_start_idx:]
# y_flat = np.full_like(x_flat, clamp_value)

# # Step 7: Combine full smoothed series
# y_smooth_full = np.concatenate([y_blended, y_flat])

# # Step 8: Wrap in DataArray
# clamped = xr.DataArray(
#     y_smooth_full,
#     coords={"time": x_dt},
#     dims=["time"],
#     name="ice_water_smooth"
# )

# # Interpolate to 6H time grid
# clamped_interp = clamped.interp(time=da_temp.time, method='linear')


# dH_dt_bot_clamped = clamped_interp.differentiate('time',datetime_unit="s") # m/s

# # latent heat from ice growth and decay at the bottom as in Semtner (1976)
# L_ice = 333000  # J/m3 
# rho_i = 910 #kg/m3 - sea ice density
# F_l_clamped = L_ice*rho_i*dH_dt_bot_clamped # where dH_dt is the BOTTOM ice growth rate; negative F_l means heat is being released from the ice to the ocean (ice growth)

# F_l_clamped.plot()
