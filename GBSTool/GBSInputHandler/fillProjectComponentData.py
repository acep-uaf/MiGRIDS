#String, SetupInformation -> None
#produces xml files associated with components in a project
def fillProjectComponentData(setupDir, setupInfo):
    import os
    from writeXmlTag import writeXmlTag
    componentNames = setupInfo.componentNames  # unique list of component names
    #
    # # get the directory to save the component descriptor xml files in
    componentDir = os.path.join(setupDir,'../Components/')
    for row in setupInfo.components: # for each component
         componentDesctiptor = row.component_name + 'Descriptor.xml'

         for tag in row.__dict__.keys(): # for each tag (skip component name column)
            if tag not in ['component_name', 'tags']:
                attr = 'value'
                value = row.__dict__[tag]
                print(tag, attr,value)
                writeXmlTag(componentDesctiptor,tag,attr,value,componentDir)
            elif (tag == 'tags') & (row.__dict__[tag] != ''):
                print ('tags: %s ' %row.__dict__[tag])
            # write the extras
                for extra in row.__dict__[tag].keys():  # for each extra tag
                   print(extra, attr, value)
                   attr = 'value'
                   value = row.__dict__[tag][extra]
                   writeXmlTag(componentDesctiptor, extra, attr, value, componentDir)
    return