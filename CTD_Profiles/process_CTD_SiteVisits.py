'''
    Load in CTD profiles from site visits
    Save CTD data as nc file
'''

import matplotlib as mpl
mpl.interactive(True)
from matplotlib import pyplot as plt
import numpy as np
from scipy import io
import pandas as pd
import cmocean
import gsw
import os
import xarray as xr
from datetime import datetime
import sys
sys.path.append(os.path.abspath('../../'))
from functions import IMS_toolbox as IMS

#
# Some globals
#

exec(open('../globals.py').read()) # year, pathroot

# Where the CTD data sits:
header = '/home/eoliver/Dropbox/Nunatsiavut_Futures/WP2_Data_Repository/CTD/'

# Time series details
community = 'Postville'
siteList = [['2026_02_02', 'IMS'], ['2026_02_09', 'IMS'], ['2026_02_18', 'IMS'], ['2026_02_24', 'IMS'], ['2026_03_02', 'IMS'], ['2026_03_12', 'IMS'], ['2026_03_19', 'IMS'], ['2026_03_26', 'IMS'], ['2026_04_01', 'IMS'], ['2026_04_10', 'IMS'], ['2026_04_16', 'IMS'], ['2026_04_17', 'IMS'], ['2026_04_18', 'IMS'], ['2026_04_23', 'IMS'], ['2026_04_29', 'IMS'], ['2026_05_05', 'IMS']]
dt = 0.5

#
# Load in data
#

# lon/lat, ice/snow, file locations, site names, etc
Ns = len(siteList)
date = {}
ice = {}
snow = {}
fileCast = {}
for i in range(Ns):
    ymd = siteList[i][0] # YYYY_MM_DD
    site = siteList[i][1] # Site name
    CTDmetaData = pd.read_excel(header + 'CTD_' + str(ymd[:4]) + '.xlsx')
    ift = np.where(CTDmetaData['Field Trip ID'] == community + '_' + ymd.replace('_', ''))[0][0] # field trip
    ns = int(CTDmetaData['Number of sites visited'][ift]) # times visited that trip
    js = np.where(CTDmetaData['Site name'][ift:ift+ns] == site)[0][0] + ift
    date[ymd] = datetime.toordinal(CTDmetaData['Date'][js].date()) + (CTDmetaData['Time (must be prior to taking the measurement)'][js].hour+(CTDmetaData['Time (must be prior to taking the measurement)'][js].minute+CTDmetaData['Time (must be prior to taking the measurement)'][js].second/60)/60)/24
    ice[ymd] = 0.01*CTDmetaData['Ice thickness (cm)'][js] # cm -> m
    snow[ymd] = 0.01*CTDmetaData['Snow thickness (cm)'][js] # cm -> m
    fileCast[ymd] = header + community + '/' + ymd + '/' + community + '_' + ymd.replace('_', '') + '_' + site.replace(' ','') + '_' + CTDmetaData['Preferred cast'][js].replace(' ','') + '.csv'

times = list(date.keys())

# # Load individual casts and store into one Dataset
ctd = pd.read_csv(fileCast[times[0]]).to_xarray() # Index 0 which files will be appended to
# Append all files into one pandas dataframe
for i in range(1, len(times)):
    ds = pd.read_csv(fileCast[times[i]]).to_xarray()
    ctd = xr.concat([ctd, ds],'date')

dates =  pd.to_datetime(times,format='%Y_%m_%d')
ctd['date'] = dates

#
# Add other variables
# 

# Pressure in the below needs to be sea pressure
# This is estimated to be 10.1285 dbar from the weather station in 2026

# Absolute Salinity 
SA = gsw.SA_from_SP(ctd['Salinity'], ctd['Pressure']-10.1285, lon=-59, lat=55)

# Conservative Temperature
CT = gsw.CT_from_t(SA, ctd['Temperature'], ctd['Pressure']-10.1285,)

# Conservative freezing temperature
T_freezing = gsw.CT_freezing(SA, ctd['Pressure']-10.1285, 0)

# Potential density (referenced to 0 dbar)
RHO = gsw.sigma0(SA, CT) + 1000.

# Oxygen saturation percent
O2sol = gsw.O2sol(SA, CT, ctd['Pressure']-10.1285, -59.671, 54.959)
DOsat = 100*ctd['Dissolved O2']/(O2sol*RHO*1e-3)

# Speed of sound
CS = gsw.sound_speed(SA, CT, ctd['Pressure']-10.1285)

# Rossby radius
N2, p_mid = gsw.Nsquared(SA, CT, ctd['Pressure']-10.1285, 54.959, axis=1) # Buoyancy frequency
z_mid = gsw.z_from_p(p_mid, 54.959)
# Rossby radius of deformation (1st baroclinic; see Chelton et al. 1998)
c1 = np.nan*np.zeros(z_mid.shape[0])
Ld = np.nan*np.zeros(z_mid.shape[0])
# Fix negative values of N2, following Chelton et al. (1998):
# - First smooth with a running average to take care of some +/- noise
# - Replace a negative value with the (pos) value at the next shallowest depth.
# - Replace neg values at the shallowest depth with 10e-8
N2_Ld = N2.copy()
for i in range(N2_Ld.shape[0]):
    N2_Ld[i,:] = IMS.runavg_ecj(N2_Ld[i,:], 7, mode='valid')
N2_Ld[np.isnan(N2_Ld)] = 0.
N2_Ld[np.isinf(N2_Ld)] = 0.
for i in range(N2_Ld.shape[0]):
    if N2_Ld[i,0] < 0:
        N2_Ld[i,0] = 1e-8
    for k in range(1,N2_Ld.shape[1]):
        if N2_Ld[i,k]<0:
            N2_Ld[i,k] = N2_Ld[i,k-1]
    # First baroclinic gravity wave speed [m/s]
    valid = ~np.isnan(z_mid[i,:])
    isort = np.flipud(np.argsort(z_mid[i,valid]))
    c1[i] = -np.trapz(np.sqrt(N2_Ld[i,valid][isort]), z_mid[i,valid][isort]) / np.pi
    # Rossby radius of deformation [m]
    Ld[i] = c1[i] / np.abs(gsw.f(54.959))
# Fix values with no data
c1[c1==0.] = np.nan
Ld[Ld==0.] = np.nan

# Ice and snow must be assigned as coordinates because they do not share the same index as the ocean vars
ctd = ctd.assign({"Absolute_Salinity":SA, "Conservative_Temperature":CT, "Freezing_Temperature":T_freezing, "Potential_Density":RHO, "Oxygen Saturation":DOsat, "Sound Speed": CS, "Hsnow":list(snow.values()), "Hice":list(ice.values()), "Ld":list(Ld)})

#
# Additional processing
#

# Smooth ECOPuck data with running average
L = 5 # Window size
for v in ['CDOM', 'Backscatter', 'Chlorophyll']:
    vartmp = np.nan*np.zeros(ctd[v].shape)
    for i in range(len(ctd.date)):
        vartmp[i,:] = IMS.runavg_ecj(ctd[v][i,:], L, 'valid')
    ctd[v] = (['date', 'index'], vartmp)

# Trim profiles
zTrimTop = 0.25 # Top, in metres - 0.25 m based on SIMBA comarison
zTrimBot = 0.5 # Bottom, in metres
d = ctd['Depth'] # depths
dmax = d.max('index') - zTrimBot 
ctd = ctd.where((d<dmax) & (d>zTrimTop), drop=True) 

# Save as nc file
nc = ctd.to_netcdf(pathroot + '/data/' + year + '/CTD_Profiles/CTD_IMS_SiteVisits.nc')

