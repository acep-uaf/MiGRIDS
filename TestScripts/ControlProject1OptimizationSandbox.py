'''
Tests the optimization algorithm on ControlProject1
'''

from GBSOptimizer.optimize import optimize

# Create optimization object
ctrlPrj1Optimize = optimize('ControlProject1', [])
print('Initialization complete.')

ctrlPrj1Optimize.doOptimization()

print(ctrlPrj1Optimize.fl)