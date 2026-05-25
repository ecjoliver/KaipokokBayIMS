import numpy as np
import matplotlib.pyplot as plt
import cmocean
import matplotlib as mpl
import xarray as xr
from matplotlib.cm import ScalarMappable
import gsw

plt.ion()

ds = xr.open_dataset('ADCP/adp.nc')
# Swap real time and distance dims
ds = ds.swap_dims({'TIME':'time','DISTANCE':'distance'})
ds = ds.sel(time=slice('2024-01-26','2024-4-15')) # cut time to match other IMS data

### Velocities ENU 
# Facetgrid - plot ENU velocities on subplots - just a quick look at the data
fg = ds.v.plot(x="time",
	y="distance",
	col="BEAM",
	col_wrap=1,
	vmin=-.2,
	vmax=0.2,
	cmap='RdBu_r', 
	figsize=(8,5))
fg.set_ylabels('Distance [m]')
fg.set_xlabels('Time')

titles = ['East','North','Up']
for ax, title in zip(fg.axes.flatten(), titles):
    ax.set_title(title)

# plt.savefig('figures/ADCP/ADCP_ENU.png',dpi=200)



### Speed
v_N = ds.v.sel(BEAM=1)
v_E = ds.v.sel(BEAM=2)
speed_adp = np.sqrt(v_N**2 + v_E**2)
plt.figure()
speed_adp.plot(vmin=0,vmax=0.5,cbar_kwargs={'label':'Speed (m/s)'}) # contourf
plt.title('ADCP speed')
# plt.savefig('ADCP_speed.png',dpi=200)


### Backscatter
fg = ds.a.plot(x="time",
	y="distance",
	col="BEAM",
	col_wrap=1,
	# vmin=-.2,
	# vmax=0.2,
	cmap='RdBu_r', 
	figsize=(8,5),
	cbar_kwargs={"label":"Bakcscatter [db]"})
fg.set_ylabels('Distance [m]')
fg.set_xlabels('Time')

titles = ['a1','a2','a3']
for ax, title in zip(fg.axes.flatten(), titles):
    ax.set_title(title)
# plt.savefig('figures/ADCP/ADCP_backscatter.png',dpi=200)


##### Subplots -NOT WORKING
fig,ax = plt.subplots(nrows=3,ncols=1,sharex=True)

dist = ds.DISTANCE

time = ds.time.values
vmin = -0.2
vmax = 0.2
im = ax[0].contourf(time,dist,ds.v.sel(BEAM=1),levels=np.linspace(-0.2,0.2,9),cmap='RdBu_r')
# divider = make_axes_locatable(ax[0])
# cax = divider.append_axes('right', size='5%', pad=0.05)
fig.colorbar(im, ax=ax[0], orientation='vertical')

# plt.clim(-0.2,0.2)