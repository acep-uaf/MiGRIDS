#String, SetupInformation -> None
#edits the ModelSetupInformation object to contain parameters in the setup.xml file
#setupXM is the path and filename of the setup.xml file
from getSetupInformation import getSetupInformation
import os
def inputHandlerToUI(setupFolder, setupInfo):
    #assign tag values in the setupxml to the setupInfo model
    getSetupInformation(os.path.join(setupFolder, setupInfo.project + 'Setup.xml'), setupInfo)
    return