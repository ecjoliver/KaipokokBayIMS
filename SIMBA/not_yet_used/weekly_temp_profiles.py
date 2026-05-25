import xarray as xr
import matplotlib.pyplot as plt
import pickle
with open('./SIMBA/temp_ice.pickle','rb') as f:
	temp_ice = pickle.load(f)


temp_ice_wk = temp_ice.resample(time='W').mean('time')
temp_ice_day = temp_ice.resample(time='1D').mean('time')


da_temp = temp_ice_day

# create colormap for time
cm = plt.cm.bwr(np.linspace(0, 1, len(da_temp)))

plt.figure(figsize=(8,10),facecolor='white')
ax = plt.subplot(111)
ax.set_prop_cycle('color', list(cm)) # color each line in sequential order
ax.plot(da_temp.T, z) 

plt.ylabel('z [cm]',fontsize=fontsize)
plt.xlabel('T [deg. C]', fontsize=fontsize)
plt.ylim(-100, 50)
plt.grid()
ax.tick_params(axis='both',labelsize=fontsize)

## COLORBAR
# create a ListedColormap and BoundaryNorm
cmap = ListedColormap(cm)
bounds = np.linspace(0, 1, len(da_temp) + 1)
norm = BoundaryNorm(bounds, cmap.N)

# Add a discrete colorbar for the entire figure
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, boundaries=bounds, ticks=0.5*(bounds[1:] + bounds[:-1]))
cbar.set_label('Time', fontsize=fontsize)

# Change the tick labels on the colorbar - month day
# new_tick_labels = [pd.to_datetime(str(t)).strftime('%m-%d %H:%M') for t in da_temp['time'].values]
new_tick_labels = [pd.to_datetime(str(t)).strftime('%m-%d') for t in da_temp['time'].values]

cbar.set_ticklabels(new_tick_labels)
n = 24  # Keep every nth label
[l.set_visible(False) for (i,l) in enumerate(cbar.ax.yaxis.get_ticklabels()) if i % n != 0]
cbar.ax.tick_params(labelsize=fontsize-4)
# plt.savefig('/home/mwang/thesis/IMS2024/SIMBA/Jan24-31_temp_profiles.png')

