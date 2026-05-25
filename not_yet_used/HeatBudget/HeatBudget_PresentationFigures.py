'''
Presentation figures 
'''

# -------------Snow and ice evolution ---------------------------------


fig,axx = plt.subplots(nrows=1,ncols=1,figsize=(10,5),sharex=True, facecolor='w')
# fig.suptitle('Surface heat balance',fontsize=16,y=0.92)
# t1 = H_bottom.time.values.to_datetime()
t1 = pd.to_datetime(H_bottom.time)
axx.plot(t1,H_bottom,color='mediumblue')
hIce = axx.fill_between(t1,H_bottom.values,0,color='mediumblue',alpha=0.2)
axx.set_xlim(['2024-01-26','2024-04-15'])

# axx[0].errorbar(x=mbs_snow.index,y=mbs_snow.Mean,yerr=mbs_snow.Std,color='gray',capsize=capsz,fmt='o')
# axx[0].plot(mbs_snow.Min,color='gray',linestyle='--')
# axx[0].plot(mbs_snow.Max,color='gray',linestyle='--')
axx.plot(snow_air.time,snow_air,color='gray')
hSnow = axx.fill_between(snow_air.time.values,snow_ice.resample(time='1D').mean('time'),snow_air,color='gray',alpha=0.2)

axx.plot(t1,snow_ice_smoothed,color='cornflowerblue')
hFlood = axx.fill_between(t1,0,snow_ice_smoothed,color='cornflowerblue',alpha=0.2)
# hSlush = axx[0].fill_between(mbs_flood.index[5:],np.zeros(len(mbs_flood.index[5:])),np.zeros(len(mbs_flood.index[5:]))+[0,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015],color='midnightblue',alpha=0.5)
l1 = axx.legend([hSnow,hFlood,hIce],['Dry Snow','Snow-Ice','Sea Ice'],bbox_to_anchor=(1.001,1.001),fontsize=fontsize+4)
axx.set_xlim([t1[0],t1[-1]])
axx.set_ylabel('z [m]',fontsize=fontsize+4)
axx.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
axx.tick_params(axis='both',labelsize=fontsize+4)

#
# plt.savefig('figures/HeatBudget/SnowIce_presentation.png',dpi=600, bbox_inches='tight')
#

# ------------- Total net surface heat flux components ---------------------------------

fig,axx = plt.subplots(nrows=1,ncols=1,figsize=(10,5),sharex=True,facecolor='w',layout='constrained')

# COMPLETE SURFACE HEAT BALANCE AS STACKED PLOT
F_c_surf_pos = F_c_surf.where(F_c_surf > 0, 0)
F_c_surf_neg = F_c_surf.where(F_c_surf < 0, 0)
F_sens_pos = F_sens.where(F_sens > 0, 0)
F_sens_neg = F_sens.where(F_sens < 0, 0)
F_lat_pos = F_lat.where(F_lat > 0, 0)
F_lat_neg = F_lat.where(F_lat < 0, 0)

# axx.text(0.01,0.96,'(a) Surface heat balance',fontsize=fontsize,transform=axx[an].transAxes,
        # verticalalignment='top')
bar_width = np.timedelta64(22, 'h')
axx.bar(t, F_lw_net_clean, width=bar_width, color='firebrick',label=r'$F_{\mathrm{netLWR}}$')
axx.bar(t, F_sw_net, width=bar_width, color='peru',label=r'$F_\mathrm{netSWR}$')
axx.bar(t, F_c_surf_neg, width=bar_width, bottom=F_lw_net_clean.where(F_c_surf<0,0), color='steelblue',label=r'$F_\mathrm{c,s}$')
axx.bar(t, F_c_surf_pos, width=bar_width, bottom=F_sw_net.where(F_c_surf>0,0), color='steelblue')
axx.bar(t, F_sens_neg, width=bar_width, bottom=F_c_surf_neg+F_lw_net_clean.where(F_sens<0,0), color='forestgreen',label=r'$F_\mathrm{SH}$')
axx.bar(t, F_sens_pos, width=bar_width, bottom=F_c_surf_pos+F_sw_net.where(F_sens>0,0), color='forestgreen')
axx.bar(t, F_lat_neg, width=bar_width, bottom=F_c_surf_neg+F_lw_net_clean.where(F_lat<0,0)+F_sens_neg, color='violet',label=r'$F_\mathrm{LH}$')
axx.bar(t, F_lat_pos, width=bar_width, bottom=F_c_surf_pos+F_sw_net.where(F_lat>0,0)+F_sens_pos, color='violet')
axx.bar(t, F_snowmelt, width=bar_width, bottom=F_c_surf_neg+F_lw_net.where(F_snowmelt<0,0)+F_sens_neg+F_lat_neg, color='lawngreen',label=r'$F_{\mathrm{snowmelt}}$')
axx.bar(t, F_icemelt, width=bar_width, bottom=F_c_surf_neg+F_lw_net.where(F_icemelt<0,0)+F_sens_neg+F_lat_neg+F_snowmelt, color='gold',label=r'$F_{\mathrm{icemelt}}$')

axx.plot(t,F_net_surf,'k-',label=r'$F_{\mathrm{net,s}}$')
axx.set_ylabel(r'W m$^{-2}$',fontsize=fontsize+4)
l2 = axx.legend(bbox_to_anchor=(1,1.001),fontsize=fontsize+4)
axx.grid()
axx.tick_params(axis='y',labelsize=fontsize+4)
axx.set_xlim(['2024-01-25','2024-04-16'])
axx.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
axx.tick_params(axis='both',labelsize=fontsize+4)

# plt.savefig('figures/HeatBudget/SurfaceFluxes_presentation.png',dpi=600, bbox_inches='tight')
