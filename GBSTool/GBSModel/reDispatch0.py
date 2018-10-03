# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu, Alaska Center for Energy and Power
# Date: July 13, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
import numpy as np

# this object dispatches units with a rule based system. Power setpoints to the wind turbine react slowly to the loading
# on the thermal energy storage system. The TES reacts quickly the the amount of wind power that can be accepted into the
# grid. This requires a TES to be part of the system.
class reDispatch:
    def __init__(self, args):
        self.wfPset = 0 # initiate the power output of the wind farm to zero
        self.wfPsetResponseRampRate = args['wfPsetResponseRampRate']
        self.tessPset = args['tessPset']

    # FUTUREFEATURE: replace windfarm (wf) setpoints with a list of windturbine setpoints.
    def reDispatch(self, SO):
        """
        This dispatches the renewable energy in the grid.
        :param OS: pass the instance of the SystemOperations being run
        :param P: the current load
        :param wfPset: the power setpoints for each wind turbine
        """
        P = SO.P # current demand
        # wind turbine output is the min of available and setpoint
        # get available wind power
        wfPAvail = sum(SO.WF.wtgPAvail)
        # this is the actual output of the wind turbine
        self.wfP = min(wfPAvail,self.wfPset)
        # dispach the wf
        SO.WF.runWtgDispatch(self.wfP,0, SO.masterIdx)

        # the amount used to supply the load is the min of the max allowed and the output
        # the maximum amount of power that can be imported from renewable resources
        self.rePlimit = max([P - sum(SO.PH.genMolAvail), 0])
        # amount of imported wind power
        self.wfPimport = min(self.rePlimit, self.wfP)

        # charge the EESS with whatever is leftover, as much as possible.
        # amount of wind power used to charge the eess is the minimum of maximum charging power and the difference
        # between available wind power and wind power imported to the grid.
        self.wfPch = min(sum(SO.EESS.eesPinAvail), self.wfP - self.wfPimport)

        # Any leftover needs to be dumped into the TES, up to maximum power
        self.wfPtess = min(SO.TESS.tesPInMax, self.wfP-self.wfPimport-self.wfPch)
        # FUTUREFEATURE: replace this with a proper calc
        SO.TESS.runTesDispatch(self.wfPtess)


        # if the tess is being charged differently than the setpoint, increment timer. If reaches point, start ramping down wind power
        # the difference between loading and the setpoint for each tes in the tess
        tessLoadingDifference = self.wfPtess - SO.TESS.tesPInMax * self.tessPset
        # calculate the change in wtg setpoint
        # kW * kW/(kW*s) * s/step = kW/step. For example, 10 kW difference * 0.25 kW/(kW*s) response rate * 1 s per step
        # gives 2.5 kW change per step. If 10s per time step, then the rate would 25 kW change per step. This would overshoot
        # thus there needs to be a check that stops from overshooting for simulations with long time steps.
        wfPchange = min([tessLoadingDifference*self.wfPsetResponseRampRate*SO.timeStep, tessLoadingDifference], key=abs)
        self.wfPset = max(min(self.wfPset - wfPchange, wfPAvail),0)





