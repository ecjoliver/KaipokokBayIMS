'''
    Plot weekly ice and snow thicknesses
''' 

# Some globals
exec(open('../globals.py').read()) # modules, year, pathroot

# Load in NetCDF file of site visit data
ds = xr.open_dataset(pathroot + '/data/' + year + '/SiteVisits/SiteVisits_Weekly_IceSnowWater.nc')

# Make diagnostic plots
plt.figure(figsize=(15,5),facecolor='white')
plt.clf()
plt.plot(ds.time, ds.hi, 'k-o', zorder=7, label='Ice thickness')
plt.plot(ds.time, ds.hw, 'b-o', zorder=5, label='Water level')
plt.plot(ds.time, ds.hs, '--o', color='0.25', zorder=9, label='Snow (at hole)')
plt.plot(ds.time, ds.hs_snowStake_mean, '-o', color='0.25', zorder=13, label='Snow (from stakes, mean)')
plt.fill_between(ds.time, ds.hs_snowStake_mean - ds.hs_snowStake_sd, ds.hs_snowStake_mean + ds.hs_snowStake_sd, color='0.75', zorder=11, label='Snow (from stakes, std. dev.)')
plt.plot(ds.time, ds.hs_snowStake_1, '.', color='0.5', zorder=15, label='Snow (individual stakes)')
plt.plot(ds.time, ds.hs_snowStake_2, '.', color='0.5', zorder=15)
plt.plot(ds.time, ds.hs_snowStake_3, '.', color='0.5', zorder=15)
plt.plot(ds.time, ds.hs_snowStake_4, '.', color='0.5', zorder=15)
plt.plot(ds.time, ds.hs_snowStake_5, '.', color='0.5', zorder=15)
plt.plot(ds.time, ds.hs_snowStake_6, '.', color='0.5', zorder=15)
plt.plot(ds.time, ds.hs_snowStake_7, '.', color='0.5', zorder=15)
plt.plot(ds.time, ds.hs_snowStake_8, '.', color='0.5', zorder=15)
plt.plot(ds.time, ds.hs_snowStake_9, '.', color='0.5', zorder=15)
plt.legend()
plt.ylabel(r'$h$ (m)')

# plt.savefig('../../figures/' + year + '/SiteVisits/SiteVisits_Weekly_IceSnowWater.png', dpi=600, bbox_inches='tight')

