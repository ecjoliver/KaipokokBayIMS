'''
    Load weekly Site Visit information generate a file with the qualitative observations
''' 

# Some globals
exec(open('../globals.py').read()) # modules, year, pathroot

# Load in Excel sheet of Site Visit (meta)data
df = pd.read_excel(pathroot + '/data/' + year + '/SiteVisits/SiteVisits_' + year + '_MetaData.xlsx', header=1)

# Create Markdown file with observations
f = open(pathroot + '/data/' + year + '/SiteVisits/SiteVisits_Weekly_Observations.md', 'w')
for i in range(len(df)):
    f.write('***' + df.Date[i].strftime('%d %B %Y') + '***  \r')
    if str(df['Weather when collected'][i]) != 'nan':
        f.write('**Weather:** ')
        f.write(df['Weather when collected'][i] + '  \r')
    if str(df['Ice/snow conditions'][i]) != 'nan':
        f.write('**Ice/snow conditions:** ')
        f.write(df['Ice/snow conditions'][i] + '  \r')
    if str(df['Observations (e.g. Facebook discussions)'][i]) != 'nan':
        f.write('**Observations:** ')
        f.write(df['Observations (e.g. Facebook discussions)'][i] + '  \r')
    if str(df['Field notes'][i]) != 'nan':
        f.write('**Field notes:** ')
        f.write(df['Field notes'][i] + '  \r')
    if str(df['Ice core notes'][i]) != 'nan':
        f.write('**Ice core notes:** ')
        f.write(df['Ice core notes'][i] + '  \r')
    if str(df['Data notes'][i]) != 'nan':
        f.write('**Data notes:** ')
        f.write(df['Data notes'][i] + '  \r')
    f.write('\r')
f.close()



