# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

import Powerhouse
import Windfarm
import Solarfarm
import ElectricalStorageSystem
import ThermalSystems
import Demand


class SystemOperations:
    # System Variables
    # Generation and dispatch resources
    powerhouse = Powerhouse()
    windfarm = Windfarm()
    solarfarm = Solarfarm()
    electricalStorageSystem = ElectricalStorageSystem()
    thermalSystems = ThermalSystems()
    demand = Demand()

    def __init__(self, systemConfigFile):



