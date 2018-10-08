import os

#gets the file path for a specific folder within the application data ouput structure
def getFilePath(setupFolder, designator,**kwargs):
    if designator == 'Processed':
        return os.path.join(setupFolder,*['..','TimeSeriesData','Processed'])
    elif designator == 'Components':
        return os.path.join(setupFolder, *['..', 'Components'])
    elif designator == 'OutputData':
        return os.path.join(setupFolder, *['..', '..','OutputData'])
    elif designator[0:3] == 'Set':
        return os.path.join(setupFolder, *['..', '..','OutputData', designator])
    elif designator[0:3] == 'Run':
        return os.path.join(setupFolder, *['..', '..','OutputData', kwargs.get('Set'), designator])
    elif designator == 'Project':
        return os.path.join(setupFolder,*['..','..'])

