from GBSUserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler
from GBSController.UIToHandler import UIToHandler
from GBSUserInterface.makeAttributeXML import integerToTimeIndex
def updateSetsSql(set, setupModel):
    uihandler = UIToHandler()
    xmlfile =  setupModel.getSetAttributeXML(set)
    soup = uihandler.getSetAttributeXML(xmlfile)
    setupTags = soup.findChild('setupTag')['value'].split(' ')
    setupValue = soup.findChild('setupValue')['value'].split(' ')
    if setupValue[setupTags.index("runTimeSteps")].split(',') != 'all':
        start = integerToTimeIndex(setupModel.data.fixed, setupValue[setupTags.index("runTimeSteps")].split(',')[0])
        end = integerToTimeIndex(setupModel.data.fixed, setupValue[setupTags.index("runTimeSteps")].split(',')[1])
    else:
        start = ''
        end = ''
    timestep = setupValue[setupTags.index("timeStep")]
    components = setupValue[setupTags.index("componentNames")]
    updateTuple = (start, end, timestep, components,  set)
    # check if the setup information exists in the database
    sqlHandler = ProjectSQLiteHandler()
    dataTuple = sqlHandler.cursor.execute("select date_start, date_end, timestep, component_names, _id from setup where set_name = '" + set + "'").fetchone()
    # update setup table database columns with xml attribute information if it exists otherwise create a record
    if dataTuple is not None:
        #update

        sqlHandler.cursor.execute("UPDATE setup set date_start = ?, date_end = ?, timestep = ?,component_names = ? where set_name = ?", updateTuple)
    else:
        #insert
        sqlHandler.cursor.execute(
            "INSERT INTO setup (date_start, date_end, timestep, component_names, set_name) Values(?,?,?,?,?) ", updateTuple)

    # update the set table also
    compNames = soup.findChild('compName')['value'].split(' ')
    compTags = soup.findChild('compTag')['value'].split(' ')
    compAttrs = soup.findChild('compAttr')['value'].split(' ')
    compValues = soup.findChild('compValue')['value'].split(' ')
    for i,c in enumerate(compNames):
        dataTuple = (set,c,compTags[i],compValues[i])
        #this will result in a new row if a value has changed directly in the xml but not in the project database
        if len(sqlHandler.cursor.execute("SELECT * from sets where set_name = ? AND component = ? AND change_tag = ? AND to_value = ?", dataTuple).fetchall()) < 1:
            sqlHandler.cursor.execute("INSERT INTO sets (set_name, component, change_tag, to_value) VALUES (?,?,?,?)", dataTuple)

    sqlHandler.connection.commit()
    sqlHandler.closeDatabase()

    return
#TODO write function to update run table
def updateRunsSql():
    return
#load previously run sets.
# ModelSetupInfo -> Boolean
def loadSets(model,window):
    import os
    from GBSUserInterface.FormModelRuns import SetsTableBlock, SetsPages
    from PyQt5 import QtWidgets
    # if sets have been run then setup should not be editable, return True
    if os.path.exists(model.outputFolder):
        # look in output Data folder for sets
        sets = [os.path.basename(x) for x in os.listdir(model.outputFolder) if os.path.basename(x)[0:3] == 'Set']
        for set in sets:
            # make a tab unless its set0
            if set != 'Set0':
                modelRunForm =window.findChild(QtWidgets.QWidget,"modelDialog")
                modelRunForm.newTab()

            # fill the tab with data
            #the tables are pulling from the sqlite database so we just need to make sure those data are up to date
            updateSetsSql(set,model)
            # fill run table with run data
            updateRunsSql()
            book = window.findChild(SetsPages)
            objects = book.findChildren(QtWidgets.QWidget)
            # each tab is a QStackedWidget
            currentTab = book.findChildren(SetsTableBlock)[int(''.join(filter(str.isdigit, set)))]

            if currentTab is not None:
                currentTab.fillData(set)
    if len(sets) > 1:
        return True
    return False




