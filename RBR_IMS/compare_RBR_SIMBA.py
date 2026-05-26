'''
   Compare RBR and SIMBA temperatures
'''

#
# Some globals
#

exec(open('../globals.py').read()) # modules, year, pathroot

#
# Load in data
#

ds_T = xr.open_dataset(pathroot + '/data/' + year + '/RBR_IMS/RBR_temperature.nc')
ds_SIMBA = xr.open_dataset(pathroot + '/data/' + year + '/SIMBA/SIMBA_temp.nc')

#
# Time series comparisons
#

plt.figure(figsize=(11,9), facecolor='w')
# z = -1.0 m
zi = 1.0
plt.subplot(3,1,1)
plt.plot(ds_T.time, ds_T.T.sel(z=zi), 'k-', alpha=0.5)
plt.plot(ds_SIMBA.time, ds_SIMBA.temp.sel(z=-zi), 'k-', alpha=0.5)
plt.plot(ds_T.time, IMS.DoodsonX0(ds_T.T.sel(z=zi)), 'b-', label='RBR (z=-' + str(zi) + ' m)')
plt.plot(ds_SIMBA.time, IMS.DoodsonX0(ds_SIMBA.temp.sel(z=-zi)), 'r-', label='SIMBA (z=-' + str(zi) + ' m)')
plt.ylabel(r'Temperature, $T$ ($^\circ$C)')
plt.legend(loc='upper left')
plt.xlim([ds_T.time[0], ds_T.time[-1]])
# z = -1.5 m
zi = 1.5
plt.subplot(3,1,2)
plt.plot(ds_T.time, ds_T.T.sel(z=zi), 'k-', alpha=0.5)
plt.plot(ds_SIMBA.time, ds_SIMBA.temp.sel(z=-zi), 'k-', alpha=0.5)
plt.plot(ds_T.time, IMS.DoodsonX0(ds_T.T.sel(z=zi)), 'b-', label='RBR (z=-' + str(zi) + ' m)')
plt.plot(ds_SIMBA.time, IMS.DoodsonX0(ds_SIMBA.temp.sel(z=-zi)), 'r-', label='SIMBA (z=-' + str(zi) + ' m)')
plt.ylabel(r'Temperature, $T$ ($^\circ$C)')
plt.legend(loc='upper left')
plt.xlim([ds_T.time[0], ds_T.time[-1]])
# z = -2.4
zi = 2.4
plt.subplot(3,1,3)
plt.plot(ds_T.time, ds_T.T.sel(z=zi), 'k-', alpha=0.5)
plt.plot(ds_SIMBA.time, ds_SIMBA.temp.sel(z=-zi), 'k-', alpha=0.5)
plt.plot(ds_T.time, IMS.DoodsonX0(ds_T.T.sel(z=zi)), 'b-', label='RBR (z=-' + str(zi) + ' m)')
plt.plot(ds_SIMBA.time, IMS.DoodsonX0(ds_SIMBA.temp.sel(z=-zi)), 'r-', label='SIMBA (z=-' + str(zi) + ' m)')
plt.ylabel(r'Temperature, $T$ ($^\circ$C)')
plt.legend(loc='upper left')
plt.xlim([ds_T.time[0], ds_T.time[-1]])
#
plt.tight_layout()

# plt.savefig('../../figures/' + year + '/RBR_IMS/RBR_Timeseries_CompareSIMBA.png', dpi=600, bbox_inches='tight')
