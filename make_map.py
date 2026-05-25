'''
    Make overview map of Kaipokok Bay and IMS
'''

import cartopy
import cartopy.crs as ccrs
from cartopy.io import shapereader
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib_scalebar.scalebar import ScaleBar
import os
import matplotlib as mpl
mpl.interactive(True)

# Some globals
exec(open('globals.py').read()) # year[transect], pathroot
pathroot = os.path.abspath('../../../') # Redefine pathroot

# Labrador coastline - HIGH RES
shp = shapereader.Reader(pathroot + '/data/GSHHS_Labrador/GSHHS_f_L1_Labrador')

# Load in Kaipokok Bay transect and IMS coordinates
df = pd.read_csv(pathroot + '/data/Coordinates/Kaipokok_Bay_Transect.csv')

# Short form of site names
site_labels= {'Pea Point': 'PP', 'Sandbar': 'SAN', 'Halfway Island': 'HI', 'Beaver River Point': 'BRP', 'Rapids': 'RAP', 'Big Point': 'BP', 'PostW': 'PO', 'Postville West': 'POW', 'Goulou': 'GOU', 'Woody Island': 'WI', 'IMS': 'IMS', 'Pugaviks West': 'PUW', 'Pugaviks': 'PUG', 'Alkamy': 'ALK', 'Iggiak': 'IGG', "Cape O'War": 'CW', 'Little Neck': 'LN', 'Ground Island': 'GI', 'Jackos Point': 'JP', 'Cape Point': 'CP', 'Punchin Island': 'PI', 'Black Island': 'BI'}

#
# Create map
#

fig = plt.figure(figsize=(6,8))
plt.clf()
ax = fig.add_subplot(1,1,1, projection=ccrs.Mercator()) # non-rotated projection

# Add high quality coastlines
for geometry in shp.geometries():
    ax.add_geometries([geometry], ccrs.PlateCarree(), facecolor='lightgray', edgecolor='lightgray', linewidth=0.5)

# Focus domain on Kaipokok Bay
lat1, lon1, lat2, lon2 = 54.72, -59.25, 55.25, -60
ax.set_extent([lon1, lon2, lat1, lat2], crs=ccrs.PlateCarree()) # Kaipokok Bay
ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=['left', 'bottom'], xlabel_style={'fontsize': 13}, ylabel_style={'fontsize': 13}, linewidth=0.01)

# Add CTD transect locations
ax.plot(df.Longitude, df.Latitude, 'o--', color='cornflowerblue', markersize=5, transform=ccrs.PlateCarree())
ax.plot(df[df.Site == 'IMS'].Longitude, df[df.Site == 'IMS'].Latitude, 'ko', markersize=8, transform=ccrs.PlateCarree())

# Add labels on sites
transform = ccrs.PlateCarree()._as_mpl_transform(ax)
for site in df.Site:
    if site == 'IMS':
        ax.annotate(site_labels[site], (df[df.Site == site].Longitude - 0.05, df[df.Site == site].Latitude + 0.025), color='k', size=12, xycoords=transform, ha='left', va='top')
    else:
        ax.annotate(site_labels[site], (df[df.Site == site].Longitude + 0.005, df[df.Site == site].Latitude - 0.005), color='0.25', size=10, xycoords=transform, ha='left', va='top')

# Add Scale Bar
ax.add_artist(ScaleBar(1, location='lower right'))

# plt.savefig('../figures/' + year + '/KaipokokBay_Map_IMSTransect.png', dpi=600, bbox_inches='tight')


