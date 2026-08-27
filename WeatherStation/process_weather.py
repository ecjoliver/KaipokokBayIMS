'''
Create the weather station netcdf file and plot the summary onto one big subplot
'''

#
# Some globals
#

# Some globals
exec(open('../globals.py').read()) # modules, year, pathroot
time_start = {}
time_end = {}
time_start['2024'] = '2024-01-25T16:00.000000000' # Deployment YYYY-MM-DDTHH:MM.MMMM (UTC)
time_end['2024'] = '2024-04-17T12:00.000000000' # Recovery YYYY-MM-DDTHH:MM.MMMM (UTC)
time_start['2025'] = '2025-02-19T14:00.000000000' # Deployment YYYY-MM-DDTHH:MM.MMMM (UTC)
time_end['2025'] = '2025-04-11T00:00.000000000' # Recovery YYYY-MM-DDTHH:MM.MMMM (UTC)
time_start['2026'] = '2026-02-06T00:00.000000000' # Deployment YYYY-MM-DDTHH:MM.MMMM (UTC)
time_end['2026'] = '2026-04-21T14:30.000000000' # Recovery YYYY-MM-DDTHH:MM.MMMM (UTC)

#
# A. Process weather station SD card data to netcdf
#

# Load files from current working directory
path = os.path.join(pathroot, 'data', year, 'WeatherStation', 'Converted', 'TOA5_TEN_MINS*')
files = IMS.find_unique_filenames(path)
df = pd.read_csv(files[0],sep=',',skiprows=1) # Index 0 which files will be appended to
# Append all files into one pandas dataframe
for i in range(1, len(files)):
    temp_df = pd.read_csv(files[i],skiprows=1)
    # df = df.append(temp_df)
    df = pd.concat([df, temp_df])

# Clean datafiles
df = df.drop(labels=[0,1]) # Drop rows with unit and sample type
df = df.drop(['RECORD','MetSENS_Status'],axis=1)
# Drop duploicates and sort by chronological order
df = df.drop_duplicates().sort_values(by='TIMESTAMP')
# Set the index to time
df_ = df.set_index('TIMESTAMP')
ds = df_.to_xarray() # Convert to xarray dataset
ds = ds.rename( 
    {'TIMESTAMP': 'time',
    }
)

# Sort by time
ds['time'] = pd.DatetimeIndex(ds['time'].values) # convert to datetime
ds = ds.astype(float) # conversion makes array into strings, so convert values to float

# Reduce to deployment time period
ds = ds.sel(time=slice(time_start[year], time_end[year]))

# Save as NetCDF
nc = ds.to_netcdf(pathroot + '/data/' + year + '/WeatherStation/WeatherVars_SD.nc') # Save to netCDF file

#
# B. Process data from CR1000X logger - complete weather station data
#

# Load data
df = pd.read_csv(pathroot + '/data/' + year + '/WeatherStation/Logger/CR1000X_Ten_min_complete.dat',sep=',',skiprows=1)

# Clean datafiles
df = df.drop(labels=[0,1]) # Drop rows with unit and sample type
df = df.drop(['RECORD','MetSENS_Status'],axis=1)
# Drop duploicates and sort by chronological order
df = df.drop_duplicates().sort_values(by='TIMESTAMP')
# Set the index to time
df_ = df.set_index('TIMESTAMP')
ds = df_.to_xarray() # Convert to xarray dataset
ds = ds.rename( 
    {'TIMESTAMP': 'time',
    }
)

# Sort by time
ds['time'] = pd.DatetimeIndex(ds['time'].values) # convert to datetime
ds = ds.astype(float) # conversion makes array into strings, so convert values to float

# Relative Humidity calculation - must be calculated from Dew point and air temp because it was not chosen as an output variable when setting up the logger
TD = ds.DP_C_Avg # Dew point
Ta = ds.AirT_C_Avg # air temp
RH = 100*(np.exp((17.625*TD)/(243.04+TD))/np.exp((17.625*Ta)/(243.04+Ta))) # Relative humidity
ds = ds.assign({"RH":RH}) # Add humidity to the dataset

# Reduce to deployment time period
ds = ds.sel(time=slice(time_start[year], time_end[year]))

# Save as NetCDF
nc = ds.to_netcdf(pathroot + '/data/' + year + '/WeatherStation/WeatherVars_CR1000X.nc') # Save to netCDF file

