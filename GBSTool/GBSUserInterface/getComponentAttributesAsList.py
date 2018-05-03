def getComponentAttributesAsList(componentName, componentFolder):
    from GBSController.UIToHandler import UIToHandler

    handler = UIToHandler()
    componentSoup = handler.makeComponentDescriptor(componentName, componentFolder)
    attributeList = []
    for tag in componentSoup.find_all():
        if (tag.parent.name not in ['component', 'childOf', 'type']) & (tag.name not in ['component','childOf','type']):
            parent = tag.parent.name
            pt = '.'.join([parent,tag.name])
        else:
            pt = tag.name

        for a in tag.attrs:
            if a != 'unit':
                 attributeList.append('.'.join([pt,str(a)]))
    return attributeList