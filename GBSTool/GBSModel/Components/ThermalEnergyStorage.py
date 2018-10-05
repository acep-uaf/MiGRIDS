# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Jeremy VanderMeer, jbvandermeer@alaska.edu, Alaska Center for Energy and Power
# Date: June 15, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
from bs4 import BeautifulSoup as Soup

class ThermalEnergyStorage:
    # Constructor
    def __init__(self, tesID, tesT, tesState, timeStep, tesDescriptor):

        # write initial values to internal variables
        self.tesID = tesID  # internal id used in Powerhouse for tracking generator objects. *type int*
        self.tesT = tesT  # Current state of charge in pu
        self.tesState = tesState  # Generator operating state [dimensionless, index]. See docs for key.
        self.timeStep = timeStep  # the time step used in the simulation in seconds

        # run the descriptor parser file to grab information from the descriptor file for this unit
        self.tesDescriptorParser(tesDescriptor)

        # these values will be set when checkOperatingConditions is run
        self.tesP = 0
        self.tesQ = 0
        self.tesPinAvail = 0
        self.tesPoutAvail = 0
        self.outOfBounds = 0
        self.tesPloss = 0
        self.checkOperatingConditions()

    # energy storage descriptor parser
    def tesDescriptorParser(self, tesDescriptor):
        """
        Reads the data from a given tesDescriptor file and uses the information given to populate the
        respective internal variables.

        :param tesDescriptor: relative path and file name of tesDescriptor.xml-file that is used to populate static
        information

        :return:
        """
        # read xml file
        tesDescriptorFile = open(tesDescriptor, "r")
        tesDescriptorXml = tesDescriptorFile.read()
        tesDescriptorFile.close()
        tesSoup = Soup(tesDescriptorXml, "xml")

        # Dig through the tree for the required data
        self.tesName = tesSoup.component.get('name')
        self.tesPOutMax = float(tesSoup.POutMaxPa.get('value'))  # max discharging power
        self.tesPInMax = float(tesSoup.PInMaxPa.get('value'))  # max charging power
        self.tesEMax = float(
            tesSoup.ratedDuration.get('value')) * self.tesPInMax  # the maximum energy capacity of the EES in kWs
        self.thermalCapacity = float(tesSoup.thermalCapacity.get('value'))  # thermalCapacity
        self.thermalConductanceInsulation = float(tesSoup.thermalConductanceInsulation.get('value'))  # thermalConductanceInsulation
        self.thermalConductanceExchanger = float(tesSoup.thermalConductanceExchanger.get('value'))  # thermalConductanceExchanger
        self.conversionEfficiency = float(tesSoup.conversionEfficiency.get('value'))  # conversionEfficiency
        self.ambientTemperature = float(tesSoup.ambientTemperature.get('value'))  # ambientTemperature
        self.thermalCapacity = float(tesSoup.thermalCapacity.get('value'))  # thermalCapacity
        # check if EMax is zero, this is likely because it is a zero EES condition. Set it to 1 kWs in order not to crash the
        # SOC calculations
        if self.tesEMax == 0:
            self.tesEMax = 1
        # 'essChargeRate' is the fraction of power that it would take to fully charge or discharge the ESS that is the
        # maximum charge or discharge power. This creates charging and discharging curves that exponentially approach full
        # and zero charge.
        self.tesChargeRate = float(tesSoup.chargeRate.get('value'))
        self.setPointResponseRampRate = float(tesSoup.setPointResponseRampRate.get('value'))
        self.setPoint = float(tesSoup.setPoint.get('value'))


    def checkOperatingConditions(self):
        """
        Checks if the tes is operating within defined bounds. Otherwise, triggers the respective (cummulative
            energy) timers.

        :return:
        """
        if self.tesState == 2:  # if running online
            self.tesPinAvail = self.tesPInMax
            # check to make sure the current power output or input is not greater than the maximum allowed.
            if self.tesP > self.tesPinAvail:
                self.outOfBounds = True
            else:
                self.outOfBounds = False

        elif self.tesState == 1:  # if starting up
            self.tesPinAvail = 0  # not available to produce power yet
            self.outOfBounds = False
        else:  # if off
            # no power available and reset counters
            self.tesPinAvail = 0  # not available to produce power yet
            self.outOfBounds = False