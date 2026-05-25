'''
    Load weekly ice and snow thicknesses and generate a file from the data
''' 

import pandas as pd
import numpy as np
import xarray as xr
import os

# Some globals
pathroot = os.path.abspath('../../')
year = '2026'

# Load in Excel sheet of Site Visit (meta)data
df = pd.read_excel(pathroot + '/data/' + year + '/SiteVisits/SiteVisits_' + year + '_MetaData.xlsx', header=1)

# Make time index from date (ignore hour, unneeded at this scale)
df = df.rename(columns={'Date': 'time'})
df = df.set_index('time')

# Select ice and snow data columns
df = df[['Ice thickness (cm)', 'Water level (cm)', 'Snow depth in hole (cm)', 'Snow (1)', 'Snow (2)', 'Snow (3)', 'Snow (4)', 'Snow (5)', 'Snow (6)', 'Snow (7)', 'Snow (8)', 'Snow (9)']]

# Rename columns
df = df.rename(columns={'Ice thickness (cm)': 'hi'})
df = df.rename(columns={'Water level (cm)': 'hw'})
df = df.rename(columns={'Snow depth in hole (cm)': 'hs'})
df = df.rename(columns={'Snow (1)': 'hs_snowStake_1'})
df = df.rename(columns={'Snow (2)': 'hs_snowStake_2'})
df = df.rename(columns={'Snow (3)': 'hs_snowStake_3'})
df = df.rename(columns={'Snow (4)': 'hs_snowStake_4'})
df = df.rename(columns={'Snow (5)': 'hs_snowStake_5'})
df = df.rename(columns={'Snow (6)': 'hs_snowStake_6'})
df = df.rename(columns={'Snow (7)': 'hs_snowStake_7'})
df = df.rename(columns={'Snow (8)': 'hs_snowStake_8'})
df = df.rename(columns={'Snow (9)': 'hs_snowStake_9'})

# Save as xarray
ds = df.to_xarray()

# Calculate snow depth for each snow stake
ds['hs_snowStake_1'].data = 140. - ds['hs_snowStake_1'].data
ds['hs_snowStake_2'].data = 140. - ds['hs_snowStake_2'].data
ds['hs_snowStake_3'].data = 140. - ds['hs_snowStake_3'].data
ds['hs_snowStake_4'].data = 140. - ds['hs_snowStake_4'].data
ds['hs_snowStake_5'].data = 140. - ds['hs_snowStake_5'].data
ds['hs_snowStake_6'].data = 140. - ds['hs_snowStake_6'].data
ds['hs_snowStake_7'].data = 140. - ds['hs_snowStake_7'].data
ds['hs_snowStake_8'].data = 140. - ds['hs_snowStake_8'].data
ds['hs_snowStake_9'].data = 140. - ds['hs_snowStake_9'].data

# Calculate mean and std. dev. of snow depth across the 9 snow stakes
hs_mean = xr.zeros_like(ds.hs_snowStake_1)
hs_std = xr.zeros_like(ds.hs_snowStake_1)
hs_mean = (ds.hs_snowStake_1 + ds.hs_snowStake_2 + ds.hs_snowStake_3 + ds.hs_snowStake_4 + ds.hs_snowStake_5 + ds.hs_snowStake_6 + ds.hs_snowStake_7 + ds.hs_snowStake_8 + ds.hs_snowStake_9)/9.
hs_sd = np.sqrt((ds.hs_snowStake_1 - hs_mean)**2 + (ds.hs_snowStake_2 - hs_mean)**2 + (ds.hs_snowStake_3 - hs_mean)**2 + (ds.hs_snowStake_4 - hs_mean)**2 + (ds.hs_snowStake_5 - hs_mean)**2 + (ds.hs_snowStake_6 - hs_mean)**2 + (ds.hs_snowStake_7 - hs_mean)**2 + (ds.hs_snowStake_8 - hs_mean)**2 + (ds.hs_snowStake_9 - hs_mean)**2)/9
ds['hs_snowStake_mean'] = hs_mean
ds['hs_snowStake_sd'] = hs_sd

# Convert ice, snow and water to m
ds['hi'].data = ds['hi'].data/100.
ds['hw'].data = ds['hw'].data/100.
ds['hs'].data = ds['hs'].data/100.
ds['hs_snowStake_1'].data = ds['hs_snowStake_1'].data/100.
ds['hs_snowStake_2'].data = ds['hs_snowStake_2'].data/100.
ds['hs_snowStake_3'].data = ds['hs_snowStake_3'].data/100.
ds['hs_snowStake_4'].data = ds['hs_snowStake_4'].data/100.
ds['hs_snowStake_5'].data = ds['hs_snowStake_5'].data/100.
ds['hs_snowStake_6'].data = ds['hs_snowStake_6'].data/100.
ds['hs_snowStake_7'].data = ds['hs_snowStake_7'].data/100.
ds['hs_snowStake_8'].data = ds['hs_snowStake_8'].data/100.
ds['hs_snowStake_9'].data = ds['hs_snowStake_9'].data/100.
ds['hs_snowStake_mean'].data = ds['hs_snowStake_mean'].data/100.
ds['hs_snowStake_sd'].data = ds['hs_snowStake_sd'].data/100.

# Save as NetCDF file
nc = ds.to_netcdf(pathroot + '/data/' + year + '/SiteVisits/SiteVisits_Weekly_IceSnowWater.nc')

