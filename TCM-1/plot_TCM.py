'''
    Load in TCM data
'''

# Some globals

exec(open('../globals.py').read()) # modules, year, pathroot

#
# Load in TCM data
#

da_tcm_hourly = xr.open_dataset(pathroot + '/data/' + year + '/TCM-1/TCM_currents_hourly.nc')
da_tcm_detided = xr.open_dataset(pathroot + '/data/' + year + '/TCM-1/TCM_currents_detided.nc')
da_tcm_daily = xr.open_dataset(pathroot + '/data/' + year + '/TCM-1/TCM_currents_daily.nc')

z = list(da_tcm_hourly['Speed'].z.data)

#
# Plots
#

# Full time series (hourly and detided)
c = {'1.0': 'red', '1.5': 'black', '2.0': 'blue'}
lw = 3 # linewidth
fig,axx = plt.subplots(nrows=4,ncols=1,figsize=(8,9),sharex=True, facecolor='w')
for zi in z:
    axx[0].plot(da_tcm_hourly['time'], da_tcm_hourly['Speed'].sel(z=zi), c=c[str(zi)], alpha=0.5)
    axx[0].plot(da_tcm_detided['time'], da_tcm_detided['Speed'].sel(z=zi), c=c[str(zi)], linewidth=lw, zorder=5, label=str(zi)+' m')
    axx[0].set_ylabel('m/s')
    axx[0].set_title('Speed')
    
    axx[1].plot(da_tcm_hourly['time'], da_tcm_hourly['Velocity-N'].sel(z=zi), c=c[str(zi)], alpha=0.5)
    axx[1].plot(da_tcm_detided['time'], da_tcm_detided['Velocity-N'].sel(z=zi), c=c[str(zi)], linewidth=lw, zorder=5, label=str(zi)+' m')
    axx[1].set_ylabel('m/s')
    axx[1].set_title('Velocity-N')
    
    axx[2].plot(da_tcm_hourly['time'], da_tcm_hourly['Velocity-E'].sel(z=zi), c=c[str(zi)], alpha=0.5)
    axx[2].plot(da_tcm_detided['time'], da_tcm_detided['Velocity-E'].sel(z=zi), c=c[str(zi)], linewidth=lw, zorder=5, label=str(zi)+' m')
    axx[2].set_ylabel('m/s')
    axx[2].set_title('Velocity-E')
    
    axx[3].plot(da_tcm_hourly['time'], da_tcm_hourly['Heading'].sel(z=zi), c=c[str(zi)], alpha=0.5)
    axx[3].plot(da_tcm_detided['time'], da_tcm_detided['Heading'].sel(z=zi), c=c[str(zi)], linewidth=lw, zorder=5, label=str(zi)+' m')
    axx[3].set_ylabel('degrees')
    axx[3].set_title('Heading')

axx[3].legend(loc='upper left')

plt.xlim(da_tcm_hourly.time[0], da_tcm_hourly.time[-1])
plt.tight_layout()

# plt.savefig('../../figures/' + year + '/TCM-1/TCM_Overview_Hourly.png', dpi=600, bbox_inches='tight')

# Full time series (daily)
c = {'1.0': 'red', '1.5': 'black', '2.0': 'blue'}
lw = 2 # linewidth
fig,axx = plt.subplots(nrows=4,ncols=1,figsize=(8,9),sharex=True, facecolor='w')
for zi in z:
    axx[0].plot(da_tcm_daily['time'], da_tcm_daily['Speed'].sel(z=zi), c=c[str(zi)], linewidth=lw, zorder=5, label=str(zi)+' m')
    axx[0].set_ylabel('m/s')
    axx[0].set_title('Speed')
    
    axx[1].plot(da_tcm_daily['time'], da_tcm_daily['Velocity-N'].sel(z=zi), c=c[str(zi)], linewidth=lw, zorder=5, label=str(zi)+' m')
    axx[1].set_ylabel('m/s')
    axx[1].set_title('Velocity-N')
    
    axx[2].plot(da_tcm_daily['time'], da_tcm_daily['Velocity-E'].sel(z=zi), c=c[str(zi)], linewidth=lw, zorder=5, label=str(zi)+' m')
    axx[2].set_ylabel('m/s')
    axx[2].set_title('Velocity-E')
    
    axx[3].plot(da_tcm_daily['time'], da_tcm_daily['Heading'].sel(z=zi), c=c[str(zi)], linewidth=lw, zorder=5, label=str(zi)+' m')
    axx[3].set_ylabel('degrees')
    axx[3].set_title('Heading')

axx[3].legend(loc='upper left')

plt.xlim(da_tcm_daily.time[0], da_tcm_daily.time[-1])
plt.tight_layout()

# plt.savefig('../../figures/' + year + '/TCM-1/TCM_Overview_Daily.png', dpi=600, bbox_inches='tight')

# Wind roses
N = len(z)*2 # Number of subplots (2x TCMs x (tidal, non-tidal)
# Determine axes locations for windrose plots
rect = {}
plt.figure()
for i in range(N):
    ax = plt.subplot(2,len(z),i+1)
    rect[i] = ax.get_position()
plt.close()
# Create windrose plots
fig = plt.figure()
i = 0
# With tides
for zi in z:
    wa = WindroseAxes(fig, rect[i])
    ax = fig.add_axes(wa)
    wa.bar(da_tcm_hourly['Heading'].sel(z=zi).data, 100*da_tcm_hourly['Speed'].sel(z=zi).data, bins=np.arange(0,8,2), normed=True, opening=0.8, edgecolor='white')
    ax.set_legend(title='Current speed (cm/s)')
    wa.set_title('z = ' + str(zi) + ' m (with tides)')
    i += 1
# Without tides
for zi in z:
    wa = WindroseAxes(fig, rect[i])
    ax = fig.add_axes(wa)
    wa.bar(da_tcm_detided['Heading'].sel(z=zi), 100*da_tcm_detided['Speed'].sel(z=zi), bins=np.arange(0,8,2), normed=True, opening=0.8, edgecolor='white')
    ax.set_legend(title='Current speed (cm/s)')
    wa.set_title('z = ' + str(zi) + ' m (detided)')
    i += 1

# plt.savefig('../../figures/' + year + '/TCM-1/TCM_WindRose.png', dpi=600, bbox_inches='tight')

