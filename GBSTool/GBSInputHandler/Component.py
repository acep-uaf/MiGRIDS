from GBSController.UIToHandler import UIToHandler
# Component class consisting of component name, units and attribute - required for data input
class Component:
    """A class with access to the generic characteristics of a component."""

    def __init__(self,  **kwargs):
        # component name consists of its type and a number
        self.component_name = kwargs.get('component_name')
        # column name is how the component is referred to in the dataset. Typically component_name and attribute
        self.column_name = kwargs.get('column_name')
        self.original_field_name=kwargs.get('original_field_name')
        self.units = kwargs.get('units')
        self.offset = kwargs.get('offset')
        self.datatype = kwargs.get('datatype')

        self.scale = kwargs.get('scale')
        #type specifies the type of component (i.e. wtg, gen)
        self.type = kwargs.get('type')
        if self.type is None:
            self.inferComponentType()
        self.attribute =kwargs.get('attribute')
        self.filepath = kwargs.get('filepath')
        self.source = kwargs.get('source')

        self.tags=kwargs.get('tags')
    def inferComponentType(self):
        #contact the UIToHandler to get possible types
        handler = UIToHandler()
        possibleTypes = handler.getComponentTypes()
        # match the name to a type
        match = [i for i in possibleTypes if self.column_name[0:3] in i]
        if len(match) > 0:
            return match[0]
        return


    # set the datatype for a column in a dataframe that contains data for a specific component
    def setDatatype(self, df):
        #if the datatype is an integer it becomes a float with 0 decimal places

        if self.datatype[0:3] == 'int':
            df[self.column_name] = round(df[self.column_name].astype('float'), 0)
        else:
            #otherwise it is the specified datatype
            df[self.column_name] = df[self.column_name].astype(self.datatype)
        return df

    # Component, dictionary -> dictionary
    def toDictionary(self):

        return self.__dict__
