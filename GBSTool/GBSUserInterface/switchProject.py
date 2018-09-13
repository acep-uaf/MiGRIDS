import shutil
import os
from GBSUserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler
from GBSUserInterface.ModelSetupInformation import ModelSetupInformation
def switchProject(setupModel):
    '''saves an existing project, clears the database and initiates a new project'''
    saveProject(setupModel.setupFolder)
    del setupModel
    newmodel = ModelSetupInformation()
    clearProject()
    return newmodel

def saveProject(pathTo):
    '''saves the current project database to the specified path'''
    path = os.path.dirname(__file__)
    shutil.copy(os.path.join(path, '../project_manager'),
                os.path.join(pathTo, 'project_manager'))
    print('Database was saved to %s' % pathTo)
    return

def clearProject():
    handler = ProjectSQLiteHandler()
    # get the name of the last project worked on
    lastProjectPath = handler.getProjectPath()
    handler.makeDatabase()
    handler.closeDatabase()
    return lastProjectPath