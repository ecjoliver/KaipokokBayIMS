'''
    Metadata for each transect
'''

#import numpy as np

#
# Transect definitions (field trip and site names)
#

# NOTE SITES NEED TO BE LISTED IN ORDER OF WEST TO EAST, COULD ADD CHECK TO RE-ORDER BASED ON LON VALUES

year = {}
community = {}
siteList = {}
xlims = {}
Dmax = {}
thicklims = {}
Tlims = {}
Slims = {}
Dlims = {}
N2lims = {}
CSlims = {}
FTlims = {}
Chlims = {}
CDlims = {}
BSlims = {}
DOlims = {}
OSlims = {}

# Kaipokok Bay
# Spring 2023
transect = 'Kaipokok Bay (2023 Apr)'
year[transect] = '2023'
community[transect] = 'Postville'
siteList[transect] = [['2023_04_21', 'Pea Point'], ['2023_04_21', 'Sandbar'], ['2023_04_21', 'Halfway Island'], ['2023_04_21', 'Beaver River Point'], ['2023_04_21', 'Rapids'], ['2023_04_21', 'Big Point'], ['2023_04_21', 'PostW'], ['2023_04_23', 'Postville West'], ['2023_04_23', 'Goulou'], ['2023_04_23', 'Woody Island'], ['2023_04_23', 'Pugaviks West'], ['2023_04_22', 'Pugaviks'], ['2023_04_23', 'Alkamy'], ['2023_04_22', 'Iggiak'], ['2023_04_22', "Cape O'War"], ['2023_04_22', 'Little Neck'], ['2023_04_22', 'Ground Island'], ['2023_04_22', 'Jackos Point'], ['2023_04_22', 'Cape Point'], ['2023_04_23', 'Punchin Island'], ['2023_04_22', 'Black Island']]
xlims[transect] = np.array([-59.932701, -59.35074])
Dmax[transect] = 120.
thicklims[transect] = np.array([-1.2, 0.5])
Tlims[transect] = [-1.75, -0.4]
Slims[transect] = [17, 32]
Dlims[transect] = [1014, 1026]
N2lims[transect] = [0, 0.02]
CSlims[transect] = [1420, 1440]
FTlims[transect] = [-1., 1.]
Chlims[transect] = [0, 1.5]
CDlims[transect] = [0, 12]
BSlims[transect] = [0.0005, 0.009]
DOlims[transect] = [370, 440]
OSlims[transect] = [85, 120]

# Kaipokok Bay
# Winter 2024
transect = 'Kaipokok Bay (2024 Jan)'
year[transect] = '2024'
community[transect] = 'Postville'
siteList[transect] = [['2024_01_26', 'Pea Point'], ['2024_01_26', 'Sandbar'], ['2024_01_26', 'Halfway Island'], ['2024_01_28', 'Beaver River Point'], ['2024_01_28', 'Rapids'], ['2024_01_25', 'Big Point'], ['2024_01_25', 'PostW'], ['2024_01_25', 'Postville West'], ['2024_01_25', 'Goulou'], ['2024_01_29', 'Woody Island'], ['2024_01_22', 'IMS'], ['2024_01_25', 'Pugaviks West'], ['2024_01_29', 'Pugaviks'], ['2024_01_29', 'Alkamy'], ['2024_01_29', 'Iggiak'], ['2024_01_30', "Cape O'War"], ['2024_01_30', 'Little Neck'], ['2024_01_30', 'Ground Island'], ['2024_01_30', 'Jackos Point'], ['2024_01_30', 'Cape Point']]
xlims[transect] = np.array([-59.932701, -59.35074])
Dmax[transect] = 120.
thicklims[transect] = np.array([-1.2, 0.5])
Tlims[transect] = [-1.75, -0.4]
Slims[transect] = [17, 32]
Dlims[transect] = [1014, 1026]
N2lims[transect] = [0, 0.02]
CSlims[transect] = [1420, 1440]
FTlims[transect] = [-1., 1.]
Chlims[transect] = [0, 1.5]
CDlims[transect] = [0, 12]
BSlims[transect] = [0.0005, 0.009]
DOlims[transect] = [370, 440]
OSlims[transect] = [85, 120]

# Kaipokok Bay
# Spring 2024
transect = 'Kaipokok Bay (2024 Apr)'
year[transect] = '2024'
community[transect] = 'Postville'
siteList[transect] = [['2024_04_18', 'Pea Point'], ['2024_04_18', 'Sandbar'], ['2024_04_18', 'Halfway Island'], ['2024_04_18', 'Beaver River Point'], ['2024_04_20', 'Rapids'], ['2024_04_15', 'Big Point'], ['2024_04_15', 'PostW'], ['2024_04_15', 'Postville West'], ['2024_04_18', 'Goulou'], ['2024_04_18', 'Woody Island'], ['2024_04_15', 'IMS'], ['2024_04_18', 'Pugaviks West'], ['2024_04_19', 'Pugaviks'], ['2024_04_19', 'Alkamy'], ['2024_04_19', 'Iggiak'], ['2024_04_19', "Cape O'War"], ['2024_04_19', 'Little Neck'], ['2024_04_19', 'Ground Island'], ['2024_04_19', 'Jackos Point'], ['2024_04_19', 'Cape Point'], ['2024_04_19', 'Punchin Island'], ['2024_04_19', 'Black Island']]
xlims[transect] = np.array([-59.932701, -59.35074])
Dmax[transect] = 120.
thicklims[transect] = np.array([-1.2, 0.5])
Tlims[transect] = [-1.75, -0.4]
Slims[transect] = [17, 32]
Dlims[transect] = [1014, 1026]
N2lims[transect] = [0, 0.02]
CSlims[transect] = [1420, 1440]
FTlims[transect] = [-1., 1.]
Chlims[transect] = [0, 1.5]
CDlims[transect] = [0, 12]
BSlims[transect] = [0.0005, 0.009]
DOlims[transect] = [370, 440]
OSlims[transect] = [85, 120]

# Kaipokok Bay
# Late Spring 2024
transect = 'Kaipokok Bay (2024 Jun)'
year[transect] = '2024'
community[transect] = 'Postville'
siteList[transect] = [['2024_06_24', 'Pea Point'], ['2024_06_24', 'Sandbar'], ['2024_06_24', 'Halfway Island'], ['2024_06_24', 'Beaver River Point'], ['2024_06_24', 'Rapids'], ['2024_06_24', 'Big Point'], ['2024_06_24', 'PostW'], ['2024_06_24', 'Postville West'], ['2024_06_24', 'Goulou'], ['2024_06_24', 'Woody Island'], ['2024_06_24', 'Pugaviks West'], ['2024_06_25', 'Pugaviks'], ['2024_06_25', 'Alkamy'], ['2024_06_25', 'Iggiak']]
xlims[transect] = np.array([-59.932701, -59.35074])
Dmax[transect] = 120.
thicklims[transect] = np.array([-1.2, 0.5])
Tlims[transect] = [-1.75, 10.]
Slims[transect] = [4, 32]
Dlims[transect] = [1012, 1026]
N2lims[transect] = [0, 0.02]
CSlims[transect] = [1440, 1465]
FTlims[transect] = [-10., 10.]
Chlims[transect] = [0, 1.5]
CDlims[transect] = [0, 12]
BSlims[transect] = [0.0005, 0.009]
DOlims[transect] = [320, 440]
OSlims[transect] = [85, 120]

# Kaipokok Bay
# Fall 2024 
transect = 'Kaipokok Bay (2024 Oct)'
year[transect] = '2024'
community[transect] = 'Postville'
siteList[transect] = [['2024_10_07', 'Pea Point'], ['2024_10_07', 'Sandbar'], ['2024_10_07', 'Halfway Island'], ['2024_10_07', 'Beaver River Point'], ['2024_10_07', 'Rapids'], ['2024_10_07', 'Big Point'], ['2024_10_07', 'PostW'], ['2024_10_07', 'Postville West'], ['2024_10_07', 'Goulou'], ['2024_10_07', 'Woody Island'], ['2024_10_07', 'Pugaviks West'], ['2024_10_07', 'Pugaviks'], ['2024_10_07', 'Alkamy'], ['2024_10_07', 'Iggiak'], ['2024_10_07', "Cape O'War"], ['2024_10_07', 'Little Neck'], ['2024_10_07', 'Ground Island'], ['2024_10_07', 'Jackos Point']]
xlims[transect] = np.array([-59.932701, -59.35074])
Dmax[transect] = 120.
thicklims[transect] = np.array([-1.2, 0.5])
Tlims[transect] = [-1.75, 10.]
Slims[transect] = [4, 32]
Dlims[transect] = [1012, 1026]
N2lims[transect] = [0, 0.02]
CSlims[transect] = [1440, 1465]
FTlims[transect] = [-10., 10.]
Chlims[transect] = [0, 1.5]
CDlims[transect] = [0, 12]
BSlims[transect] = [0.0005, 0.009]
DOlims[transect] = [320, 440]
OSlims[transect] = [85, 120]

# Kaipokok Bay
# Winter 2025
transect = 'Kaipokok Bay (2025 Feb)'
year[transect] = '2025'
community[transect] = 'Postville'
siteList[transect] = [['2025_02_10', 'Pea Point'], ['2025_02_10', 'Sandbar'], ['2025_02_10', 'Halfway Island'], ['2025_02_10', 'Beaver River Point'], ['2025_02_10', 'Rapids'], ['2025_02_11', 'Big Point'], ['2025_02_11', 'PostW'], ['2025_02_11', 'Postville West'], ['2025_02_11', 'Goulou'], ['2025_02_11', 'Woody Island'], ['2025_02_10', 'IMS'], ['2025_02_09', 'Pugaviks West'], ['2025_02_13', 'Pugaviks'], ['2025_02_13', 'Alkamy'], ['2025_02_13', 'Iggiak'], ['2025_02_13', "Cape O'War"], ['2025_02_13', 'Little Neck'], ['2025_02_13', 'Ground Island'], ['2025_02_13', 'Jackos Point'], ['2025_02_13', 'Cape Point']]
xlims[transect] = np.array([-59.932701, -59.35074])
Dmax[transect] = 120.
thicklims[transect] = np.array([-1.2, 0.5])
Tlims[transect] = [-1.75, -0.4]
Slims[transect] = [17, 32]
Dlims[transect] = [1014, 1026]
N2lims[transect] = [0, 0.02]
CSlims[transect] = [1420, 1440]
FTlims[transect] = [-1., 1.]
Chlims[transect] = [0, 1.5]
CDlims[transect] = [0, 12]
BSlims[transect] = [0.0005, 0.009]
DOlims[transect] = [370, 440]
OSlims[transect] = [85, 120]

# Kaipokok Bay
# Spring 2025
transect = 'Kaipokok Bay (2025 Apr)'
year[transect] = '2025'
community[transect] = 'Postville'
siteList[transect] = [['2025_04_10', 'Pea Point'], ['2025_04_10', 'Sandbar'], ['2025_04_10', 'Halfway Island'], ['2025_04_10', 'Beaver River Point'], ['2025_04_10', 'Rapids'], ['2025_04_10', 'Big Point'], ['2025_04_10', 'PostW'], ['2025_04_10', 'Postville West'], ['2025_04_10', 'Goulou'], ['2025_04_10', 'Woody Island'], ['2025_04_11', 'Pugaviks West'], ['2025_04_11', 'Pugaviks'], ['2025_04_11', 'Alkamy'], ['2025_04_11', 'Iggiak'], ['2025_04_11', "Cape O'War"], ['2025_04_11', 'Little Neck'], ['2025_04_11', 'Ground Island'], ['2025_04_11', 'Jackos Point'], ['2025_04_11', 'Cape Point'], ['2025_04_11', 'Punchin Island']]
xlims[transect] = np.array([-59.932701, -59.35074])
Dmax[transect] = 120.
thicklims[transect] = np.array([-1.2, 0.5])
Tlims[transect] = [-1.75, -0.4]
Slims[transect] = [17, 32]
Dlims[transect] = [1014, 1026]
N2lims[transect] = [0, 0.02]
CSlims[transect] = [1420, 1440]
FTlims[transect] = [-1., 1.]
Chlims[transect] = [0, 1.5]
CDlims[transect] = [0, 12]
BSlims[transect] = [0.0005, 0.009]
DOlims[transect] = [370, 440]
OSlims[transect] = [85, 120]

# Kaipokok Bay
# Late Spring 2025
transect = 'Kaipokok Bay (2025 Jun)'
year[transect] = '2025'
community[transect] = 'Postville'
siteList[transect] = [['2025_06_27', 'Pea Point'], ['2025_06_27', 'Sandbar'], ['2025_06_27', 'Halfway Island'], ['2025_06_27', 'Beaver River Point'], ['2025_06_27', 'Rapids'], ['2025_06_27', 'Big Point'], ['2025_06_27', 'PostW'], ['2025_06_27', 'Postville West'], ['2025_06_27', 'Goulou'], ['2025_06_27', 'Woody Island'], ['2025_06_27', 'IMS'], ['2025_06_27', 'Pugaviks West'], ['2025_06_27', 'Pugaviks'], ['2025_06_27', 'Alkamy'], ['2025_06_27', 'Iggiak']]
xlims[transect] = np.array([-59.932701, -59.35074])
Dmax[transect] = 120.
thicklims[transect] = np.array([-1.2, 0.5])
Tlims[transect] = [-1.75, 10.]
Slims[transect] = [4, 32]
Dlims[transect] = [1012, 1026]
N2lims[transect] = [0, 0.02]
CSlims[transect] = [1440, 1465]
FTlims[transect] = [-10., 10.]
Chlims[transect] = [0, 1.5]
CDlims[transect] = [0, 12]
BSlims[transect] = [0.0005, 0.009]
DOlims[transect] = [320, 440]
OSlims[transect] = [85, 120]

# Kaipokok Bay
# Fall 2025
transect = 'Kaipokok Bay (2025 Oct)'
year[transect] = '2025'
community[transect] = 'Postville'
siteList[transect] = [['2025_10_14', 'Pea Point'], ['2025_10_14', 'Sandbar'], ['2025_10_14', 'Halfway Island'], ['2025_10_14', 'Beaver River Point'], ['2025_10_14', 'Rapids'], ['2025_10_14', 'Big Point'], ['2025_10_14', 'PostW'], ['2025_10_14', 'Postville West'], ['2025_10_14', 'Goulou'], ['2025_10_14', 'Woody Island'], ['2025_10_14', 'IMS'], ['2025_10_14', 'Pugaviks West'], ['2025_10_14', 'Pugaviks'], ['2025_10_14', 'Alkamy'], ['2025_10_14', 'Iggiak'], ['2025_10_14', "Cape O'War"], ['2025_10_14', 'Little Neck'], ['2025_10_14', 'Ground Island'], ['2025_10_14', 'Jackos Point'],['2025_10_14', 'Cape Point'], ['2025_10_14', 'Punchin Island'], ['2025_10_14', 'Black Island']]
xlims[transect] = np.array([-59.932701, -59.35074])
Dmax[transect] = 120.
thicklims[transect] = np.array([-1.2, 0.5])
Tlims[transect] = [-1.75, 10.]
Slims[transect] = [4, 32]
Dlims[transect] = [1012, 1026]
N2lims[transect] = [0, 0.02]
CSlims[transect] = [1440, 1465]
FTlims[transect] = [-10., 10.]
Chlims[transect] = [0, 1.5]
CDlims[transect] = [0, 12]
BSlims[transect] = [0.0005, 0.009]
DOlims[transect] = [320, 440]
OSlims[transect] = [85, 120]

# Kaipokok Bay
# Winter 2026
transect = 'Kaipokok Bay (2026 Feb)'
year[transect] = '2026'
community[transect] = 'Postville'
siteList[transect] = [['2026_02_05', 'Pea Point'], ['2026_02_05', 'Sandbar'], ['2026_02_05', 'Halfway Island'], ['2026_02_05', 'Beaver River Point'], ['2026_02_05', 'Rapids'], ['2026_02_07', 'Big Point'], ['2026_02_07', 'PostW'], ['2026_02_06', 'Postville West'], ['2026_02_06', 'Goulou'], ['2026_02_06', 'Woody Island'], ['2026_02_02', 'IMS'], ['2026_02_06', 'Pugaviks West'], ['2026_02_06', 'Pugaviks'], ['2026_02_06', 'Alkamy'], ['2026_02_06', 'Iggiak'], ['2026_02_06', 'Little Neck'], ['2026_02_06', 'Jackos Point']]
xlims[transect] = np.array([-59.932701, -59.35074])
Dmax[transect] = 120.
thicklims[transect] = np.array([-1.2, 0.5])
Tlims[transect] = [-1.75, -0.4]
Slims[transect] = [17, 32]
Dlims[transect] = [1014, 1026]
N2lims[transect] = [0, 0.02]
CSlims[transect] = [1420, 1440]
FTlims[transect] = [-1., 1.]
Chlims[transect] = [0, 1.5]
CDlims[transect] = [0, 12]
BSlims[transect] = [0.0005, 0.009]
DOlims[transect] = [370, 440]
OSlims[transect] = [85, 120]

# Kaipokok Bay
# Spring 2026
transect = 'Kaipokok Bay (2026 Apr)'
year[transect] = '2026'
community[transect] = 'Postville'
siteList[transect] = [['2026_04_19', 'Pea Point'], ['2026_04_19', 'Sandbar'], ['2026_04_19', 'Halfway Island'], ['2026_04_19', 'Beaver River Point'], ['2026_04_19', 'Rapids'], ['2026_04_18', 'Big Point'], ['2026_04_18', 'PostW'], ['2026_04_18', 'Postville West'], ['2026_04_18', 'Goulou'], ['2026_04_18', 'Woody Island'], ['2026_04_16', 'IMS'], ['2026_04_21', 'Pugaviks West'], ['2026_04_21', 'Pugaviks'], ['2026_04_22', 'Alkamy'], ['2026_04_22', 'Iggiak'], ['2026_04_22', 'Little Neck'], ['2026_04_22', 'Jackos Point'], ['2026_04_22', 'Cape Point'], ['2026_04_22', 'Punchin Island'], ['2026_04_22', 'Black Island']]
xlims[transect] = np.array([-59.932701, -59.35074])
Dmax[transect] = 120.
thicklims[transect] = np.array([-1.2, 0.5])
Tlims[transect] = [-1.75, -0.4]
Slims[transect] = [17, 32]
Dlims[transect] = [1014, 1026]
N2lims[transect] = [0, 0.02]
CSlims[transect] = [1420, 1440]
FTlims[transect] = [-1., 1.]
Chlims[transect] = [0, 1.5]
CDlims[transect] = [0, 12]
BSlims[transect] = [0.0005, 0.009]
DOlims[transect] = [370, 440]
OSlims[transect] = [85, 120]

# Trout Net Point-Julie's Point (Kaipokok Bay)
# Winter 2025
transect = 'Trout-Julie (2025 Feb)'
year[transect] = '2025'
community[transect] = 'Postville'
siteList[transect] = [['2025_02_17', 'Trout-Julie 1'], ['2025_02_17', 'Trout-Julie 2'], ['2025_02_17', 'IMS'], ['2025_02_17', 'Trout-Julie 4'], ['2025_02_17', 'Trout-Julie 5']]
xlims[transect] = np.array([-59.689, -59.653])
Dmax[transect] = 80.
thicklims[transect] = np.array([-1.2, 0.5])
Tlims[transect] = [-1.75, -0.4]
Slims[transect] = [17, 32]
Dlims[transect] = [1014, 1026]
N2lims[transect] = [0, 0.02]
CSlims[transect] = [1420, 1440]
FTlims[transect] = [-1., 1.]
Chlims[transect] = [0, 1.5]
CDlims[transect] = [0, 12]
BSlims[transect] = [0.0005, 0.009]
DOlims[transect] = [370, 440]
OSlims[transect] = [85, 120]

# Spruce Point-Goulou Point (Kaipokok Bay)
# Winter 2025
transect = 'Spruce-Goulou (2025 Feb)'
year[transect] = '2025'
community[transect] = 'Postville'
siteList[transect] = [['2025_02_17', 'Spruce-Goulou 1'], ['2025_02_17', 'Spruce-Goulou 2'], ['2025_02_17', 'Spruce-Goulou 3'], ['2025_02_17', 'Spruce-Goulou 4'], ['2025_02_17', 'Spruce-Goulou 5']]
xlims[transect] = np.array([-59.737, -59.715])
Dmax[transect] = 50.
thicklims[transect] = np.array([-1.2, 0.5])
Tlims[transect] = [-1.75, -0.4]
Slims[transect] = [17, 32]
Dlims[transect] = [1014, 1026]
N2lims[transect] = [0, 0.02]
CSlims[transect] = [1420, 1440]
FTlims[transect] = [-1., 1.]
Chlims[transect] = [0, 1.5]
CDlims[transect] = [0, 12]
BSlims[transect] = [0.0005, 0.009]
DOlims[transect] = [370, 440]
OSlims[transect] = [85, 120]

###
### Special list
###

# Kaipokok Bay
# Spring 2023 - Up the bay
transect = 'Kaipokok Bay (2023 Apr) Up'
year[transect] = '2023'
community[transect] = 'Postville'
siteList[transect] = [['2023_04_21', 'Pea Point'], ['2023_04_21', 'Sandbar'], ['2023_04_21', 'Halfway Island'], ['2023_04_21', 'Beaver River Point'], ['2023_04_21', 'Rapids']]
xlims[transect] = np.array([-59.932701, -59.35074])
Dmax[transect] = 120.
thicklims[transect] = np.array([-1.2, 0.5])
Tlims[transect] = [-1.75, -0.4]
Slims[transect] = [17, 32]
Dlims[transect] = [1014, 1026]
N2lims[transect] = [0, 0.02]
CSlims[transect] = [1420, 1440]
FTlims[transect] = [-1., 1.]
Chlims[transect] = [0, 1.5]
CDlims[transect] = [0, 12]
BSlims[transect] = [0.0005, 0.009]
DOlims[transect] = [370, 440]
OSlims[transect] = [85, 120]

# Kaipokok Bay
# Spring 2023 - Out the bay
transect = 'Kaipokok Bay (2023 Apr) Out'
year[transect] = '2023'
community[transect] = 'Postville'
siteList[transect] = [['2023_04_21', 'Big Point'], ['2023_04_21', 'PostW'], ['2023_04_23', 'Postville West'], ['2023_04_23', 'Goulou'], ['2023_04_23', 'Woody Island'], ['2023_04_23', 'Pugaviks West'], ['2023_04_22', 'Pugaviks'], ['2023_04_23', 'Alkamy'], ['2023_04_22', 'Iggiak'], ['2023_04_22', "Cape O'War"], ['2023_04_22', 'Little Neck'], ['2023_04_22', 'Ground Island'], ['2023_04_22', 'Jackos Point'], ['2023_04_22', 'Cape Point'], ['2023_04_23', 'Punchin Island'], ['2023_04_22', 'Black Island']]
xlims[transect] = np.array([-59.932701, -59.35074])
Dmax[transect] = 120.
thicklims[transect] = np.array([-1.2, 0.5])
Tlims[transect] = [-1.75, -0.4]
Slims[transect] = [17, 32]
Dlims[transect] = [1014, 1026]
N2lims[transect] = [0, 0.02]
CSlims[transect] = [1420, 1440]
FTlims[transect] = [-1., 1.]
Chlims[transect] = [0, 1.5]
CDlims[transect] = [0, 12]
BSlims[transect] = [0.0005, 0.009]
DOlims[transect] = [370, 440]
OSlims[transect] = [85, 120]

# Kaipokok Bay
# Winter 2024 - Up the Bay
transect = 'Kaipokok Bay (2024 Jan) Up'
year[transect] = '2024'
community[transect] = 'Postville'
siteList[transect] = [['2024_01_26', 'Pea Point'], ['2024_01_26', 'Sandbar'], ['2024_01_26', 'Halfway Island'], ['2024_01_28', 'Beaver River Point'], ['2024_01_28', 'Rapids']]
xlims[transect] = np.array([-59.932701, -59.35074])
Dmax[transect] = 120.
thicklims[transect] = np.array([-1.2, 0.5])
Tlims[transect] = [-1.75, -0.4]
Slims[transect] = [17, 32]
Dlims[transect] = [1014, 1026]
N2lims[transect] = [0, 0.02]
CSlims[transect] = [1420, 1440]
FTlims[transect] = [-1., 1.]
Chlims[transect] = [0, 1.5]
CDlims[transect] = [0, 12]
BSlims[transect] = [0.0005, 0.009]
DOlims[transect] = [370, 440]
OSlims[transect] = [85, 120]

# Kaipokok Bay
# Winter 2024 - Out the Bay
transect = 'Kaipokok Bay (2024 Jan) Out'
year[transect] = '2024'
community[transect] = 'Postville'
siteList[transect] = [['2024_01_25', 'Big Point'], ['2024_01_25', 'PostW'], ['2024_01_25', 'Postville West'], ['2024_01_25', 'Goulou'], ['2024_01_29', 'Woody Island'], ['2024_01_22', 'IMS'], ['2024_01_25', 'Pugaviks West'], ['2024_01_29', 'Pugaviks'], ['2024_01_29', 'Alkamy'], ['2024_01_29', 'Iggiak'], ['2024_01_30', "Cape O'War"], ['2024_01_30', 'Little Neck'], ['2024_01_30', 'Ground Island'], ['2024_01_30', 'Jackos Point'], ['2024_01_30', 'Cape Point']]
xlims[transect] = np.array([-59.932701, -59.35074])
Dmax[transect] = 120.
thicklims[transect] = np.array([-1.2, 0.5])
Tlims[transect] = [-1.75, -0.4]
Slims[transect] = [17, 32]
Dlims[transect] = [1014, 1026]
N2lims[transect] = [0, 0.02]
CSlims[transect] = [1420, 1440]
FTlims[transect] = [-1., 1.]
Chlims[transect] = [0, 1.5]
CDlims[transect] = [0, 12]
BSlims[transect] = [0.0005, 0.009]
DOlims[transect] = [370, 440]
OSlims[transect] = [85, 120]

# Kaipokok Bay
# Spring 2024 - Up the Bay
transect = 'Kaipokok Bay (2024 Apr) Up'
year[transect] = '2024'
community[transect] = 'Postville'
siteList[transect] = [['2024_04_18', 'Pea Point'], ['2024_04_18', 'Sandbar'], ['2024_04_18', 'Halfway Island'], ['2024_04_18', 'Beaver River Point'], ['2024_04_20', 'Rapids']]
xlims[transect] = np.array([-59.932701, -59.35074])
Dmax[transect] = 120.
thicklims[transect] = np.array([-1.2, 0.5])
Tlims[transect] = [-1.75, -0.4]
Slims[transect] = [17, 32]
Dlims[transect] = [1014, 1026]
N2lims[transect] = [0, 0.02]
CSlims[transect] = [1420, 1440]
FTlims[transect] = [-1., 1.]
Chlims[transect] = [0, 1.5]
CDlims[transect] = [0, 12]
BSlims[transect] = [0.0005, 0.009]
DOlims[transect] = [370, 440]
OSlims[transect] = [85, 120]

# Kaipokok Bay
# Spring 2024 - Out the bay
transect = 'Kaipokok Bay (2024 Apr) Out'
year[transect] = '2024'
community[transect] = 'Postville'
siteList[transect] = [['2024_04_15', 'Big Point'], ['2024_04_15', 'PostW'], ['2024_04_15', 'Postville West'], ['2024_04_18', 'Goulou'], ['2024_04_18', 'Woody Island'], ['2024_04_15', 'IMS'], ['2024_04_18', 'Pugaviks West'], ['2024_04_19', 'Pugaviks'], ['2024_04_19', 'Alkamy'], ['2024_04_19', 'Iggiak'], ['2024_04_19', "Cape O'War"], ['2024_04_19', 'Little Neck'], ['2024_04_19', 'Ground Island'], ['2024_04_19', 'Jackos Point'], ['2024_04_19', 'Cape Point'], ['2024_04_19', 'Punchin Island'], ['2024_04_19', 'Black Island']]
xlims[transect] = np.array([-59.932701, -59.35074])
Dmax[transect] = 120.
thicklims[transect] = np.array([-1.2, 0.5])
Tlims[transect] = [-1.75, -0.4]
Slims[transect] = [17, 32]
Dlims[transect] = [1014, 1026]
N2lims[transect] = [0, 0.02]
CSlims[transect] = [1420, 1440]
FTlims[transect] = [-1., 1.]
Chlims[transect] = [0, 1.5]
CDlims[transect] = [0, 12]
BSlims[transect] = [0.0005, 0.009]
DOlims[transect] = [370, 440]
OSlims[transect] = [85, 120]

# Full transect list
transects = year.keys()
