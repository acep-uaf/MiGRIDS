#String, SetupInformation -> None
#produces xml files associated with components in a project
def fillProjectComponentData(setupDir, setupInfo):
    componentNames = setupInfo.componentNames  # unique list of component names
    #
    # # get the directory to save the component descriptor xml files in
    # componentDir = projectDir + '/InputData/Components/'
    # for row in range(df.shape[0]): # for each component
    #     componentDesctiptor = componentNames[row] + 'Descriptor.xml'
    #
    #     for column in range(1,df.shape[1]): # for each tag (skip component name column)
    #         tag = df.columns[column]
    #         attr = 'value'
    #         value = df[df.columns[column]][row]
    #         writeXmlTag(componentDesctiptor,tag,attr,value,componentDir)
    #
    #     # see if there is a csv file with more tag information for that component
    #     componentTagInfo = componentNames[row] + 'TagInformation.csv'
    #     os.chdir(userInputDir)
    #     if os.path.exists(componentTagInfo):
    #         dfComponentTag = pd.read_csv(componentTagInfo)  # read as a data frame
    #         dfComponentTag = dfComponentTag.fillna('')  # remplace nan values with empty'
    #         componetTag = dfComponentTag.as_matrix()  # matrix of values from data frame
    #         # fill tag information into the component descriptor xml file
    #         for row in range(componetTag.shape[0]):  # for each tag
    #             tag = componetTag[row, range(0, 4)]
    #             tag = [x for x in tag if not x == '']
    #             attr = dfComponentTag['Attribute'][row]
    #             value = dfComponentTag['Value'][row]
    #             writeXmlTag(componentDesctiptor, tag, attr, value, componentDir)
    return