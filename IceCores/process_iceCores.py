'''
    Load Kaipokok Bay ice cores and generate a file from the data
''' 

# Some globals
exec(open('../globals.py').read()) # modules, year, pathroot

# Load in Excel sheet of Site Visit (meta)data
xls = pd.ExcelFile(pathroot + '/data/' + year + '/IceCores/IceSalinity_' + year + '.xlsx')
sheets = xls.sheet_names

# Loop over each sheet (= site + date)
site0 = {}
date_collected0 = {}
date_measured0 = {}
L0 = {} # Core length (cm)
S0 = {} # Salinity (ppt)
C0 = {} # Conductivity (uS/cm)
T0 = {} # Temperature when measured (degC)
for sheet in sheets:
    df = pd.read_excel(pathroot + '/data/' + year + '/IceCores/IceSalinity_' + year + '.xlsx', sheet_name=sheet, header=None)
    # Load in site name and dates (collected, measured)
    site0[sheet] = df[1][2]
    date_collected0[sheet] = df[1][0]
    date_measured0[sheet] = df[1][1]
    # Load in core length
    L0[sheet] = np.array([df[4][4], df[4][12], df[4][20]])
    # Load in salinities
    S0[sheet] = np.zeros((7,3))
    S0[sheet][:,0] = df[1][5:11+1].values
    S0[sheet][:,1] = df[1][13:19+1].values
    S0[sheet][:,2] = df[1][21:27+1].values
    # Load in conductivities
    C0[sheet] = np.zeros((7,3))
    C0[sheet][:,0] = df[2][5:11+1].values
    C0[sheet][:,1] = df[2][13:19+1].values
    C0[sheet][:,2] = df[2][21:27+1].values
    # Load in temperatures
    T0[sheet] = np.zeros((7,3))
    T0[sheet][:,0] = df[3][5:11+1].values
    T0[sheet][:,1] = df[3][13:19+1].values
    T0[sheet][:,2] = df[3][21:27+1].values

# Generate more useful data form
Nc = 3 # Number of cores
sites = list(np.unique(list(site0.values())))
zb = {} # Vertical coordinate of segments (bounds)
z = {} # Vertical coordinate of segments (mid-points)
L = {}
N = {} # Number of segments (per core)
S = {}
C = {}
T = {}
for site in sites:
    L[site] = {}
    N[site] = {}
    zb[site] = {}
    z[site] = {}
    S[site] = {}
    C[site] = {}
    T[site] = {}
for sheet in sheets:
    site = site0[sheet]
    date = date_collected0[sheet]
    L[site][date] = L0[sheet] # Core length
    N[site][date] = np.zeros(3) # Number of segments
    # z coordinate of cores
    zb[site][date] = {}
    z[site][date] = {}
    for ic in range(len(L[site][date])):
        N[site][date][ic] = np.sum(~np.isnan(S0[sheet][:,ic])) # Number of segments
        NL = np.floor(L[site][date][ic]/10.) # Number of WHOLE 10 cm sections given core length
        # Calculate z coordinate bounds on segments
        #if NL < N[site][date][ic]: # Case A: Last segment is partial (<10 cm)
        #    zb[site][date][ic] = np.append(10*np.arange(N[site][date][ic]), L[site][date][ic])
        #elif NL == N[site][date][ic]: # Case B: Last segment is expanded (>10 cm)
        #    zb[site][date][ic] = np.append(10*np.arange(N[site][date][ic]), L[site][date][ic])
        #elif NL > N[site][date][ic]: # Case C: Core longer than 70 cm, last segment is expanded (>10 cm)
        #    zb[site][date][ic] = np.append(10*np.arange(N[site][date][ic]), L[site][date][ic])
        zb[site][date][ic] = np.append(10*np.arange(N[site][date][ic]), L[site][date][ic])
        # Calculate z coordinate (segment mid-points)
        z[site][date][ic] = zb[site][date][ic][:-1] + 0.5*np.diff(zb[site][date][ic])
    # Salinity, Conductivity, Temperature of each core
    S[site][date] = {}
    C[site][date] = {}
    T[site][date] = {}
    for ic in range(len(L[site][date])):
        S[site][date][ic] = S0[sheet][:int(N[site][date][ic]),ic]
        C[site][date][ic] = C0[sheet][:int(N[site][date][ic]),ic]
        T[site][date][ic] = T0[sheet][:int(N[site][date][ic]),ic]

# Convert z and zb from cm to m
for site in sites:
    for date in z[site].keys():
        for ic in range(Nc):
            zb[site][date][ic] /= 100.
            z[site][date][ic] /= 100.

#
# Calculate practical and absolute salinity using GSW package
#

SP = {}
SA = {}
for site in sites:
    SP[site] = {}
    SA[site] = {}
    for date in z[site].keys():
        SP[site][date] = {}
        SA[site][date] = {}
        for ic in range(Nc):
            SP[site][date][ic] = gsw.SP_from_C(1e-3*C[site][date][ic], T[site][date][ic], 0.)
            SA[site][date][ic] = gsw.SA_from_SP(SP[site][date][ic], 0., -59.671, 54.959)

#
# Plot up the data
#

cols = ['k', 'b', 'g']

# Salinity
plt.figure(figsize=(7,15), facecolor='w')
plt.clf()
cnt = 1
for site in S.keys():
    for date in S[site].keys():
        plt.subplot(3,2,cnt)
        for ic in range(3):
            #plt.plot(S[site][date][ic], z[site][date][ic], '-', color=cols[ic], alpha=0.25)
            plt.plot(S[site][date][ic], z[site][date][ic], '.', color=cols[ic])
            plt.step(S[site][date][ic], zb[site][date][ic][:-1], color=cols[ic])
            plt.step(S[site][date][ic], zb[site][date][ic][1:], where='post', color=cols[ic])
        if cnt >= 5:
            plt.xlabel('Salinity (ppt)')
        if np.mod(cnt,2) == 1:
            plt.ylabel('z (m)')
        plt.title(site + ' ' + str(date)[:10])
        cnt += 1
plt.tight_layout()

plt.savefig(pathroot + '/figures/' + year + '/IceCores/IceCores_SalinityYSI.png', dpi=600, bbox_inches='tight')

# Temperature
plt.figure(figsize=(7,15), facecolor='w')
plt.clf()
cnt = 1
for site in S.keys():
    for date in S[site].keys():
        plt.subplot(3,2,cnt)
        for ic in range(3):
            plt.plot(T[site][date][ic], z[site][date][ic], '.', color=cols[ic])
            plt.step(T[site][date][ic], zb[site][date][ic][:-1], color=cols[ic])
            plt.step(T[site][date][ic], zb[site][date][ic][1:], where='post', color=cols[ic])
        if cnt >= 5:
            plt.xlabel(r'Temperature ($^\circ$C)')
        if np.mod(cnt,2) == 1:
            plt.ylabel('z (m)')
        plt.title(site + ' ' + str(date)[:10])
        cnt += 1
plt.tight_layout()

plt.savefig(pathroot + '/figures/' + year + '/IceCores/IceCores_Temperature.png', dpi=600, bbox_inches='tight')

# Conductivity
plt.figure(figsize=(7,15), facecolor='w')
plt.clf()
cnt = 1
for site in S.keys():
    for date in S[site].keys():
        plt.subplot(3,2,cnt)
        for ic in range(3):
            plt.plot(C[site][date][ic], z[site][date][ic], '.', color=cols[ic])
            plt.step(C[site][date][ic], zb[site][date][ic][:-1], color=cols[ic])
            plt.step(C[site][date][ic], zb[site][date][ic][1:], where='post', color=cols[ic])
        if cnt >= 5:
            plt.xlabel(r'Conductivity ($\mu$S/cm)')
        if np.mod(cnt,2) == 1:
            plt.ylabel('z (m)')
        plt.title(site + ' ' + str(date)[:10])
        cnt += 1
plt.tight_layout()

plt.savefig(pathroot + '/figures/' + year + '/IceCores/IceCores_Conductivity.png', dpi=600, bbox_inches='tight')

# Practical Salinity
plt.figure(figsize=(7,15), facecolor='w')
plt.clf()
cnt = 1
for site in S.keys():
    for date in S[site].keys():
        plt.subplot(3,2,cnt)
        for ic in range(3):
            #plt.plot(S[site][date][ic], z[site][date][ic], '-', color=cols[ic], alpha=0.25)
            plt.plot(SP[site][date][ic], z[site][date][ic], '.', color=cols[ic])
            plt.step(SP[site][date][ic], zb[site][date][ic][:-1], color=cols[ic])
            plt.step(SP[site][date][ic], zb[site][date][ic][1:], where='post', color=cols[ic])
        if cnt >= 5:
            plt.xlabel('Practical Salinity (PSU)')
        if np.mod(cnt,2) == 1:
            plt.ylabel('z (m)')
        plt.title(site + ' ' + str(date)[:10])
        cnt += 1
plt.tight_layout()

plt.savefig(pathroot + '/figures/' + year + '/IceCores/IceCores_SalinityPractical.png', dpi=600, bbox_inches='tight')

# Absolute Salinity
plt.figure(figsize=(7,15), facecolor='w')
plt.clf()
cnt = 1
for site in S.keys():
    for date in S[site].keys():
        plt.subplot(3,2,cnt)
        for ic in range(3):
            #plt.plot(S[site][date][ic], z[site][date][ic], '-', color=cols[ic], alpha=0.25)
            plt.plot(SA[site][date][ic], z[site][date][ic], '.', color=cols[ic])
            plt.step(SA[site][date][ic], zb[site][date][ic][:-1], color=cols[ic])
            plt.step(SA[site][date][ic], zb[site][date][ic][1:], where='post', color=cols[ic])
        if cnt >= 5:
            plt.xlabel('Absolute Salinity (g/kg)')
        if np.mod(cnt,2) == 1:
            plt.ylabel('z (m)')
        plt.title(site + ' ' + str(date)[:10])
        cnt += 1
plt.tight_layout()

plt.savefig(pathroot + '/figures/' + year + '/IceCores/IceCores_SalinityAbsolute.png', dpi=600, bbox_inches='tight')

# Salinity differences
plt.figure(figsize=(7,15), facecolor='w')
plt.clf()
cnt = 1
for site in S.keys():
    for date in S[site].keys():
        plt.subplot(3,2,cnt)
        for ic in range(3):
            plt.plot(SP[site][date][ic] - S[site][date][ic], z[site][date][ic], '.', color=cols[ic])
            plt.step(SP[site][date][ic] - S[site][date][ic], zb[site][date][ic][:-1], color=cols[ic])
            plt.step(SP[site][date][ic] - S[site][date][ic], zb[site][date][ic][1:], where='post', color=cols[ic])
        if cnt >= 5:
            plt.xlabel('Practical Salinity - Salinity')
        if np.mod(cnt,2) == 1:
            plt.ylabel('z (m)')
        plt.title(site + ' ' + str(date)[:10])
        cnt += 1
plt.tight_layout()

plt.savefig(pathroot + '/figures/' + year + '/IceCores/IceCores_SalinityPracticalMinusYSI.png', dpi=600, bbox_inches='tight')

plt.figure(figsize=(7,15), facecolor='w')
plt.clf()
cnt = 1     
for site in S.keys():
    for date in S[site].keys():
        plt.subplot(3,2,cnt)
        for ic in range(3):
            plt.plot(SA[site][date][ic] - S[site][date][ic], z[site][date][ic], '.', color=cols[ic])
            plt.step(SA[site][date][ic] - S[site][date][ic], zb[site][date][ic][:-1], color=cols[ic])
            plt.step(SA[site][date][ic] - S[site][date][ic], zb[site][date][ic][1:], where='post', color=cols[ic])
        if cnt >= 5:
            plt.xlabel('Absolute Salinity - Salinity')
        if np.mod(cnt,2) == 1:
            plt.ylabel('z (m)')
        plt.title(site + ' ' + str(date)[:10])
        cnt += 1
plt.tight_layout()

plt.savefig(pathroot + '/figures/' + year + '/IceCores/IceCores_SalinityAbsolute-YSI.png', dpi=600, bbox_inches='tight')

