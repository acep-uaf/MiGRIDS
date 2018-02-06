

# create instance
import os
import numpy as np
from ElectricalStorage import ElectricalEnergyStorage
from matplotlib import cm
eesID = 1
eesP = 0
eesQ = 0
eesSOC = 0.5
eesState = 0
eesSRC = 100
timeStep = 1
eesDescriptor = 'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\\test\InputData\Components\ees1Descriptor.xml'
Ees1 = ElectricalEnergyStorage(eesID, eesP, eesQ, eesSOC, eesState, eesSRC, timeStep, eesDescriptor)
Ees1.eesState = 2

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure()
ax = fig.gca(projection='3d')
X, Y = np.meshgrid(Ees1.eesLossMapE,Ees1.eesLossMapP)

# Plot the surface.
surf = ax.plot_surface(X, Y, Ees1.eesLossMapLoss, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)

print('done')

