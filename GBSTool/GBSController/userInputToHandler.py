#Is called from the GBSUserInterface package to initial xml file generation through the GBSInputHandler functions
#SetupInformation ->
def userInputToHandler(setupInfo):
    from initiateProject import initiateProject
    from fillProjectData import fillProjectData

    # write the information to a setup xml
    # create a mostly blank xml setup file and individual component xml files
    initiateProject(setupInfo.project, setupInfo.componentNames, setupInfo.setupFolder, setupInfo.setupFolder)
    #fill in project data
    fillProjectData(setupInfo.setupFolder, setupInfo)