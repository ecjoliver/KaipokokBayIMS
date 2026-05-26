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
# 2024
if year == '2024':
    rsk_botCTD = datapath + '/' + year + '/' + 'RBR/CTD_bottom/060699_20240416_0025.rsk' # bottom 
    rsk_CTD_0 = datapath + '/' + year + '/' + 'RBR/CTDs_from_Tstring/206045_20240416_2337.rsk' # 1.88 m
    rsk_CTD_1 = datapath + '/' + year + '/' + 'RBR/CTDs_from_Tstring/206046_20240416_2329.rsk' # 2.38 m
    rsk_TD_2 = datapath + '/' + year + '/' + 'RBR/TDs_from_Tstring/204292_20240414_1343.rsk' # 2.89 m
    rsk_TD_3 = datapath + '/' + year + '/' + 'RBR/TDs_from_Tstring/204337_20240414_1341.rsk' # 4.75 m
    rsk_TD_4 = datapath + '/' + year + '/' + 'RBR/TDs_from_Tstring/204291_20240417_1338.rsk' # 38 m
    rsk_TS = datapath + '/' + year + '/' + 'RBR/Tstring/204294_20240416_0047.rsk' # Thermistor string
# 2026
elif year == '2026':
    rsk['CTD_bottom'] = pathroot + '/data/' + year + '/RBR_IMS/CTD_Bottom/206045_20260420_2250.rsk' # Bottom CTD
    rsk['CTD_sfc'] = pathroot + '/data/' + year + '/RBR_IMS/CTD_nearSurface/206046_20260422_2121.rsk' # Near-surface CTD
    rsk['CTD_BGC_1'] = pathroot + '/data/' + year + '/RBR_IMS/CTD_BGC/208049_20260422_2106.rsk' # 1 m CTD w/ BGC
    rsk['CTD_BGC_5'] = pathroot + '/data/' + year + '/RBR_IMS/CTD_BGC/204289_20260422_2115.rsk' # 5 m CTD w/ BGC
    rsk['TD_2'] = pathroot + '/data/' + year + '/RBR_IMS/TD/204291_20260422_2125.rsk' # 2.4 m TD
    rsk['TD_4'] = pathroot + '/data/' + year + '/RBR_IMS/TD/204292_20260422_2128.rsk' # 4.25 m TD
    rsk['TD_38'] = pathroot + '/data/' + year + '/RBR_IMS/TD/204337_20260422_2130.rsk' # 38 m TD
    rsk['Tstring'] = pathroot + '/data/' + year + '/RBR_IMS/Tstring/204294_20260422_2135.rsk' # Tstring
    rsk['PAR'] = pathroot + '/data/' + year + '/RBR_IMS/PAR/203807_20260422_2110.rsk' # Tstring
    for ins in rsk.keys():
        time_start[ins] = '2026-02-03T21:00:00' # Deployment YYYY-MM-DDTHH:MM:SS (UTC)
        if ins == 'CTD_bottom':
            time_end[ins] = '2026-04-20T20:50:00' # Recovery YYYY-MM-DDTHH:MM:SS (UTC)
        else:
            time_end[ins] = '2026-04-21T14:14:00' # Recovery of non-bottom CTD instruments, ~+1 day...
        

# load data from files
rbr = {}
for ins in rsk.keys():
    rbr[ins] = IMS.load_RSK(rsk[ins], time_start[ins], time_end[ins])

#
# Create arrays for each variable
#

# I think the below needs to be year-specific!

# Temperature
# NOTE: Reorder Tstring nodes. Fitst node starts at the bottom of the string (AKA #12 labeled on string). 
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
# Bottom (10 s sample rate, shorter deployment)
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
# BGC CTDs (3 min sample rate)
T = np.zeros((len(rbr['CTD_BGC_1'].data), 2))
pB = np.zeros((len(rbr['CTD_BGC_1'].data), 2))
T[:,0] = rbr['CTD_BGC_1'].data['temperature']
T[:,1] = rbr['CTD_BGC_5'].data['temperature']
pB[:,0] = rbr['CTD_BGC_1'].data['pressure']
pB[:,1] = rbr['CTD_BGC_5'].data['pressure']
tB = rbr['CTD_BGC_1'].data['timestamp']
ds_TB = xr.Dataset(
            data_vars=dict(
                T=(['time', 'z'], T),
                p=(['time', 'z'], pB)
            ),
            coords=dict(
                time=tB,
                z=[1.0, 5.0]
            ),
            attrs=dict(description='CTD Temperature data at 1.0 m and 5.0 m'))
# Resample to hourly, and join both arrays
ds_TS = ds_TS.resample(time='1h').mean('time')
ds_TD = ds_TD.resample(time='1h').mean('time')
ds_TB = ds_TB.resample(time='1h').mean('time')
ds_T = xr.merge([ds_TS, ds_TD, ds_TB], join="outer")
ds_T = ds_T.assign_attrs(description='CTD, TD and Tstring Temperatre data at 1., 1.5, 2.4, 3.4, 4.25, 5., 6.17, 8.94, 11.71, 14.48, 17.25, 20.02, 22.79, 25.56, 28.33, 31.1, 33.87, 38., 55 m. T is in situ temperature, PT is potential temperature, CT is conservative temperature.')

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
# Bottom (10 s sample rate, shorter deployment)
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
# BGC CTDs (3 min sample rate)
S = np.zeros((len(rbr['CTD_BGC_1'].data), 2))
pB = np.zeros((len(rbr['CTD_BGC_1'].data), 2))
S[:,0] = rbr['CTD_BGC_1'].data['salinity']
S[:,1] = rbr['CTD_BGC_5'].data['salinity']
pB[:,0] = rbr['CTD_BGC_1'].data['pressure']
pB[:,1] = rbr['CTD_BGC_5'].data['pressure']
tB = rbr['CTD_BGC_1'].data['timestamp']
ds_SB = xr.Dataset(
            data_vars=dict(
                S=(['time', 'z'], S),
                p=(['time', 'z'], pB)
            ),
            coords=dict(
                time=tB,
                z=[1.0, 5.0]
            ),
            attrs=dict(description='CTD Salinity data at 1.0 m and 5.0 m'))
# Resample to hourly, and join both arrays
ds_SS = ds_SS.resample(time='1h').mean('time')
ds_SD = ds_SD.resample(time='1h').mean('time')
ds_SB = ds_SB.resample(time='1h').mean('time')
ds_S = xr.merge([ds_SS, ds_SD, ds_SB], join="outer")

# BGC variables
# zB
chlorophyll_counts = np.zeros((len(rbr['CTD_BGC_1'].data), 2))
cdom_counts = np.zeros((len(rbr['CTD_BGC_1'].data), 2))
backscatter_counts = np.zeros((len(rbr['CTD_BGC_1'].data), 2))
dissolved_o2_concentration = np.zeros((len(rbr['CTD_BGC_1'].data), 2))
dissolved_o2_concentration = np.zeros((len(rbr['CTD_BGC_1'].data), 2))
pB = np.zeros((len(rbr['CTD_BGC_1'].data), 2))
serial = np.zeros(2, dtype=int)
chlorophyll_counts[:,0] = rbr['CTD_BGC_1'].data['chlorophyll']
chlorophyll_counts[:,1] = rbr['CTD_BGC_5'].data['chlorophyll']
cdom_counts[:,0] = rbr['CTD_BGC_1'].data['cdom']
cdom_counts[:,1] = rbr['CTD_BGC_5'].data['cdom']
dissolved_o2_concentration[:,0] = rbr['CTD_BGC_1'].data['dissolved_o2_concentration']
dissolved_o2_concentration[:,1] = rbr['CTD_BGC_5'].data['dissolved_o2_concentration']
backscatter_counts[:,0] = rbr['CTD_BGC_1'].data['backscatter']
backscatter_counts[:,1] = rbr['CTD_BGC_5'].data['backscatter']
pB[:,0] = rbr['CTD_BGC_1'].data['pressure']
pB[:,1] = rbr['CTD_BGC_5'].data['pressure']
serial[0] = rbr['CTD_BGC_1'].instrument.serialID
serial[1] = rbr['CTD_BGC_5'].instrument.serialID
tB = rbr['CTD_BGC_1'].data['timestamp']
# Make xarray dataset
ds_BGC = xr.Dataset(
            data_vars=dict(
                chlorophyll_counts=(['time', 'z'], chlorophyll_counts),
                cdom_counts=(['time', 'z'], cdom_counts),
                dissolved_o2_concentration=(['time', 'z'], dissolved_o2_concentration),
                backscatter_counts=(['time', 'z'], backscatter_counts),
                p=(['time', 'z'], pB),
                serial=(['z'], serial)
            ),
            coords=dict(
                time=tB,
                z=[1.0, 5.0]
            ),
            attrs=dict(description='BGC CTD data at 1.0 m and 5.0 m'))
# Resample to hourly
ds_BGC = ds_BGC.resample(time='1h').mean('time')
ds_BGC['serial'] = (['z'], serial)

# PAR
PAR = np.zeros(rbr['PAR'].data.shape)
tP = rbr['PAR'].data['timestamp']
PAR[:] = rbr['PAR'].data['par']
serial = np.array([rbr['PAR'].instrument.serialID])
# Make xarray dataset
ds_PAR = xr.Dataset(
            data_vars=dict(
                PAR=(['time'], PAR)
            ),
            coords=dict(
                time=tP,
                z=[1.2]
            ),
            attrs=dict(description='PAR data at 1.2 m'))
# Resample to hourly
ds_PAR = ds_PAR.resample(time='1h').mean('time')
ds_PAR['serial'] = (['z'], serial)

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
ds_S = ds_S.assign_attrs(description='CTD Salinity data at 1.0 1.5 5.0 55.0 m. S is Practical Salinity. SA is Absolute Salinity (g/kg). rho is in situ density (kg/m3).')

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
# Convert BGC data to variables with units, based on calibration coefficients
#
# Convert ECOPuck BGC data to variables with units
ecocals = {}
ecocals[204289] = {}
ecocals[204289]['chlorophyll'] = [49., 0.0121] # Dark counts, scale factor; ug/L
ecocals[204289]['cdom'] = [50., 0.091] # Dark counts, scale factor; ppb
ecocals[204289]['backscatter'] = [36., 0.000002323] # Dark counts, scale factor; m-1 sr-1
ecocals[208049] = {}
ecocals[208049]['chlorophyll'] = [49., 0.0121] # Dark counts, scale factor; ug/L
ecocals[208049]['cdom'] = [50., 0.091] # Dark counts, scale factor; ppb
ecocals[208049]['backscatter'] = [50., 0.000002443] # Dark counts, scale factor; m-1 sr-1
# Make varables for scaled BGC data
ds_BGC['chlorophyll'] = (['time', 'z'], ds_BGC.chlorophyll_counts.data.copy())
ds_BGC['cdom'] = (['time', 'z'], ds_BGC.cdom_counts.data.copy())
ds_BGC['backscatter'] = (['time', 'z'], ds_BGC.backscatter_counts.data.copy())
# Scale each variable, and insert it into dataset
for zi in ds_BGC.z.data:
    serial = int(ds_BGC.sel(z=zi).serial.data)
    for var in ['chlorophyll', 'cdom', 'backscatter']:
        dark, scale = ecocals[serial][var]
        ds_BGC[var].loc[dict(z=zi)] = (ds_BGC.sel(z=zi)[var+'_counts'].data - dark)*scale

# Add oxygen saturation percent
ds_BGC['dissolved_o2_saturation'] = (['time', 'z'], ds_BGC.dissolved_o2_concentration.data.copy())
for zi in ds_BGC.z.data:
    O2sol = gsw.O2sol(ds_S.SA.sel(z=zi).data, ds_T.CT.sel(z=zi).data, ds_BGC.p.sel(z=zi).data-10.1285, -59.671, 54.959) # umol/kg
    ds_BGC['dissolved_o2_saturation'].loc[dict(z=zi)] = 100*ds_BGC.dissolved_o2_concentration.sel(z=zi).data/(O2sol*ds_S.rho.sel(z=zi).data*1e-3)

# Put units in dataset metadata
ds_BGC = ds_BGC.assign_attrs(description='BGC CTD data at 1.0 m and 5.0 m. chlorophyll has units ug/L, cdom of ppb, backscatter of m-1 sr-1. These variables _counts are the raw, unscaled ECOPuck count data. dissolved_o2_concentration has units of umol/L, dissolved_o2_saturation has units of %. PAR has units of umol/m2/s.')

#
# Save data as netcdf files
#

nc = ds_T.to_netcdf(pathroot + '/data/' + year + '/RBR_IMS/RBR_temperature.nc')
nc = ds_S.to_netcdf(pathroot + '/data/' + year + '/RBR_IMS/RBR_salinity_density.nc')
nc = ds_BGC.to_netcdf(pathroot + '/data/' + year + '/RBR_IMS/RBR_BGC.nc')
nc = ds_PAR.to_netcdf(pathroot + '/data/' + year + '/RBR_IMS/RBR_PAR.nc')

