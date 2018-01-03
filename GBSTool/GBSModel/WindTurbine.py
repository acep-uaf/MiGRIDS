# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

# General imports
from bs4 import BeautifulSoup as Soup
from GBSAnalyzer.CurveAssemblers.wtgPowerCurveAssembler import WindPowerCurve


class WindTurbine:
    """
    Wind turbine class: stub

    :var:

    :method __init__: Constructor with additional instructions

    :returns:
    """

    def __init__(self, wtgID, wtgP, wtgQ, wtgDescriptor):
        """
        Constructor: stub

        :param wtgID:
        :param wtgP:
        :param wtgQ:
        :param wtgDescriptor:
        """
        # TODO: implement this

    def wtgDescriptorParser(self, wtgDescriptor):
        """
        wtgDescriptorParser: parses the necessary data from the wtgDescriptor.xml file provided.

        :param wtgDescriptor:
        :return:
        """

        # TODO: implement this