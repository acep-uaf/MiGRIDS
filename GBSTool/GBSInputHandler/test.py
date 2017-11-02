# test implementation
# create a dataframe

from readAvecCsv import readAvecCsv
x_df = readAvecCsv('ChevakDispatch201612.csv','Chevak')
import matplotlib.pyplot as plt
plt.plot(x_df.DATE,x_df.Village_Load)

from convertDataframeToNetcdf import convertDataframeToNetcdf # import fuction
ncData = convertDataframeToNetcdf(x_df,'test.nc',['kW','kvar','kPA'])
print(ncData.variables)


# get children
children = soup.findChildren()  # get all children
for i in range(len(children)):
    name = children[i].name
    attributes = children[i].attrs
    grandkids = children[i].findChildren