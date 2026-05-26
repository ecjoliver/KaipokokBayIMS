'''
    Compare CTD profiles with SIMBA data
'''

#
# Some globals
#

exec(open('../globals.py').read()) # modules, year, pathroot

fontsize=12

#
# Load in data
#

ctd = xr.open_dataset(pathroot + '/data/' + year + '/CTD_Profiles/CTD_IMS_SiteVisits.nc')
simba = xr.open_dataset(pathroot + '/data/' + year + '/SIMBA/SIMBA_temp.nc')

#
# Comparison plots
#

plt.figure(figsize=(15,13))
plt.clf()
for i in range(len(ctd.date)):
    ax = plt.subplot(4,4,i+1)
    ds = simba.sel(time=ctd.date[i], method='nearest')
    plt.plot(ctd.sel(date=ctd.date[i]).Temperature, -ctd.sel(date=ctd.date[i]).Depth, 'b-', label='CTD ' + str(ctd['date'][i].data)[:16])
    plt.plot(ds.temp, ds.z, 'r-', label='SIMBA ' + str(ds.time.data)[:16])
    plt.plot([-2., 0.], ctd.Hice[i].data*np.array([-1, -1]), ':')
    plt.xlim(-2, 0)
    plt.ylim(-3, 0)
    if np.mod(i+1,4) == 1:
        plt.ylabel('z (m)')
    else:
        ax.set_yticklabels([])
    if i+1 >= 13:
        plt.xlabel(r'Temperature, $T$ ($^\circ$C)')
    else:
        ax.set_xticklabels([])
    plt.legend(loc='lower left', fontsize=8)
    axs = ax.twiny()
    axs.plot(ctd.sel(date=ctd.date[i])['Absolute_Salinity'], -ctd.sel(date=ctd.date[i]).Depth, 'g-')
    if i+1 <= 4:
        axs.set_xlabel(r'Salinity, $S_\mathrm{A}$ (g/kg)', color='g')
        axs.set_xticklabels(axs.get_xticklabels(), color='g')
    else:
        axs.set_xticklabels([])

plt.tight_layout()

# plt.savefig('../../figures/' + year + '/CTD_Profiles/CTD_IMS_SiteVisits_CompareSIMBA.png', dpi=600, bbox_inches='tight')

