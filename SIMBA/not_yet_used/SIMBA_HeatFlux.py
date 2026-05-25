'''
Calculate and plot conductive heat flux from SIMBA data 
Requires loading data using load_SIMBA.py
Ice temperature is loaded from a pickle file, created in SIMBA_interface_detecton.py
'''
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pickle
import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl
mpl.interactive(True)
import cmocean
# import warnings; warnings.simplefilter('ignore')
import xarray as xr

with open('./SIMBA/temp_ice_z.pickle','rb') as f:
	temp_ice = pickle.load(f)

fontsize=12
z = temp_ice.z

# ---Conductive heat flux within the ice-----------------------

k_i = 2.09 # W/m/K, choose some constant for now (Pringle et al. 2006)  
# k_i = 3
dTdz = temp_ice.differentiate('z')
F_c_2d = k_i * (dTdz)

# Vertical average F_c
F_c_1d = F_c_2d.mean('z')

#---Plot a bunch of things------------------
# plt.rcParams.update({'font.size': fontsize})
fig,axx = plt.subplots(nrows=3,ncols=1,figsize=(20,28),sharex=True, facecolor='w')

labelfontsz=12
ylims=[-0.75, 0.50]
time_temp = temp_ice.time.values
# Temperature
im = axx[0].pcolormesh(time_temp, z, temp_ice.T, cmap=cmocean.cm.thermal, vmin=-2,vmax=0)
axx[0].set_ylabel('z [m]',color='black',fontdict={'fontsize':labelfontsz})
axx[0].set_title('Ice temperature')
axx[0].set_ylim(ylims)
# Add and adjust colorbar
divider = make_axes_locatable(axx[0])
cax = divider.append_axes('right', size="3%", pad=0.05,)
cbar = fig.colorbar(im, cax=cax)

# cbar = fig.colorbar(im,ax=axx[0],pad=0.02)
cbar.set_label(label='deg. C',
                                size=fontsize)
cbar.ax.tick_params(labelsize=fontsize)


# Conductive heat flux
im = axx[1].pcolormesh(time_temp, z, F_c_2d.T, vmin=-50, vmax=50, cmap='RdBu_r')
axx[1].set_ylabel('z [m]',fontdict={'fontsize':labelfontsz})
axx[1].set_title(r'Conductive heat with $k_i$=2.09')
axx[1].set_ylim(ylims)
# Adjust colorbar
divider = make_axes_locatable(axx[1])
cax = divider.append_axes('right', size="3%", pad=0.05,)
cbar = fig.colorbar(im, cax=cax)

cbar.set_label(label=r"W m$^{-2}$",
                                size=fontsize)
cbar.ax.tick_params(labelsize=fontsize)

# Vertical average F_c
axx[2].plot(time_temp, F_c_1d,'k-',linewidth=2, label=k_i,zorder=100)
axx[2].grid()
axx[2].set_title('Vertically averaged conductive heat')
axx[2].set_ylabel(r"W m$^{-2}$",fontdict={'fontsize':labelfontsz})
divider = make_axes_locatable(axx[2])
cax = divider.append_axes('right', size="3%", pad=0.05,)
cax.remove()

# Add other options for k_i
k_is = np.linspace(1.5,3,7)
for k_i_ in k_is:
	F_c = k_i_ * (dTdz)
	# Vertical average F_c
	F_c_1d = F_c.mean('z')
	axx[2].plot(time_temp,F_c_1d,label=k_i_)

axx[2].legend(loc='lower right',ncol=2, title=r'$k_i$')

# plt.savefig('figures/HeatBudget/SIMBA_Fc.png',dpi=300)
