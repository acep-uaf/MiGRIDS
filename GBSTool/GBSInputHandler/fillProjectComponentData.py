#String, Component -> None
#writes individual tags to an existing xml file
def fillProjectComponentData(component, componentDir):
    import os
    from writeXmlTag import writeXmlTag


    componentDescriptor = component.component_name + 'Descriptor.xml'

    for tag in component.__dict__.keys(): # for each tag (skip component name column)
        if tag not in ['component_name', 'tags']:
            attr = 'value'
            value = component.__dict__[tag]

            if (value != '') & (value is not None):
                writeXmlTag(componentDescriptor,tag,attr,value,componentDir)

    return