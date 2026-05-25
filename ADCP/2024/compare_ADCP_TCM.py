'''Compare the TCM and ADCP speeds and velocities. '''


import numpy as np
import matplotlib.pyplot as plt
import cmocean
import matplotlib as mpl
import xarray as xr
from matplotlib.cm import ScalarMappable
import gsw


### Load ADCP
ds_ADCP = xr.open_dataset('ADCP/adp.nc')
# Swap real time and distance dims
ds_ADCP = ds_ADCP.swap_dims({'TIME':'time','DISTANCE':'distance'})
ds_ADCP = ds_ADCP.sel(time=slice('2024-01-26','2024-4-15'))

### Load TCM from plot_TCM.py - use da_tcm

TCM_1_5 = da_tcm.sel(Depth=1.5)
TCM_2 = da_tcm.sel(Depth=2)

TCM_daily = da_tcm.resample(time='1D').mean('time')
TCM_1_5_daily = TCM_daily.sel(Depth=1.5)
TCM_2_daily = TCM_daily.sel(Depth=2)

###### Get top "1.5 m" from ADCP data - do this by seeing where the speed "jumps" - that is the ice bottom

# Where is the ADCP?
# gsw.z_from_p(ds.pressure,lat=55) # 12m

z = ds_ADCP.distance # depth in m , max in this array is 12.5 m

# z_15 = z[-1]-3 # 1.5m below ice surface, but need to shift down bevause it's still in the ice zone, hence the 4
# v_surf = ds.v.where((z>(z_15-0.5)) & (z<(z_15+0.5)))#.mean('distance')


# line plot of average speed over distance
plt.figure()
speed_adp_avgbin = speed_adp.mean('time')
speed_adp_avgbin.plot(marker='o')
plt.ylabel('Speed (m/s)')
# find where the speed increases (this is the ice bottom in theory)
loc = np.where(speed_adp_avgbin>0.15)[0][0]
plt.plot(speed_adp_avgbin.distance[loc],speed_adp_avgbin[loc],'ro')

v_surf = ds_ADCP.v.isel(distance=slice(loc-4,loc)).mean('distance') # use the first index where v is not too high (from above speed)
v_surf_N = v_surf.sel(BEAM=1) 
v_surf_E = v_surf.sel(BEAM=2)

speed_surf = np.sqrt(v_surf_N**2 + v_surf_E**2)*100 # convert to cm/s

# Plot the speeds

plt.figure(figsize=(8,8),facecolor='white')

ax = plt.subplot(211)
speed_surf.plot()
TCM_1_5['Speed (cm/s)'].plot()
TCM_2['Speed (cm/s)'].plot()
# plt.xlim(['2024-01-23','2024-04-15'])
plt.ylim([0,25])
ax.set_xticklabels([])
plt.xlabel("")
plt.legend(['ADCP 3-4 m avg','TCM-1 1.5 m','TCM-1 2 m'])
plt.title('Raw')

# Daily means
plt.subplot(212)
speed_surf_daily = speed_surf.resample(time='1D').mean('time')
speed_surf_daily.plot()
TCM_1_5_daily['Speed (cm/s)'].plot()
TCM_2_daily['Speed (cm/s)'].plot()
# plt.xlim(['2024-01-23','2024-04-15'])
plt.ylim([0,15])
plt.title('Daily mean')
plt.tight_layout()
# plt.savefig('figures/ADCP_TCM_speeds.png',dpi=300)