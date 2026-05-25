'''
Plot the results from heatbudget.py
'''



#################### SURFACE FLUXES ###############################

#---------------- Plot the surface heat balance  ----------------

t = T_a.time

plt.rcParams.update({'font.size': fontsize})


fig,axx = plt.subplots(nrows=2,ncols=1,figsize=(10,8),sharex=True, facecolor='w')
fig.suptitle('Surface heat balance with varying k_i',fontsize=16,y=0.92)

axx[0].axhline(0,c='dimgrey',alpha=0.8)
axx[0].plot(t,F_sw_net_tot,color='peru',linestyle='-',label=r'F$_{netSWR}$')
axx[0].plot(t,F_lw_net_clean,c='firebrick',label=r'F$_{netLWR}$')
axx[0].plot(t,F_sens,c='forestgreen',label=r'F$_{sens}$')
axx[0].plot(t,F_c_surf_1d,label=r'F$_{c,surf}$',c='deepskyblue',linestyle='-')
axx[0].plot(t,F_lat,label=r'F$_{lat}$',c='pink',linestyle='-')
axx[0].plot(t,F_net,label=r'F$_{net,surf}$',c='black',linestyle='--')


axx[0].set_ylim([-150,150])
axx[0].set_ylabel(r'W/m$^2$')
l1 = axx[0].legend(bbox_to_anchor=(1.001,1.001))
# axx[0].grid()


# plot net fluxes with and without latent heat
axx[1].axhline(0,c='dimgrey',alpha=0.8)
axx[1].plot(t,F_surf,label=r'F$_{surf}$',c='black',linestyle='-')
axx[1].plot(t,F_c_surf_1d,label=r'F$_{c,surf}$',c='deepskyblue',linestyle='-')

axx[1].set_ylabel(r'W/m$^2$')
axx[1].set_ylim([-150,150])
l2 = axx[1].legend(bbox_to_anchor=(1,1.001))
# axx[1].grid()

# axx[2].plot(t,F_diffs + F_c, label=r'Residual',color='grey')
axx[2].axhline(0,c='dimgrey',alpha=0.8)
axx[2].plot(t,F_turb, label=r'F$_{turb}$',color='b',linestyle='-') # 
axx[2].plot(t,F_rad, label=r'F$_{rad}$',color='orange',linestyle='-') # 
axx[2].plot(t,F_net, label=r'F$_{net,surf}$',color='k',linestyle='--') # residual
axx[2].set_ylabel(r'W/m$^2$')
axx[2].set_ylim([-150,150])
l3 = axx[2].legend(bbox_to_anchor=(1,1.001))
# axx[2].grid()

axx[2].set_xlim(['2024-01-26','2024-04-15'])

# Customize x-ticks: Show all daily ticks but label only every 15 days
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))  # Ticks every day
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format as YYYY-MM-DD

# Label only every 10th day by modifying the tick labels

labels = [pd.Timestamp(date).strftime('%Y-%m-%d') if i % 10 == 0 else '' for i, date in enumerate(t.values)]
plt.xticks(t.values, labels, rotation=15)
print()

#
# plt.savefig('figures/HeatBudget/surf_balance_daily_ki.png',dpi=300, bbox_inches='tight')
#


#---------------- Compare surface temperatures ----------------
# Compare T_s derived from observations and calculated from "perfect" heat balance

plt.figure(figsize=(10,5))
plt.plot(T_s.time,T_s,label='Surface balance')
plt.plot(T_s_obs.time, T_s_obs, label='SIMBA (obs)')
T_a.plot(label='Air temp')
plt.title('Surface temperature calculation')
plt.legend()

# plt.savefig('figures/HeatBudget/Ts.png',dpi=300,bbox_inches='tight')





##---------------- Compare conductive heat fluxes ----------------

plt.figure(figsize=(8,5),facecolor='white')
# (-F_diffs).plot(color='grey',alpha=0.8,label=r'$F_c = F_{sens} + F_{netSWR} + F_{netLWR}$')# Residual from surface balance
F_c_approx.plot(color='green',alpha=0.8, label=r'$F_c = (T_s-T_w)/(H_i/k_i + H_s/k_s)$') # F_c = (Ts - Tw)/(Hi/ki + Hs/ks)
F_c_approx_obs.plot(color='cyan',alpha=0.8, label=r'$F_c = (T_s(obs)-T_w)/(H_i/k_i + H_s/k_s)$') # F_c = (Ts - Tw)/(Hi/ki + Hs/ks)
(F_c).plot(color='black', label=r'$F_c (ref) = k_i dT/dz$') # Reference layer
F_c_1d = F_c_2d.mean('z') # dTdz averaged over entire ice slab
F_c_1d.plot(color='red', label=r'$F_c = k_i dT/dz$')
plt.legend()
plt.ylabel(r'W/m$^2$')
plt.xticks(rotation=15)
# plt.ylim([-20,40])
plt.xlim(['2024-01-26','2024-04-15'])
plt.title('Comparison of conductive heat flux derivations w/ varying k_i')
# plt.savefig('figures/HeatBudget/Fc_compare_ki.png',dpi=300)



#################### BOTTOM HEAT FLUXES #####################


###-------------- Plot Fw into bins with line on top ----------------

# Lei and Perovich methods yield nearly identical results. NEed to play around with parameters C_s and q_m still. 
# Uncertainty in F_w decreases with increasing averaging period

F_w_lei_sub = F_w_lei.sel(time=slice('2024-02-02',None))

F_w_bins = F_w_lei_sub.resample(time='30D').mean('time')
F_w_wk = F_w_lei_sub.resample(time='7D').mean('time')
F_w_day = F_w_lei_sub.resample(time='1D').mean('time')

t_plot = F_w_wk.time

fig, ax = plt.subplots(figsize=(10,6))
ax.plot(t_plot,F_w_wk,'r-',zorder=10, label='7-day average')
plt.xlim([t1,t2])
plt.xticks(rotation=15)

p1 = ax.twiny()
# p1.bar(F_w_bins.time.values, F_w_bins,width=1,
# 	zorder=1,color='grey',alpha=0.5, align='edge',edgecolor='black',label='30-day average')
F_w_bins.to_series().plot.bar(color='grey',alpha=0.8,width=1,align='edge',edgecolor='black',label='30-day average')
p1.set_xticks([])
p1.set_xlim([0,F_w_bins.size])
p1.set_xlabel('')
p2 = ax.twiny()
p2.plot(F_w_day.time.values, F_w_day,'k--',label='1-day average')
p2.set_xticks([])
plt.xlim([t1,t2])
plt.title('Ocean Heat Flux (Fw): basal balance residual method \n H from 2x 5-day moving average \n S_i = 5')
ax.set_ylabel(r'W/m$^2$')
# plt.ylim([-5,20])
fig.legend(bbox_to_anchor=(0.4, 0.35, 0.5, 0.5))
# plt.savefig('figures/HeatBudget/Fw_perov_5Si.png',dpi=300,bbox_inches='tight')


###-------------- Plot basal balance ----------------

# Since the hole takes about 12 weeks to get to 0.32 m thick (the initial thickness), cut off the first 12 days otherwise dH_dt is too big to match Fc.
# Other option is to calculate another Fc for the hole during that time period
F_l_ = F_l.sel(time=slice('2024-02-02',None))
fig, ax = plt.subplots(figsize=(10,6))
# F_w_lei.plot(label=r'$F_w$')
Fw_quad_daily.plot(label=r'F$_w$')
(F_c).plot(label=r'$F_c$')
# F_s.plot(label=r'$F_s$')
F_l_.plot(label=r'$F_l$')
# Total (should be 0!)
# (F_l + F_s + F_c_ref - F_w_lei).plot(color='k')
plt.axhline(0,color='grey',linestyle='--')
plt.legend()
plt.xlim([t1,t2])
plt.ylim([-50,60])
plt.ylabel(r'W/m$^2$')
plt.title('Basal heat flux balance')
# plt.savefig('figures/HeatBudget/basal_balance_5day.png',dpi=400,bbox_inches='tight')



fig, ax = plt.subplots(figsize=(10,6))
plt.axhline(0,color='grey',linestyle='--')

F_w_avg.plot(label=r'$F_w$',c='red')
F_c_avg.plot(label=r'$F_c$',c='deepskyblue')
# F_s_avg.plot(label=r'$F_s$',c='green')
F_l_avg.plot(label=r'$F_l$',c='pink')
F_bot.plot(label=r'$F_{net}$',c='k')
# Total (should be 0!)
# (F_l + F_s + F_c_ref - F_w_lei).plot(color='k')
plt.legend()
plt.xlim(['2024-01-26','2024-04-15'])
plt.ylim([-80,50])
plt.ylabel(r'W/m$^2$')
plt.title('Daily basal heat fluxes')
plt.xticks(rotation=15)

#
# plt.savefig('figures/HeatBudget/basal_balance_FwQuad.png',dpi=400,bbox_inches='tight')
#


#################### COMBINED SURFACE AND BOTTOM FLUXES ###############################

# Plot net flux from surface and bottom with correlations to ice and snow temps

t_plot = T_i_1d.time
fig,axx = plt.subplots(nrows=3,ncols=1,figsize=(10,8))
axx[0].plot(F_diff.time,F_diff_net,'k-',label=r'$F_{diff} = F_{surf} - F_{bot}$')
axx[0].plot(t_plot,T_s_1d,c='r',label='Snow temperature')
axx[0].axhline(0,c='grey')
# axx[0].set_ylim(-25,30)
axx[0].set_ylabel(r'Flux [W/m$^2$]/Snow T [$^\circ$C]')

ax_ = axx[0].twinx()
ax_.plot(t_plot,T_i_1d,c='c',label='Ice temperature')
ax_.set_ylabel(r'Ice T [$^\circ$C]')

plt.xticks(rotation=15)
plt.xlim(t1,t2)
ax_.set_ylim(-5,0)

fig.legend(loc='upper left',fontsize=10,bbox_to_anchor=[0.09,0.99])

axx[1].plot(lags_s,corr_s)
axx[1].set_xlabel('Lag (days)')
axx[1].set_ylabel('Correlation')
axx[1].set_title(r'Cross correlation: Snow temp and F$_{diff}$')
axx[2].plot(lags_i,corr_i)
axx[2].set_xlabel('Lag (days)')
axx[2].set_ylabel('Correlation')
axx[2].set_title(r'Cross correlation: Ice temp and F$_{diff}$')

#
# plt.savefig('figures/HeatBudget/Fdiff_Ts_Ti_corrs.png',dpi=400,bbox_inches='tight')
#


#---------- Plot net fluxes from surface and bottom with F_diff --------------

plt.figure(figsize=(8,5))
Fnet_bot.plot(c='crimson',label=r'Net basal flux ($F_{bot})$')
F_net.rolling(time=3,center='True').mean().plot(label=r'Net surface flux ($F_{surf}$)',c='steelblue')
# F_net.plot(label=r'Net surface flux ($F_{surf}$)',c='blue')
F_diff_net.plot(label=r'$F_{surf} - F_{bot}$',c='k',linewidth=2)
plt.legend()
plt.xticks(rotation=15)
plt.xlim(t1,t2)
plt.title('Net surface and basal fluxes')
plt.ylabel(r'W/m$^2$')

#
# plt.savefig('figures/HeatBudget/NetFluxes_surf+bot.png',dpi=400,bbox_inches='tight')
#

###### Plot net fluxes from surface and bottom with snow temperature


fig,ax = plt.subplots(figsize=(8,5))
ax.plot(F_diff_net.time,F_diff_net,label=r'$F_{surf} - F_{bot}$',c='k',linewidth=2)
 ax.axhline(0,c='grey')
ax_ = ax.twinx()
ax_.plot(T_s_1d.time,T_s_1d,c='r',label='Snow temperature')
plt.xticks(rotation=15)
plt.xlim(t1,t2)
# plt.title('Net surface and basal fluxes')
ax.set_ylabel(r'W/m$^2$')
ax_.set_ylabel(r'$^\circ C$')
fig.legend(bbox_to_anchor=[0.9,0.89])
#
# plt.savefig('figures/HeatBudget/Fdiff_Ts.png',dpi=400,bbox_inches='tight')
#

##----------------- One figure to tell the net heat flux story ---------------

fig,axx = plt.subplots(nrows=2,ncols=1,figsize=(10,8),sharex=True, facecolor='w')
fig.suptitle('Net surface heat flux',fontsize=16,y=0.92)


# Correlation with turbulent and radiative heat fluxes
axx[0].axhline(0,c='dimgrey',alpha=0.8)
axx[0].plot(t,F_turb, label=r'F$_{\mathrm{turb}}$',color='b',linestyle='-') # 
axx[0].plot(t,F_rad, label=r'F$_{\mathrm{rad}}$',color='orange',linestyle='-') # 
axx[0].plot(t,F_surf, label=r'F$_{\mathrm{net,surf}}$',color='k',linestyle='-') # residual
axx[0].set_ylabel(r'W/m$^2$')
axx[0].set_ylim([-100,100])
l3 = axx[0].legend(bbox_to_anchor=(1,1.001))
# axx[2].grid()

# Ice and snow temperature
axx[1].axhline(0,c='dimgrey',alpha=0.8)
axx[1].plot(t,temp_ice.resample(time='1D').mean('time').mean('z'), label=r'T$_{i}$',color='crimson',linestyle='-') # 
axx[1].plot(t,temp_snow.mean('z'), label=r'T$_{s}$',color='mediumpurple',linestyle='-') # 
axx[1].set_ylabel(r'W/m$^2$')
l3 = axx[1].legend(bbox_to_anchor=(1,1.001))
# axx[2].grid()


axx[1].set_xlim(['2024-01-26','2024-04-15'])


##----------------- Colored ice evolution with annotated quotes ---------------

# Add model run
begT = np.datetime64('2024-01-26')
endT = np.datetime64('2024-04-15')
with open('HeatBudget/H_percents.pickle','rb') as f:
    Hp = pickle.load(f)

H_mod = convert2da(Hp[-1],begT,endT)['H_i']
H_si_obs = -(H_ice - H_bottom)


fig,ax = plt.subplots(nrows=1,sharex=True,figsize=(10,5), facecolor='w')
# fig.suptitle('Surface heat balance',fontsize=16,y=0.92)
# t1 = H_bottom.time.values.to_datetime()
t1 = pd.to_datetime(H_bottom.time)
ax.plot(t1,H_bottom,color='mediumblue')
hIce = ax.fill_between(t1,H_bottom.values,0,color='mediumblue',alpha=0.2)
ax.set_xlim(['2024-01-26','2024-04-15'])

# axx[0].errorbar(x=mbs_snow.index,y=mbs_snow.Mean,yerr=mbs_snow.Std,color='gray',capsize=capsz,fmt='o')
# axx[0].plot(mbs_snow.Min,color='gray',linestyle='--')
# axx[0].plot(mbs_snow.Max,color='gray',linestyle='--')
ax.plot(snow_air.time,snow_air,color='gray')
hSnow = ax.fill_between(snow_air.time.values,snow_ice.resample(time='1D').mean('time'),snow_air,color='gray',alpha=0.2)

ax.plot(t1,snow_ice_smoothed,color='cornflowerblue')
hFlood = ax.fill_between(t1,0,snow_ice_smoothed,color='cornflowerblue',alpha=0.2)
# hSlush = axx[0].fill_between(mbs_flood.index[5:],np.zeros(len(mbs_flood.index[5:])),np.zeros(len(mbs_flood.index[5:]))+[0,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015],color='midnightblue',alpha=0.5)
l1 = ax.legend([hSnow,hFlood,hIce],['Dry Snow','Snow-Ice','Sea Ice'],bbox_to_anchor=(1.001,1.001))

# Model
ax.plot(H_mod.time,-H_mod,c='k',linestyle='--')
ax.plot(H_mod.time,h_si_,c='r',linestyle='--')



# Add vertical lines with annotations
events = [
	{"date": "2024-02-27"},
    {"date": "2024-02-20"},
    {"date": "2024-03-05", "label": "39 cm hard packed snow. \n Drilled ~4 inches [to] a layer \n of water ~1 inch and then ice again"},
    {"date": "2024-03-19", "label": "Slobby on top of the ice - about 5 cm of slob before we drilled the hole."},
    {"date": "2024-04-02", "label": "22.5 cm of slob on top of the ice. Very little snow now."},
    {"date": "2024-04-09"}
]

for event in events:
    date = pd.to_datetime(event["date"])
    ax.axvline(date, color='grey', linestyle='-', alpha=0.5)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))


#
# plt.savefig('../../../HeatBudget_manuscript/Figures_skeleton/labeled_evolution_blank.png',dpi=300, bbox_inches='tight')
#









