'''
   Load in RBR insrument data and save as NetCDF files
'''

#
# Some globals
#

# year = '2024'
# Start on Jan. 26, end April 15 - consistent with other datasets
# ds = ds.sel(time=slice("2024-01-26","2024-04-15")) 
#t1,t2 = '2024-01-26','2024-04-15'

exec(open('../globals.py').read()) # modules, year, pathroot

#
# Load in data
#

# define filenames
rsk = {}
time_start = {}
time_end = {}
# 2025
rsk['CTD_bottom'] = pathroot + '/data/' + year + '/RBR_IMS/CTD_Bottom/206046_20250413_0004.rsk' # Bottom CTD
rsk['CTD_sfc'] = pathroot + '/data/' + year + '/RBR_IMS/CTD_nearSurface/206045_20250413_0017.rsk' # Near-surface CTD
rsk['TD_2'] = pathroot + '/data/' + year + '/RBR_IMS/TD/204292_20250413_0047.rsk' # 2.4 m TD
rsk['TD_4'] = pathroot + '/data/' + year + '/RBR_IMS/TD/204337_20250413_0034.rsk' # 4.25 m TD
rsk['TD_38'] = pathroot + '/data/' + year + '/RBR_IMS/TD/204291_20250413_0041.rsk' # 38 m TD
rsk['Tstring'] = pathroot + '/data/' + year + '/RBR_IMS/Tstring/204294_20250413_0026.rsk' # Tstring
for ins in rsk.keys():
    time_start[ins] = '2025-02-10T20:05:00' # Deployment YYYY-MM-DDTHH:MM:SS (UTC)
    time_end[ins]   = '2025-04-12T09:30:00' # Recovery YYYY-MM-DDTHH:MM:SS (UTC)

# Code to check deployment times
for ins in ['CTD_bottom', 'CTD_sfc', 'TD_2', 'TD_4', 'TD_38']:
    rbr = RSK(rsk[ins]); rbr.open(); rbr.readdata();
    plt.plot(rbr.data['timestamp'], rbr.data['pressure'], label=ins)
plt.legend()

# load data from files
rbr = {}
for ins in rsk.keys():
    rbr[ins] = IMS.load_RSK(rsk[ins], time_start[ins], time_end[ins])

#
# Create arrays for each variable
#

# I think the below needs to be year-specific!

# Temperature
# NOTE: Reorder Tstring nodes. First node starts at the bottom of the string (AKA #12 labeled on string). 
# TS_correct_order = [1,8,9,2,7,10,3,6,11,4,5,12] # node number, bottom to top
# Note variable name (temperaturei) is such that i = node - 1
# TS_depth_vals = np.arange(3.4,34,2.77)*-1 # Top node at 3.4m, each node spaced 2.77m apart
# Near-surface + TDs + Tstring (10 s sample rate)
T = np.zeros((len(rbr['CTD_sfc'].data), 16))
pT = np.zeros((len(rbr['CTD_sfc'].data), 16))
T[:,0] = rbr['CTD_sfc'].data['temperature'] # CTD 1.5 m
pT[:,0] = rbr['CTD_sfc'].data['pressure']
T[:,1] = rbr['TD_2'].data['temperature'] # TD 2.4 m
pT[:,1] = rbr['TD_2'].data['pressure']
T[:,2] = rbr['Tstring'].data['temperature11'] # Tstring 3.4 m
pT[:,2] = np.nan*rbr['CTD_sfc'].data['pressure']
T[:,3] = rbr['TD_4'].data['temperature'] # TD 4.25 m
pT[:,3] = rbr['TD_4'].data['pressure']
T[:,4] = rbr['Tstring'].data['temperature4'] # Tstring 6.17 m
pT[:,4] = np.nan*rbr['CTD_sfc'].data['pressure']
T[:,5] = rbr['Tstring'].data['temperature3'] # Tstring 8.94 m
pT[:,5] = np.nan*rbr['CTD_sfc'].data['pressure']
T[:,6] = rbr['Tstring'].data['temperature10'] # Tstring 11.71 m
pT[:,6] = np.nan*rbr['CTD_sfc'].data['pressure']
T[:,7] = rbr['Tstring'].data['temperature5'] # Tstring 14.48 m
pT[:,7] = np.nan*rbr['CTD_sfc'].data['pressure']
T[:,8] = rbr['Tstring'].data['temperature2'] # Tstring 17.25 m
pT[:,8] = np.nan*rbr['CTD_sfc'].data['pressure']
T[:,9] = rbr['Tstring'].data['temperature9'] # Tstring 20.02 m
pT[:,9] = np.nan*rbr['CTD_sfc'].data['pressure']
T[:,10] = rbr['Tstring'].data['temperature6'] # Tstring 22.79 m
pT[:,10] = np.nan*rbr['CTD_sfc'].data['pressure']
T[:,11] = rbr['Tstring'].data['temperature1'] # Tstring 25.56 m
pT[:,11] = np.nan*rbr['CTD_sfc'].data['pressure']
T[:,12] = rbr['Tstring'].data['temperature8'] # Tstring 28.33 m
pT[:,12] = np.nan*rbr['CTD_sfc'].data['pressure']
T[:,13] = rbr['Tstring'].data['temperature7'] # Tstring 31.1 m
pT[:,13] = np.nan*rbr['CTD_sfc'].data['pressure']
T[:,14] = rbr['Tstring'].data['temperature'] # Tstring 33.87 m
pT[:,14] = np.nan*rbr['CTD_sfc'].data['pressure']
T[:,15] = rbr['TD_38'].data['temperature'] # TD 38 m
pT[:,15] = rbr['TD_38'].data['pressure']
tT = rbr['CTD_sfc'].data['timestamp']
ds_TS = xr.Dataset(
            data_vars=dict(
                T=(['time', 'z'], T),
                p=(['time', 'z'], pT)
            ),
            coords=dict(
                time=tT,
                z=[1.5, 2.4, 3.4, 4.25, 6.17, 8.94, 11.71, 14.48, 17.25, 20.02, 22.79, 25.56, 28.33, 31.1, 33.87, 38.]
            ),
            attrs=dict(description='CTD, TD, and Tstring Temperature data at 1.5, 2.4, 3.4, 4.25, 6.17, 8.94, 11.71, 14.48, 17.25, 20.02, 22.79, 25.56, 28.33, 31.1, 33.87, 38. m'))
# Bottom (10 s sample rate)
T = np.zeros((len(rbr['CTD_bottom'].data), 1))
pS = np.zeros((len(rbr['CTD_bottom'].data), 1))
T[:,0] = rbr['CTD_bottom'].data['temperature']
pS[:,0] = rbr['CTD_bottom'].data['pressure']
tS = rbr['CTD_bottom'].data['timestamp']
ds_TD = xr.Dataset(
            data_vars=dict(
                T=(['time', 'z'], T),
                p=(['time', 'z'], pS)
            ),
            coords=dict(
                time=tS,
                z=[55.0]
            ),
            attrs=dict(description='CTD Temperature data at bottom (~55 m)'))
# Resample to hourly, and join both arrays
ds_TS = ds_TS.resample(time='1h').mean('time')
ds_TD = ds_TD.resample(time='1h').mean('time')
ds_T = xr.merge([ds_TS, ds_TD], join="outer")
ds_T = ds_T.assign_attrs(description='CTD, TD and Tstring Temperatre data at 1.5, 2.4, 3.4, 4.25, 6.17, 8.94, 11.71, 14.48, 17.25, 20.02, 22.79, 25.56, 28.33, 31.1, 33.87, 38., 55 m. T is in situ temperature, PT is potential temperature, CT is conservative temperature.')

# Salinity
# Near-surface (10 s sample rate)
S = np.zeros((len(rbr['CTD_sfc'].data), 1))
pS = np.zeros((len(rbr['CTD_sfc'].data), 1))
S[:,0] = rbr['CTD_sfc'].data['salinity']
pS[:,0] = rbr['CTD_sfc'].data['pressure']
tS = rbr['CTD_sfc'].data['timestamp']
ds_SS = xr.Dataset(
            data_vars=dict(
                S=(['time', 'z'], S),
                p=(['time', 'z'], pS)
            ),
            coords=dict(
                time=tS,
                z=[1.5]
            ),
            attrs=dict(description='CTD Salinity data at 1.5 m'))
# Bottom (10 s sample rate)
S = np.zeros((len(rbr['CTD_bottom'].data), 1))
pS = np.zeros((len(rbr['CTD_bottom'].data), 1))
S[:,0] = rbr['CTD_bottom'].data['salinity']
pS[:,0] = rbr['CTD_bottom'].data['pressure']
tS = rbr['CTD_bottom'].data['timestamp']
ds_SD = xr.Dataset(
            data_vars=dict(
                S=(['time', 'z'], S),
                p=(['time', 'z'], pS)
            ),
            coords=dict(
                time=tS,
                z=[55.0]
            ),
            attrs=dict(description='CTD Salinity data at bottom (~55 m)'))
# Resample to hourly, and join both arrays
ds_SS = ds_SS.resample(time='1h').mean('time')
ds_SD = ds_SD.resample(time='1h').mean('time')
ds_S = xr.merge([ds_SS, ds_SD], join="outer")

#
# Calculate Absolute Salinity and Conservative Temperature, as well as density
#

# Pressure in the below needs to be sea pressure
# This is estimated to be 10.1285 dbar from the weather station in 2026

# Calculate Absolute Salinity (SA), and assign as new variable to Dataset
ds_S['SA'] = (['time', 'z'], gsw.SA_from_SP(ds_S.S.data, ds_S.p.data-10.1285, -59.671, 54.959))

# Calculate density
ds_S['rho'] = (['time', 'z'], ds_S.SA.data.copy())
for zi in ds_S.z.data:
    ds_S['rho'].loc[dict(z=zi)] = gsw.rho_t_exact(ds_S.SA.sel(z=zi).data, ds_T.T.sel(z=zi).data, ds_S.p.sel(z=zi).data-10.1285)

# Add attribute
ds_S = ds_S.assign_attrs(description='CTD Salinity data at 1.5 55.0 m. S is Practical Salinity. SA is Absolute Salinity (g/kg). rho is in situ density (kg/m3).')

# Calculate Potential Temperature (PT) and Conservative Temperature (CT)
# Need salinity to calculate 
# Don't have S for all points where we have T, so can't do this in general...
z_S = ds_S.z.data
z_T = ds_T.z.data
which = np.in1d(z_T, z_S) # Which temperature depths have salinity data
PT = np.nan*np.zeros(ds_T.T.shape)
CT = np.nan*np.zeros(ds_T.T.shape)
for i in range(len(which)):
    if which[i]: # For those depths where we have both temperature and salinity (i.e. CTD)
        zi = z_T[i]
        PT[:,i] = gsw.pt_from_t(ds_S.SA.sel(z=zi).data, ds_T.T.sel(z=zi).data, ds_T.p.sel(z=zi).data-10.1285, 0.)
        CT[:,i] = gsw.CT_from_pt(ds_S.SA.sel(z=zi).data, PT[:,i])
# Insert into datasets (both the temperature and the salinity arrays)
ds_T['PT'] = (['time', 'z'], PT)
ds_T['CT'] = (['time', 'z'], CT)

#
# Save data as netcdf files
#

nc = ds_T.to_netcdf(pathroot + '/data/' + year + '/RBR_IMS/RBR_temperature.nc')
nc = ds_S.to_netcdf(pathroot + '/data/' + year + '/RBR_IMS/RBR_salinity_density.nc')

