# test implementation
# create a dataframe

from readAvecCsv import readAvecCsv
x_df = readAvecCsv('ChevakDispatch201612.csv' ,'')
import matplotlib.pyplot as plt
plt.plot(x_df.DATE,x_df.Village_Load)

from dataframe2netcdf import dataframe2netcdf # import fuction
ncData = dataframe2netcdf(x_df,'test.nc',['kW','kvar','kPA'])
print(ncData.variables)


# get children
children = soup.findChildren()  # get all children
for i in range(len(children)):
    name = children[i].name
    attributes = children[i].attrs
    grandkids = children[i].findChildren