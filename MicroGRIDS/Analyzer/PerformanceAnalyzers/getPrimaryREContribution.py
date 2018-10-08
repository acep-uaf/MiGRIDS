# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: May 8, 2018
# License: MIT License (see LICENSE file of this package for more information)

def getPrimaryREContribution(time, firmLoadP, firmGenP, varGenP):
    '''
    Calculates the contribution of renewable generation (variable generation!) to the firm demand. Returns the fraction
    'Renewable kWh/Total Firm kWh' as an output.
    :param time: [Series] time vector in seconds
    :param firmLoadP: [Series] firm load real power vector in kWh
    :param firmGenP: [Series] firm generation (load following) real power vector in kWh
    :param varGenP: [Series] variable generation (non-load following) real power vector in kWh
    :return: renewableContribution: [float] fraction of renewable contribution to total firm demand.
    '''

    # First we need to figure out what of the variable generation actually contributed to meeting firm demand.
    # Demand not met by firmGenP
    remLoadP = firmLoadP - firmGenP

    # Account for the fact that there might (shouldn't have been other contributions)
    reP = varGenP.copy()
    reP[varGenP > remLoadP] = remLoadP[varGenP > remLoadP]

    # Get the kWh for the demand and RE contrib.
    firmLoadE = (firmLoadP*(time - time[0])/(60*60)).sum()
    reE = (reP*(time - time[0])/(60*60)).sum()

    # Get the load factor
    renewableContribution = reE/firmLoadE

    return renewableContribution