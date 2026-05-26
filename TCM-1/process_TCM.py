'''
    Process TCM data and save NetCDF files
'''

# Some globals

exec(open('../globals.py').read()) # modules, year, pathroot

# Load the TCM data and save it into one xarray data array

df = {}
# 2024
if year == '2024':
    df_1_5m = pd.read_csv('TCM-1/data/2024/1-5m/2112071_Postville_1-5m_(0)_Current.csv',index_col=False,parse_dates=['ISO 8601 Time'])
    df_2m = pd.read_csv('TCM-1/data/2024/2m/2012078_Postville_2m_(0)_Current.csv',index_col=False,parse_dates=['ISO 8601 Time'])
# 2025
elif year == '2025':
    df_1m = pd.read_csv('TCM-1/data/2025/1m/2112070_Postville_1m_(0)_Current.csv',index_col=False,parse_dates=['ISO 8601 Time'])
    df_1_5m = pd.read_csv('TCM-1/data/2025/1-5m/2409063_Postville_1-5m_(0)_Current.csv',index_col=False,parse_dates=['ISO 8601 Time'])
    df_2m = pd.read_csv('TCM-1/data/2025/2m/2409062_Postville_2m_(0)_Current.csv',index_col=False,parse_dates=['ISO 8601 Time'])
# 2026
elif year == '2026':
    time_start = '2026-02-03T18:22:00.000000' # Deployment YYYY-MM-DDTHH:MM:SS.SSSSSS (UTC)
    time_end = '2026-04-20T18:46:00.000000' # Recovery YYYY-MM-DDTHH:MM:SS.SSSSSS (UTC)
    df['1.5'] = pd.read_csv(pathroot + '/data/' + year + '/TCM-1/2409063_IMS_1-5m_(0)_Current.csv',index_col=False,parse_dates=['ISO 8601 Time'])
    df['2.0'] = pd.read_csv(pathroot + '/data/' + year + '/TCM-1/2409062_IMS_2-0m_(0)_Current.csv',index_col=False,parse_dates=['ISO 8601 Time'])
    z = df.keys()

# Create xarray
for zi in z:
    df[zi] = df[zi].rename(columns={'ISO 8601 Time':'time'})
    df[zi] = df[zi].set_index('time')
    df[zi] = df[zi].to_xarray()

# Select only valid time period
for zi in z:
    df[zi] = df[zi].sel(time=slice(time_start, time_end))

# Combine into one xarray
df_tcm = []
z_list = []
for zi in z:
    df_tcm.append(df[zi])
    z_list.append(float(zi))

da_tcm = xr.concat(df_tcm, pd.Index(z_list, name='z'))

# Rename variables
da_tcm = da_tcm.rename({'Speed (cm/s)':'Speed','Heading (degrees)':'Heading','Velocity-N (cm/s)':'Velocity-N','Velocity-E (cm/s)':'Velocity-E'})

# Change units from cm/s to m/s
da_tcm['Velocity-N'] = da_tcm['Velocity-N']/100
da_tcm['Velocity-E'] = da_tcm['Velocity-E']/100
da_tcm['Speed'] = da_tcm['Speed']/100

# Convert to hourly
da_tcm_hourly = da_tcm.resample(time='1H').mean('time')

#
# Remove tides
#

# Detided variables
da_tcm_detided = xr.zeros_like(da_tcm_hourly)
# Loop over depth levels
for zi in z:
    da_tcm_detided['Velocity-E'].loc[dict(z=zi)] = IMS.DoodsonX0(da_tcm_hourly['Velocity-E'].sel(z=zi).values)
    da_tcm_detided['Velocity-N'].loc[dict(z=zi)] = IMS.DoodsonX0(da_tcm_hourly['Velocity-N'].sel(z=zi).values)
    da_tcm_detided['Speed'].loc[dict(z=zi)] = np.sqrt(da_tcm_detided['Velocity-E'].sel(z=zi)**2 + da_tcm_detided['Velocity-N'].sel(z=zi)**2)
    da_tcm_detided['Heading'].loc[dict(z=zi)] = np.arctan2(da_tcm_detided['Velocity-E'].sel(z=zi), da_tcm_detided['Velocity-N'].sel(z=zi))*180./np.pi

# Daily mean, detided time series
da_tcm_daily = da_tcm_detided.resample(time='1D').mean('time')

# Save to netcdf 
nc1 = da_tcm_hourly.to_netcdf(pathroot + '/data/' + year + '/TCM-1/TCM_currents_hourly.nc')
nc2 = da_tcm_detided.to_netcdf(pathroot + '/data/' + year + '/TCM-1/TCM_currents_detided.nc')
nc3 = da_tcm_daily.to_netcdf(pathroot + '/data/' + year + '/TCM-1/TCM_currents_daily.nc')

