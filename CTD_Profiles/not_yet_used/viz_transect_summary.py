'''
Code to plot a giant summary of all CTD transect variables for the data reports 
Created by MW, modified from EO
'''


from scipy import interpolate as interp


# Choose a site from CTD_to_nc.py

#
# Load in transect metadata and data
#
header = '~/OneDrive - Dalhousie University/Thesis/IMS/IMS_2024/git_code/CTD_transect/data_raw/'

# lon/lat, ice/snow, file locatins, site names, etc
Ns = len(siteList)
CTDmetaData = pd.read_excel(header + 'CTD_' + str(year) + '.xlsx')
lon = {}
lat = {}
ice = {}
snow = {}
fileCast = {}
for i in range(Ns):
    ymd = siteList[i][0] # YYYY_MM_DD
    site = siteList[i][1] # Site name
    ift = np.where(CTDmetaData['Field Trip ID'] == community + '_' + ymd.replace('_', ''))[0][0] # field trip
    ns = int(CTDmetaData['Number of sites visited'][ift]) # sites visited that trip
    js = np.where(CTDmetaData['Site name'][ift:ift+ns] == site)[0][0] + ift
    lon[site] = -1*CTDmetaData['Longitude'][js] # Saved as degrees W, here x -1 to make degrees E
    lat[site] = CTDmetaData['Latitude'][js] # degrees N
    ice[site] = 0.01*CTDmetaData['Ice thickness (cm)'][js] # cm -> m
    snow[site] = 0.01*CTDmetaData['Snow thickness (cm)'][js] # cm -> m
    fileCast[site] = header + community + '/' + ymd + '/' + community + '_' + ymd.replace('_', '') + '_' + site.replace(' ','') + '_' + CTDmetaData['Preferred cast'][js].replace(' ','') + '.csv'

sites = list(lon.keys())

# CTD profiles
# Time, Depth, Pressure, Conductivity, Salinity, Temperature, Backscatter, CDOM, Chlorophyll, Dissolved O2, Optode Temperature
ctd = {}
for i in range(len(sites)):
    ctd_pd = pd.read_csv(fileCast[sites[i]])
    ctd_dict = {}
    for key in ctd_pd.keys():
        ctd_dict[key] = np.array(ctd_pd[key])
    ctd[sites[i]] = ctd_dict

#
# Process CTD data and generate transects
#

# Trim profiles top and bottom
#ctd = snfCTD.trimProfiles(ctd, zTrimTop=1.25, zTrimBot=0.5)
ctd = snfCTD.trimProfiles(ctd, zTrimTop=1.0, zTrimBot=0.5)

# Smooth certain variables
ctd = snfCTD.smoothProfiles(ctd, L=5, fields=['CDOM', 'Backscatter', 'Chlorophyll'])

# Which sites/variables to leave out (hard coded)
skip = {}
for key in ctd[site].keys():
    skip[key] = {}
    for site in ctd.keys():
        skip[key][site] = False
if transect == 'udjutok-Deep Inlet (2022 May)':
    skip['Backscatter']['Site 3'] = True
    skip['CDOM']['Site 3'] = True
    skip['Chlorophyll']['Site 3'] = True
    skip['Dissolved O2']['Site 3'] = True
if transect == 'udjutok-Deep Inlet (2023 Feb)':
    skip['Salinity']['Site 9'] = True
    skip['Salinity']['Site 1'] = True
    skip['Dissolved O2']['Site 9'] = True
    skip['Dissolved O2']['Site 1'] = True
if transect == 'kaipokok Bay (2023 Apr)':
    skip['Salinity']['Beaver River Point'] = True
    skip['Salinity']['Rapids'] = True
    skip['Salinity']['Big Point'] = True
    skip['Dissolved O2']['Beaver River Point'] = True
    skip['Dissolved O2']['Rapids'] = True
    skip['Dissolved O2']['Big Point'] = True
if transect == 'Nain Bay-Strathcona Run (2022 May)':
    skip['Salinity']['Waypoint 19'] = True
    skip['Salinity']['Waypoint 20'] = True
    skip['Salinity']['Waypoint 21'] = True
    skip['Salinity']['Waypoint 22'] = True
    skip['Salinity']['Waypoint 23'] = True
    skip['Dissolved O2']['Waypoint 19'] = True
    skip['Dissolved O2']['Waypoint 20'] = True
    skip['Dissolved O2']['Waypoint 21'] = True
    skip['Dissolved O2']['Waypoint 22'] = True
    skip['Dissolved O2']['Waypoint 23'] = True
if transect == 'Webb Bay (2022 Sep)':
    skip['Backscatter']['WB0045'] = True
    skip['CDOM']['WB0045'] = True
    skip['Backscatter']['WB0046'] = True
    skip['CDOM']['WB0046'] = True
    skip['Backscatter']['WB0047'] = True
    skip['CDOM']['WB0047'] = True
    skip['Backscatter']['WB0048'] = True
    skip['CDOM']['WB0048'] = True
    skip['Backscatter']['WB050'] = True
    skip['CDOM']['WB050'] = True
    skip['Backscatter']['WB051'] = True
    skip['CDOM']['WB051'] = True
    skip['Dissolved O2']['WB051'] = True
    skip['Salinity']['WB051'] = True
    skip['Backscatter']['WB053'] = True
    skip['CDOM']['WB053'] = True
    skip['Dissolved O2']['WB053'] = True
    skip['Salinity']['WB053'] = True
    skip['Backscatter']['WB054'] = True
    skip['CDOM']['WB054'] = True
    skip['Dissolved O2']['WB054'] = True
    skip['Salinity']['WB054'] = True
if transect == 'kaipokok Bay (2024 Jan)':
    skip['Dissolved O2']['Pugaviks West'] = True

# Check for all-nans
sites_interp = {}
for key in ctd[site].keys():
    sites_interp[key] = []
for site in ctd.keys():
    for key in ctd[site].keys():
        if (np.sum(~np.isnan(ctd[site][key])) == 0) + skip[key][site]:
            ctd[site][key] = np.zeros(ctd[site][key].shape)
        else:
            sites_interp[key].append(site)

# Interpolate sections
dlon = 0.001
ctdS = {}
ddepth = {}
llon = {}
for key in ctd[site].keys():
    if key != 'Depth':
        ctdS[key], llon[key], ddepth[key] = snfCTD.interpSectionStitch(sites_interp[key], ctd, lon, key, dlon)

# Get ice and snowthickness arrays, ordered by increasing longitude
lon_array = np.array(list(lon.values())); isort = np.argsort(lon_array); lon_array = lon_array[isort]
lat_array = np.array(list(lat.values())); lat_array = lat_array[isort]
ice_array = np.array(list(ice.values())); ice_array = ice_array[isort]
snow_array = np.array(list(snow.values())); snow_array = snow_array[isort]

#
# Higher order analyses
#


# Absolute Salinity
p = gsw.p_from_z(-ddepth['Salinity'], np.mean(lat_array)) # pressure
SP = ctdS['Salinity'] # Practical Salinity
f = interp.NearestNDInterpolator(np.array([llon['Temperature'].flatten(), ddepth['Temperature'].flatten()]).T, ctdS['Temperature'].flatten()) # Assume temp/salt not shared grid, interp accordingly
T = f(llon['Salinity'], ddepth['Salinity']) # in situ Temperature
SA = gsw.SA_from_SP(SP, p, np.mean(lon_array), np.mean(lat_array)) # Absolute Salinity
# Freezing temperature
CT = gsw.CT_from_t(SA, T, p) # Conservative Temperature
CT_fr = gsw.CT_freezing(SA, p, 0.5) # # Freezing point temperature
# Potential density (referenced to 0 dbar)
RHO = gsw.sigma0(SA, CT) + 1000.
# N-squared
N2, p_mid = gsw.Nsquared(SA, CT, p, np.nanmean(lat_array))
z_mid = gsw.z_from_p(p_mid, np.mean(lat_array))
# Speed of sound
CS = gsw.sound_speed(SA, CT, p)


#### Plot parameters
D = 10.
bgcol = '0.5'

plt.figure(figsize=(16,20))
# Basics (temp, salt, density)
plt.clf()
w = 25;
pl = 2; pu = 98;
l1 = np.min(lon_array)
l2 = np.max(lon_array)
for key in llon.keys():
    if len(llon[key]) > 0:
        l1 = np.min([np.nanmin(llon[key]), l1])
        l2 = np.max([np.nanmax(llon[key]), l2])
# Ice and snow thickness
ax = plt.subplot2grid((15,w), (0,0), rowspan=1, colspan=w-1)
# plt.fill_between(lon_array, -1.*ice_array, 0., color='#B0C4DE') # EO ice
# plt.fill_between(lon_array, 0., snow_array, color='0.6') # EO snow

plt.fill_between(lon_array, 0., snow_array, color='lightgray') # Snow
plt.fill_between(lon_array, -1.*ice_array, 0., color='#d6fffa') # Ice

# Make water blue
plt.fill_between(lon_array, -1,-1.*ice_array, color='#214761')
plt.ylim([-0.6,0.3])

plt.legend(['Snow', 'Ice'], bbox_to_anchor=(1.09,1))
plt.plot(lon_array, -1.*ice_array, 'k-')
plt.plot(lon_array, 0.*ice_array, 'k-', linewidth=0.5)
plt.plot(lon_array, snow_array, 'k-')
plt.ylabel('Thickness [m]')
plt.xlim(l1, l2)
ax.set_xticklabels([])

site_labels = ['PP','SAN','HI','BRP','RAP','BP','PO','POW','GOU','WI','IMS','PUW','PU','AL','IG','CW','LN','GI','JP','CP']
for i,site in enumerate(sites_interp['Temperature']):
    # plt.plot(lon[site], 0. + 0.008*np.nanmax(ddepth['Temperature']), 'd', color='k', clip_on=False)
    ax.annotate(site_labels[i],(lon[site]-0.01,np.nanmax(snow_array)+0.2),size=12,rotation=45,annotation_clip=False)

# Title
# plt.title(transect, fontsize=16)
ax.set_title(transect,y=1.5,fontsize=16)
# Temperature (surface)
ax = plt.subplot2grid((15,w), (1,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Temperature'], -ddepth['Temperature'], ctdS['Temperature'], cmap=cmocean.cm.thermal)
plt.clim(np.nanpercentile(ctdS['Temperature'], pl), np.nanpercentile(ctdS['Temperature'], pu))
plt.xlim(l1, l2)
ax.set_xticklabels([])
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Temperature (deep)
ax = plt.subplot2grid((15,w), (2,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Temperature'], -ddepth['Temperature'], ctdS['Temperature'], cmap=cmocean.cm.thermal)
plt.clim(np.nanpercentile(ctdS['Temperature'], pl), np.nanpercentile(ctdS['Temperature'], pu))
plt.ylabel('Depth (m)')
plt.xlim(l1, l2)
ax.set_xticklabels([])
plt.ylim(-1.*np.nanmax(ddepth['Temperature']), -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((15,w), (1,w-1), rowspan=2, colspan=1)
# plt.colorbar(cax=cax, label='Temperature [deg. C]')
plt.colorbar(cax=cax, label=r'($^\circ$C)')


# Salinity (surface)
ax = plt.subplot2grid((15,w), (3,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Salinity'], -ddepth['Salinity'], ctdS['Salinity'], cmap=cmocean.cm.haline)
plt.clim(np.nanpercentile(ctdS['Salinity'], pl), np.nanpercentile(ctdS['Salinity'], pu))
plt.xlim(l1, l2)
ax.set_xticklabels([])
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Salinity (deep)
ax = plt.subplot2grid((15,w), (4,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Salinity'], -ddepth['Salinity'], ctdS['Salinity'], cmap=cmocean.cm.haline)
plt.clim(np.nanpercentile(ctdS['Salinity'], pl), np.nanpercentile(ctdS['Salinity'], pu))
plt.ylabel('Depth (m)')
plt.xlim(l1, l2)
ax.set_xticklabels([])
plt.ylim(-1.*np.nanmax(ddepth['Salinity']), -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((15,w), (3,w-1), rowspan=2, colspan=1)
# plt.colorbar(cax=cax, label='Salinity [PSU]')
plt.colorbar(cax=cax, label='(g/kg)')


# Density (surface)
ax = plt.subplot2grid((15,w), (5,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Salinity'], -ddepth['Salinity'], RHO, cmap=cmocean.cm.dense)
plt.clim(np.nanpercentile(np.abs(RHO), pl), np.nanpercentile(np.abs(RHO), pu))
plt.xlabel('Longitude (deg. E)')
plt.xlim(l1, l2)
# for site in sites_interp['Salinity']:
#     plt.plot(lon[site], 0. + 0.008*np.nanmax(ddepth['Salinity']), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Density (deep)
ax = plt.subplot2grid((15,w), (6,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Salinity'], -ddepth['Salinity'], RHO, cmap=cmocean.cm.dense)
plt.clim(np.nanpercentile(np.abs(RHO), pl), np.nanpercentile(np.abs(RHO), pu))
plt.ylabel('Depth (m)')
# ax.set_xticklabels([])
# plt.xlabel('Longitude (deg. E)')
plt.xlim(l1, l2)
plt.ylim(-1.*np.nanmax(ddepth['Salinity']), -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((15,w), (5,w-1), rowspan=2, colspan=1)
# plt.colorbar(cax=cax, label=r'Pot. density [kg/m$^3$]')
plt.colorbar(cax=cax, label=r'(kg/m$^3$)')

# Chlorophyll (surface)
ax = plt.subplot2grid((15,w), (7,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Chlorophyll'], -ddepth['Chlorophyll'], ctdS['Chlorophyll'], cmap=cmocean.cm.algae)
plt.clim(np.nanpercentile(ctdS['Chlorophyll'], pl), np.nanpercentile(ctdS['Chlorophyll'], pu))
plt.xlim(l1, l2)
ax.set_xticklabels([])
# for site in sites_interp['Chlorophyll']:
#     plt.plot(lon[site], 0. + 0.008*np.nanmax(ddepth['Chlorophyll']), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.)
# plt.title(transect) # Title
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Chlorophyll (deep)
ax = plt.subplot2grid((15,w), (8,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Chlorophyll'], -ddepth['Chlorophyll'], ctdS['Chlorophyll'], cmap=cmocean.cm.algae)
plt.clim(np.nanpercentile(ctdS['Chlorophyll'], pl), np.nanpercentile(ctdS['Chlorophyll'], pu))
plt.ylabel('z [m]')
plt.xlim(l1, l2)
ax.set_xticklabels([])
plt.ylim(-1.*np.nanmax(ddepth['Chlorophyll']), -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((15,w), (7,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label='Chlorophyll [μg/L]')

# CDOM (surface)
ax = plt.subplot2grid((15,w), (9,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['CDOM'], -ddepth['CDOM'], ctdS['CDOM'], cmap=cmocean.cm.matter)
plt.clim(np.nanpercentile(ctdS['CDOM'], pl), np.nanpercentile(ctdS['CDOM'], pu))
plt.xlim(l1, l2)
ax.set_xticklabels([])
# for site in sites_interp['CDOM']:
#     plt.plot(lon[site], 0. + 0.008*np.nanmax(ddepth['CDOM']), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# CDOM (deep)
ax = plt.subplot2grid((15,w), (10,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['CDOM'], -ddepth['CDOM'], ctdS['CDOM'], cmap=cmocean.cm.matter)
plt.clim(np.nanpercentile(ctdS['CDOM'], pl), np.nanpercentile(ctdS['CDOM'], pu))
plt.ylabel('Depth [m]')
plt.xlim(l1, l2)
ax.set_xticklabels([])
plt.ylim(-1.*np.nanmax(ddepth['CDOM']), -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((15,w), (9,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label='CDOM [ppb]')
# Backscatter (surface)
ax = plt.subplot2grid((15,w), (11,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Backscatter'], -ddepth['Backscatter'], ctdS['Backscatter'], cmap=cmocean.cm.turbid)
plt.clim(np.nanpercentile(ctdS['Backscatter'], pl), np.nanpercentile(ctdS['Backscatter'], pu))
plt.xlim(l1, l2)
ax.set_xticklabels([])
# for site in sites_interp['Backscatter']:
#     plt.plot(lon[site], 0. + 0.008*np.nanmax(ddepth['Backscatter']), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.) 
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Backscatter (deep)
ax = plt.subplot2grid((15,w), (12,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Backscatter'], -ddepth['Backscatter'], ctdS['Backscatter'], cmap=cmocean.cm.turbid)
plt.clim(np.nanpercentile(ctdS['Backscatter'], pl), np.nanpercentile(ctdS['Backscatter'], pu))
plt.ylabel('Depth [m]')
plt.xlim(l1, l2)
ax.set_xticklabels([])
plt.ylim(-1.*np.nanmax(ddepth['Backscatter']), -1.*D) 
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((15,w), (11,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label='Backscatter [m-1 sr-1]')
# Dissolved O2 (surface)
ax = plt.subplot2grid((15,w), (13,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Dissolved O2'], -ddepth['Dissolved O2'], ctdS['Dissolved O2'], cmap=cmocean.cm.oxy)
plt.clim(np.nanpercentile(ctdS['Dissolved O2'], pl), np.nanpercentile(ctdS['Dissolved O2'], pu))
plt.xlabel('Longitude (deg. E)')
plt.xlim(l1, l2)
# for site in sites_interp['Dissolved O2']:
#     plt.plot(lon[site], 0. + 0.008*np.nanmax(ddepth['Dissolved O2']), 'd', color='k', clip_on=False)
plt.ylim(-1.*D, 0.)
bbox1 = ax.get_position().get_points()
ax.spines['bottom'].set_visible(False)
# Dissolved O2 (deep)
ax = plt.subplot2grid((15,w), (14,0), rowspan=1, colspan=w-1, facecolor=bgcol)
plt.pcolormesh(llon['Dissolved O2'], -ddepth['Dissolved O2'], ctdS['Dissolved O2'], cmap=cmocean.cm.oxy)
plt.clim(np.nanpercentile(ctdS['Dissolved O2'], pl), np.nanpercentile(ctdS['Dissolved O2'], pu))
plt.ylabel('Depth [m]')
plt.xlabel('Longitude (deg. E)')
plt.xlim(l1, l2)
plt.ylim(-1.*np.nanmax(ddepth['Dissolved O2']), -1.*D)
bbox2 = ax.get_position().get_points()
bbox2[1][1] = bbox1[0][1] # put upper edge of lower plot flush with lower edge of upper plot
ax.set_position(mpl.transforms.Bbox.from_extents(bbox2.flatten()))
ax.spines['top'].set_visible(False)
cax = plt.subplot2grid((15,w), (13,w-1), rowspan=2, colspan=1)
plt.colorbar(cax=cax, label='Dissolved O2 [μmol/L]')



# Add vertical lines at site locations
for site in sites_interp['Salinity']:
    # plt.plot(lon[site], 0. + 0.008*np.nanmax(ddepth['Salinity']), 'd', color='k', clip_on=False)
    # Draw vertical line at each location
    ax.axvline(lon[site],ymin=0,ymax=14.88,c='k',linestyle='dotted',clip_on=False,zorder=3)
    # ax2.axvline(lon[site],ymin=-150,ymax=0,c='grey',linestyle='--',clip_on=False,zorder=0)



#
# cd ~/OneDrive - Dalhousie University/Thesis/IMS/IMS_2024/git_code/figures/CTD_transect/
plt.savefig(transect.replace(' ','_').replace('(','').replace(')','') + '_Transect_Summary.png', dpi=600, bbox_inches='tight')
#



