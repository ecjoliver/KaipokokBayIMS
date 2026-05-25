import glob
import numpy as np
import scipy as sp
from scipy import interpolate as interp
import xarray as xr
import pandas as pd
import os
from pyrsktools import RSK
# import sympy as sp
import inspect
from matplotlib.colors import LinearSegmentedColormap
from datetime import date

# Ice Monitoring Site toolbox

def find_unique_filenames(path):
    '''Search in subdirectories for unique filenames'''
    unique_filenames = []

    # Use glob to get all files in the directory and its subdirectories
    all_files = glob.glob(path, recursive=True)

    for file in all_files:
        if os.path.isfile(file):  # Check if it's a file (not a directory)
            filename = os.path.basename(file)

            if filename not in unique_filenames:
                unique_filenames.append(file) # List of filepaths for each unique file
                
    return unique_filenames

    # if __name__ == "__main__":
    #     files = find_unique_filenames(path)


def load_CTD_cast(csv_filename):
    '''Load a single CTD cast from a CSV and convert the time to datetime'''
    # Load CTD data
    data = pd.read_csv(filename)
    matlab_datenums = data['Time'].astype(float)

    # Convert MATLAB serial dates to datetime
    data['Time'] = pd.to_datetime(matlab_datenums-719529, unit='D') 

    return data


def load_RSK(RSK_filename, t1, t2):
    '''
    Load RSK file for IMS data
    Convert conductivity to salinity and pressure to depth. Subset times to match IMS timeseries
    '''

    rsk = RSK(RSK_filename)
    rsk.open()
    # Start on the 26th to match weather station data (the shortest time series), even though data starts on 23rd
    rsk.readdata(t1, t2)
    if 'conductivity' in rsk.channelNames:
        rsk.derivesalinity() # add salinity to channels
    rsk.deriveseapressure()
    rsk.derivedepth()
    return rsk

def DoodsonX0(ts):
    '''
    Running Avgerage on data of using Doodson X0 filter.
    Filter weights are designed to remove the main tidal
    consituents of hourly data. Filter is 39 points long
    and so both the first and last 19 points of 'avg' are
    made into NaNs.

    Filter found here: http://www.pol.ac.uk/ntslf/acclaimdata/gloup/doodson_X0.html

    Adapted from MATLAB code by Eric Oliver, 14 Aug 2019
    '''
    X0 = np.array([1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 2, 0, 1, 1, 0, 2, 1, 1, 2, 0, 2, 1, 1, 2, 0, 1, 1, 0, 2, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1])/30.
    ts_smooth = np.convolve(ts, X0, mode='same')
    ts_smooth[:19] = np.nan 
    ts_smooth[-19:] = np.nan
    return ts_smooth

def nan_helper(y):
    """Helper to handle indices and logical indices of NaNs.

    Input:
        - y, 1d numpy array with possible NaNs
    Output:
        - nans, logical indices of NaNs
        - index, a function, with signature indices= index(logical_indices),
        to convert logical indices of NaNs to 'equivalent' indices
    """
    return np.isnan(y), lambda z: z.nonzero()[0]

def stretch1d(y,arr_size):
    '''
    stretch numpy array "y" to match another array's ("arr_size") size through linear interpolation 
    '''
    # interpolate across nans first
    nans,x = nan_helper(y)
    y[nans] = np.interp(x(nans), x(~nans), y[~nans]) 

    # Interpolate updated arrays to match new array size
    y_interp = sp.interpolate.interp1d(np.arange(y.size),y)
    y_stretch = y_interp(np.linspace(0,y.size-1,arr_size.size))

    return y_stretch


def load_Rway_station_data(file, var_str):
    '''
    Load Robert Way's weather station data into an xarray datarray (one variable only)
    '''
    # Make a new xarray with only time as datetime and air temp as floats

    file_xarr = file.to_xarray()
    time = file_xarr['time'][1:]
    var_ = file_xarr[var_str][1:]
    ds = xr.DataArray(
        data=var_.astype(float), # convert from object to float
        dims=["time"],
        coords=dict(
            time=pd.to_datetime(time).values, # convert to datetime
        ),
        # attrs=dict(
        #     description="Average temperature",
        #     units="degC",
        # ),
    )

    return ds


def load_postville_weather():
    '''
    Load Robert Way's weather station data into an xarray datarray
    '''

    filepath = './Weather/data/postville_weather_2020-2024.csv'
    df = pd.read_csv(filepath,low_memory=False)

    # remove unecessary stuff
    df_ = df.drop(index=0) # row of units
    df_ = df_.drop(['longitude','latitude','station_name','stat_num','wsc_num'],axis=1)
    # Convert time to datetime (not sure why this is necessary, but must be done)
    df_['time'] = pd.to_datetime(df_['time'])
    df_ = df_.set_index('time')
    # Convert to xarray
    ds = df_.to_xarray()
    ds =  ds.astype(float)
    # Convert ot datetime64 
    ds['time'] = pd.DatetimeIndex(ds['time'].values) 

    return ds



def fit_linear_2d(x_2d, y_2d):
    '''
    Fit linear regression function through a set of 2-d data arrays
    '''
    # Flatten the 2D datasets
    x_flat = x_2d.values.flatten()
    y_flat = y_2d.values.flatten()
    
    # Create a mask where both x and y are not NaN
    mask = ~np.isnan(x_flat) & ~np.isnan(y_flat)
    
    # Apply the mask to filter valid values
    x_valid = x_flat[mask]
    y_valid = y_flat[mask]
    
    # Perform linear regression on the valid data
    slope, intercept, r_value, p_value, std_err = sp.stats.linregress(x_valid, y_valid)
    
    return slope, intercept, r_value, p_value, std_err

def cross_corr(ts1, ts2):
    """
    Compute the cross-correlation between two time series.

    Parameters:
    ts1 (array-like): First time series.
    ts2 (array-like): Second time series (must have the same length as ts1).
    max_lag (int, optional): Maximum lag for cross-correlation. Default is length of the series - 1.

    Returns:
    lags (np.ndarray): Array of lag values.
    correlation (np.ndarray): Cross-correlation values at each lag.
    """

    # Calculate mean and standardize the series (zero mean for normalization)
    ts1_mean = np.nanmean(ts1)
    ts2_mean = np.nanmean(ts2)
    ts1_std = np.std(ts1)
    ts2_std = np.std(ts2)

    ts1_norm = (ts1 - ts1_mean) / ts1_std
    ts2_norm = (ts2 - ts2_mean) / ts2_std

    # Compute cross-correlation using numpy.correlate
    # MAsk out nans
    valid = ~np.isnan(ts1*ts2)
    corr = np.correlate(ts1_norm[valid], ts2_norm[valid], mode='full')
    
    # Normalize by length
    corr /= len(ts1)
    
    # Define lags
    # the valid mask is only good if the nans are at the edges...
    lags = np.arange(-len(ts1[valid]) + 1, len(ts1[valid]))
    

    return lags, corr

# General error propagation function
def error_propagation_func(func, variables, uncertainties=None):
    '''
    Calculate the uncertainty of a function output using generic error propagation

    sig_y = sqrt[(dy/da * sig_a)^2 + (dy/db * sig_b)^2 + ...]

    Parameters: 
    - a function (func), 
    - an array of variables that are the inputs to func (variables), 
    - the uncertainties associated with each variable (uncertainties)
    
    Returns: the propagated uncertainty
    '''
    # Get the names of the variables from the function signature
    signature = inspect.signature(func)
    variable_names = list(signature.parameters.keys())  # Extract parameter names from function signature
    
    # Define symbolic variables (same as input function's variables)
    symbols = sp.symbols(variable_names)

    # Define the symbolic function 
    f_sym = func(*symbols)
    
    # Compute the partial derivatives of the function with respect to each variable
    partial_derivatives = [sp.diff(f_sym, symbol) for symbol in symbols]
    
    # Compute the uncertainties if provided
    uncertainty = 0
    if uncertainties:
        for i, partial in enumerate(partial_derivatives):
            # Evaluate the partial derivative at the input values (substitute actual variable values)
            partial_value = np.array([float(partial.subs(dict(zip(symbols, variables_vals)))) 
                                     for variables_vals in zip(*variables)])
            uncertainty += (partial_value * uncertainties[i])**2
        
        uncertainty = np.sqrt(uncertainty)
    
    return uncertainty


def error_propagation(partial_derivatives,uncertainties):
    """
    Calculate the total uncertainty from partial derivatives and uncertainties.

    Parameters:
    partial_derivatives (list): List of partial derivatives of the function with respect to each variable.
    uncertainties (list): List of uncertainties corresponding to the variables.

    Returns:
    float: The total propagated uncertainty.
    """

    # Initialize total uncertainty
    total_uncertainty = 0
    
    # Sum the squared contributions of each term
    for i in range(len(partial_derivatives)):
        total_uncertainty += (partial_derivatives[i] * uncertainties[i]) ** 2
    
    # Return the square root of the total sum of squared uncertainties
    return np.sqrt(total_uncertainty)




def sensible_heat_flux(U_wd, T_s, T_a, sigma_Uwd=None, sigma_Ts=None, sigma_Ta=None):
    '''
    Calculate Fsens with optional error calculation
    '''
    fsh = 1.22 * 1005 * 1.75 * 10**(-3)
    # c_H = 2e-3 # Konda & Yamazawa, 1986; Andreas 2002
    # rho_a = 1.22 #kg/m3
    # c_p = 1005 # Specific heat capacity of air
    # fsh = c_H * rho_a * c_p
    # T_a - T_s means positive down (into the ice)
    F_sens = fsh * U_wd * (T_s - T_a)

    if sigma_Uwd is not None:
        dFs_dUwd = fsh*(T_s - T_a)
        dFs_dTs = fsh
        dFs_dTa = -fsh

        # Total uncertainty propagation
        sigma_Fsens = np.sqrt(
            (dFs_dUwd * sigma_Uwd)**2 +
            (dFs_dTs * sigma_Ts)**2 +
            (dFs_dTa * sigma_Ta)**2
        )

        return F_sens, sigma_Fsens
    else:
        return F_sens






def latent_heat_flux(U_wd,RH,P,T_s,T_a):

    '''
    Calculate latent heat flux using the bulk aerodynamic formula
    '''
    rho_a = 1.22 # kg/m3 - atmospheric density
    L_s = 2.83e6 # J/kg - latent heat of sublimation (or vaporization)
    c_E = 1.6e-3 # Latent heat transfer coefficient (value from Vihma et al. 2009)


    e_s_air = calculate_es_ice(T_a) # In air
    e_s_snow = calculate_es_ice(T_s) # Snow surface

    # Specific humidity of air calculated from relative humidity
    e_ = RH/100 * e_s_air

    q_a = calculate_qs(P,e_) # Actual specific humidity, g/kg
    q_s = calculate_qs(P,e_s_snow) # Snow surface specific humidity, Assume saturated so RH = 1\

    return rho_a*L_s*c_E*U_wd*(q_s - q_a)



def calculate_es_ice(T):
    # Calculate the saturated vapour pressure over ice using Arden-Buck equations (1996)
    # units: Pa
    e_s_ice = 6.1115*np.exp((23.036 - T/333.7)*(T/(279.82 + T))) * 100 #hPa to Pa
    return e_s_ice


def calculate_es_water(T):
    # Calculate the saturated vapour pressure over water using Arden-Buck equations (1996)
    # units: Pa
    e_s_water = 6.1121*np.exp((18.678 - T/234.5)*(T/(257.14 + T))) * 100 # hPa to Pa
    return e_s_water

# Calculate specific humidity or air (q_a) and snow surface (q_s)

def calculate_qs(P,e_s):
    # Calculate the specific humidity given pressure (P) and the saturated vapour pressure (e_s)
    # Units: kg/kg
    # 0.622 is the ratio of water vapour:air mass
    q_s = 0.622*e_s/(P-0.378*e_s)/1000 # g/kg to kg/kg
    return q_s



def add_to_dataset(ds, name, values, time=None, attrs=None):
    """
    Add a 1D timeseries to an xarray.Dataset.

    Parameters:
    -----------
    ds : xr.Dataset
        The original dataset to which the timeseries will be added.
    name : str
        Name of the new variable to add.
    values : array-like
        Data values for the timeseries (must align with `time`).
    time : array-like or None
        Time coordinate for the timeseries. If None, will use ds.time.
    attrs : dict or None
        Optional attributes to assign to the new variable.

    Returns:
    --------
    xr.Dataset
        A new dataset with the timeseries added.
    """

    time = ds['time'].values

    da = xr.DataArray(values, coords={'time': time}, dims='time', name=name)
    if attrs:
        da.attrs.update(attrs)

    return ds.assign({name: da})


def SIMBA_to_da(path):
    '''Search in path directory for data files and combine them into one DataArray '''
    files = sorted(glob.glob(path))
    df = pd.read_fwf(files[0], header=None) # Index 0 which files will be appended to

    for i in range(1, len(files)):
        temp_df = pd.read_fwf(files[i], header=None)
        df = df.append(temp_df)

    time = pd.to_datetime(df.loc[:,1] + ' ' + df.loc[:,2])

    # Store data in Data Array
    da = xr.DataArray(
        data=df.loc[:,8:],
        dims=["time","node"],
        coords=dict(
            time=time,
        ),
    )

    return da


def climatology(t, temp, climatologyPeriod=[None,None], pctile=90, windowHalfWidth=5, smoothPercentile=True, smoothPercentileWidth=31, maxPadLength=False, Ly=False):
    '''

    Calculates a climatology, following the Hobday et al. (2016) marine heat wave definition

    Inputs:

      t       Time vector, in datetime format (e.g., date(1982,1,1).toordinal())
              [1D numpy array of length T]
      temp    Temperature vector [1D numpy array of length T]

    Outputs:

      clim    Climatology of SST. Each key (following list) is a seasonally-varying
              time series [1D numpy array of length T] of a particular measure:

        'thresh'               Seasonally varying threshold (e.g., 90th percentile)
        'seas'                 Climatological seasonal cycle
        'missing'              A vector of TRUE/FALSE indicating which elements in 
                               temp were missing values for the MHWs detection

    Options:

      climatologyPeriod      Period over which climatology is calculated, specified
                             as list of start and end years. Default is to calculate
                             over the full range of years in the supplied time series.
                             Alternate periods suppled as a list e.g. [1983,2012].
      pctile                 Threshold percentile (%) for detection of extreme values
                             (DEFAULT = 90)
      windowHalfWidth        Width of window (one sided) about day-of-year used for
                             the pooling of values and calculation of threshold percentile
                             (DEFAULT = 5 [days])
      smoothPercentile       Boolean switch indicating whether to smooth the threshold
                             percentile timeseries with a moving average (DEFAULT = True)
      smoothPercentileWidth  Width of moving average window for smoothing threshold
                             (DEFAULT = 31 [days])
      maxPadLength           Specifies the maximum length [days] over which to interpolate
                             (pad) missing data (specified as nans) in input temp time series.
                             i.e., any consecutive blocks of NaNs with length greater
                             than maxPadLength will be left as NaN. Set as an integer.
                             (DEFAULT = False, interpolates over all missing values).
      Ly                     Specifies if the length of the year is < 365/366 days (e.g. a 
                             360 day year from a climate model). This affects the calculation
                             of the climatology. (DEFAULT = False)

    Notes:

      1. This function assumes that the input time series consist of continuous daily values
         with few missing values. Time ranges which start and end part-way through the calendar
         year are supported.

      2. This function supports leap years. This is done by ignoring Feb 29s for the initial
         calculation of the climatology and threshold. The value of these for Feb 29 is then
         linearly interpolated from the values for Feb 28 and Mar 1.

    Written by Eric Oliver, Institue for Marine and Antarctic Studies, University of Tasmania, Feb 2015
    Updated for Ice Monitoring Site by Eric Oliver, Department of Oceanography, Dalhousie University, May 2026

    '''

    #
    # Time and dates vectors
    #

    # Generate vectors for year, month, day-of-month, and day-of-year
    T = len(t)
    year = np.zeros((T))
    month = np.zeros((T))
    day = np.zeros((T))
    doy = np.zeros((T))
    for i in range(T):
        year[i] = date.fromordinal(t[i]).year
        month[i] = date.fromordinal(t[i]).month
        day[i] = date.fromordinal(t[i]).day
    # Leap-year baseline for defining day-of-year values
    year_leapYear = 2012 # This year was a leap-year and therefore doy in range of 1 to 366
    t_leapYear = np.arange(date(year_leapYear, 1, 1).toordinal(),date(year_leapYear, 12, 31).toordinal()+1)
    dates_leapYear = [date.fromordinal(tt.astype(int)) for tt in t_leapYear]
    month_leapYear = np.zeros((len(t_leapYear)))
    day_leapYear = np.zeros((len(t_leapYear)))
    doy_leapYear = np.zeros((len(t_leapYear)))
    for tt in range(len(t_leapYear)):
        month_leapYear[tt] = date.fromordinal(t_leapYear[tt]).month
        day_leapYear[tt] = date.fromordinal(t_leapYear[tt]).day
        doy_leapYear[tt] = t_leapYear[tt] - date(date.fromordinal(t_leapYear[tt]).year,1,1).toordinal() + 1
    # Calculate day-of-year values
    for tt in range(T):
        doy[tt] = doy_leapYear[(month_leapYear == month[tt]) * (day_leapYear == day[tt])]

    # Constants (doy values for Feb-28 and Feb-29) for handling leap-years
    feb28 = 59
    feb29 = 60

    # Set climatology period, if unset use full range of available data
    if (climatologyPeriod[0] is None) or (climatologyPeriod[1] is None):
        climatologyPeriod[0] = year[0]
        climatologyPeriod[1] = year[-1]

    #
    # Calculate threshold and seasonal climatology (varying with day-of-year)
    #

    tempClim = temp.copy()
    TClim = np.array([T]).copy()[0]
    yearClim = year.copy()
    monthClim = month.copy()
    dayClim = day.copy()
    doyClim = doy.copy()

    # Pad missing values for all consecutive missing blocks of length <= maxPadLength
    if maxPadLength:
        temp = pad(temp, maxPadLength=maxPadLength)
        tempClim = pad(tempClim, maxPadLength=maxPadLength)

    # Length of climatological year
    lenClimYear = 366
    # Start and end indices
    clim_start = np.where(yearClim == climatologyPeriod[0])[0][0]
    clim_end = np.where(yearClim == climatologyPeriod[1])[0][-1]
    # Inialize arrays
    thresh_climYear = np.NaN*np.zeros(lenClimYear)
    seas_climYear = np.NaN*np.zeros(lenClimYear)
    clim = {}
    clim['thresh'] = np.NaN*np.zeros(TClim)
    clim['seas'] = np.NaN*np.zeros(TClim)
    # Loop over all day-of-year values, and calculate threshold and seasonal climatology across years
    for d in range(1,lenClimYear+1):
        # Special case for Feb 29
        if d == feb29:
            continue
        # find all indices for each day of the year +/- windowHalfWidth and from them calculate the threshold
        tt0 = np.where(doyClim[clim_start:clim_end+1] == d)[0] 
        # If this doy value does not exist (i.e. in 360-day calendars) then skip it
        if len(tt0) == 0:
            continue
        tt = np.array([])
        for w in range(-windowHalfWidth, windowHalfWidth+1):
            tt = np.append(tt, clim_start+tt0 + w)
        tt = tt[tt>=0] # Reject indices "before" the first element
        tt = tt[tt<TClim] # Reject indices "after" the last element
        thresh_climYear[d-1] = np.nanpercentile(tempClim[tt.astype(int)], pctile)
        seas_climYear[d-1] = np.nanmean(tempClim[tt.astype(int)])
    # Special case for Feb 29
    thresh_climYear[feb29-1] = 0.5*thresh_climYear[feb29-2] + 0.5*thresh_climYear[feb29]
    seas_climYear[feb29-1] = 0.5*seas_climYear[feb29-2] + 0.5*seas_climYear[feb29]

    # Smooth if desired
    if smoothPercentile:
        # If the length of year is < 365/366 (e.g. a 360 day year from a Climate Model)
        if Ly:
            valid = ~np.isnan(thresh_climYear)
            thresh_climYear[valid] = runavg(thresh_climYear[valid], smoothPercentileWidth)
            valid = ~np.isnan(seas_climYear)
            seas_climYear[valid] = runavg(seas_climYear[valid], smoothPercentileWidth)
        # >= 365-day year
        else:
            thresh_climYear = runavg(thresh_climYear, smoothPercentileWidth)
            seas_climYear = runavg(seas_climYear, smoothPercentileWidth)

    # Generate threshold for full time series
    clim['thresh'] = thresh_climYear[doy.astype(int)-1]
    clim['seas'] = seas_climYear[doy.astype(int)-1]

    # Save vector indicating which points in temp are missing values
    clim['missing'] = np.isnan(temp)
    # Set all remaining missing temp values equal to the climatology
    temp[np.isnan(temp)] = clim['seas'][np.isnan(temp)]

    return clim

def runavg(ts, w):
    '''

    Performs a running average of an input time series using uniform window
    of width w. This function assumes that the input time series is periodic.

    Inputs:

      ts            Time series [1D numpy array]
      w             Integer length (must be odd) of running average window

    Outputs:

      ts_smooth     Smoothed time series

    Written by Eric Oliver, Institue for Marine and Antarctic Studies, University of Tasmania, Feb-Mar 2015

    '''
    # Original length of ts
    N = len(ts)
    # make ts three-fold periodic
    ts = np.append(ts, np.append(ts, ts))
    # smooth by convolution with a window of equal weights
    ts_smooth = np.convolve(ts, np.ones(w)/w, mode='same')
    # Only output central section, of length equal to the original length of ts
    ts = ts_smooth[N:2*N]

    return ts

def runavg_ecj(ts, w, mode='same'):
    '''     
    Perform running average of ts (1D numpy array) using uniform window
    of width w (w must be odd). Option 'mode' specifies if output should
    be defined over only the 'valid' range of of the data/window convolution
    (in which case the output is padded with NaNs outside the valid range)
    or over the 'same' range as the original data.
    '''
    if mode == 'same':
        ts_smooth = np.convolve(ts, np.ones(w)/w, mode=mode)
    elif mode == 'valid':
        ts_smooth = np.append(np.append(np.nan*np.ones(int((w-1)/2)), np.convolve(ts, np.ones(w)/w, mode=mode)), np.nan*np.ones(int((w-1)/2)))
    return ts_smooth

def interpSectionStitch(sites, ctd, coord, field, dx):
    '''
    Stitch together a series of station-to-station interpolations
    to build up an interpolated section.
    
    dx    - step in section axis
    sites - which locations/sites to use for section
    ctd   - xarray Dataset of ctd data
    coord - coordinates of ctd sites (longitude/latitude)
    field - name of oceanographic field to interpolate
    '''
    # Initialize some variables
    x1 = 999
    x2 = -999
    d2 = -999

    for i,site in enumerate(sites):
        x1 = min(coord[i], x1)
        x2 = max(coord[i], x2)
        d2 = max(ctd.sel(site=site)['Depth'].max().values, d2)

    # Interpolation coordinates
    dd = 0.05
    depth_sec = np.arange(0, d2 + dd, dd)
    x_sec = np.zeros((0,))
    field_sec = np.zeros((len(depth_sec), 0))

    Nsites = len(sites)
    # Build up interpolated section
    for i in range(Nsites - 1):
        # Interpolate over a grid
        x_sec0 = np.arange(coord[i], coord[i+1], dx)
        xx_sec0, ddepth_sec0 = np.meshgrid(x_sec0, depth_sec)
        field_sec0, _, _ = interpSection(x_sec0, depth_sec, sites[i:i+1+1], ctd, coord, field)

        # Add to full section arrays
        x_sec = np.append(x_sec, x_sec0, axis=0)
        field_sec = np.append(field_sec, field_sec0, axis=1)

    xx_sec, ddepth_sec = np.meshgrid(x_sec, depth_sec)

    return field_sec, xx_sec, ddepth_sec

def interpSection(x_sec, depth_sec, sites, ctd, coord, field):
    '''
    Interpolate the ctd data at locations indicated by sites
    over the 2D grid given by x_sec, depth_sec. The x coordinate
    can either be latitude or longitude, given by coord ('lon'/'lat')
    '''
    # Interpolate over a grid
    xx_sec, ddepth_sec = np.meshgrid(x_sec, depth_sec)
    # Data points
    x_sparse = np.array([])
    depth_sparse = np.array([])
    field_sparse = np.array([])
    for i,site in enumerate(sites):
        site_data = ctd.sel(site=site)  # Select data for the current site
        valid = ~np.isnan(site_data[field].values)
        if valid.sum() == 0:
            continue # skip if all values are nans
        x_sparse = np.append(x_sparse, coord[ctd.site == site][0]*(site_data['Depth'][valid]*0+1))
        depth_sparse = np.append(depth_sparse, site_data['Depth'][valid])
        field_sparse = np.append(field_sparse, site_data[field][valid])

    field_sec = interp.griddata(np.array([x_sparse, depth_sparse]).T, field_sparse, (xx_sec, ddepth_sec), method='linear')
    
    return field_sec, xx_sec, depth_sec

def interpSectionStitch_time(times, ctd, coord, field, dx):
    '''
    Stitch together a series of date-to-date interpolations
    to build up an interpolated section.
    
    dx    - step in section axis
    times - which time values to use for section (datetime ordinal)
    ctd   - xarray Dataset of ctd data
    coord - coordinates of ctd sites (datetime ordinal)
    field - name of oceanographic field to interpolate
    '''
    # Initialize some variables
    x1 = 99999999999
    x2 = -99999999999
    d2 = -99999999999

    for i,time in enumerate(times):
        x1 = min(coord[i], x1)
        x2 = max(coord[i], x2)
        d2 = max(np.nanmax(ctd['Depth'].data[np.in1d(coord, time),:]), d2)

    # Interpolation coordinates
    dd = 0.05
    depth_sec = np.arange(0, d2 + dd, dd)
    x_sec = np.zeros((0,))
    field_sec = np.zeros((len(depth_sec), 0))

    Ntimes = len(times)
    # Build up interpolated section
    for i in range(Ntimes - 1):
        # Interpolate over a grid
        x_sec0 = np.arange(coord[i], coord[i+1], dx)
        xx_sec0, ddepth_sec0 = np.meshgrid(x_sec0, depth_sec)
        field_sec0, _, _ = interpSection_time(x_sec0, depth_sec, times[i:i+1+1], ctd, coord, field)

        # Add to full section arrays
        x_sec = np.append(x_sec, x_sec0, axis=0)
        field_sec = np.append(field_sec, field_sec0, axis=1)

    xx_sec, ddepth_sec = np.meshgrid(x_sec, depth_sec)

    return field_sec, xx_sec, ddepth_sec

def interpSection_time(x_sec, depth_sec, times, ctd, coord, field):
    '''
    Interpolate the ctd data at time points indicated by times
    over the 2D grid given by x_sec, depth_sec. The x coordinate
    will be a time array (datetime ordinal)
    '''
    #times_values = [pd.Timestamp(ctd.date.values[i]).toordinal() for i in range(len(ctd.date.values))]
    # Interpolate over a grid
    xx_sec, ddepth_sec = np.meshgrid(x_sec, depth_sec)
    # Data points
    x_sparse = np.array([])
    depth_sparse = np.array([])
    field_sparse = np.array([])
    for i,time in enumerate(times):
        #site_data = ctd.sel(site=site)  # Select data for the current site
        time_data_depth = ctd['Depth'].data[np.in1d(coord, time),:] # Select depth data for the current time
        time_data_field = ctd[field].data[np.in1d(coord, time),:] # Select field data for the current time
        valid = ~np.isnan(time_data_field)
        if valid.sum() == 0:
            continue # skip if all values are nans
        x_sparse = np.append(x_sparse, np.array(coord)[np.in1d(coord, time)][0]*(time_data_depth[valid]*0+1))
        depth_sparse = np.append(depth_sparse, time_data_depth[valid])
        field_sparse = np.append(field_sparse, time_data_field[valid])

    field_sec = interp.griddata(np.array([x_sparse, depth_sparse]).T, field_sparse, (xx_sec, ddepth_sec), method='linear')
    
    return field_sec, xx_sec, depth_sec



