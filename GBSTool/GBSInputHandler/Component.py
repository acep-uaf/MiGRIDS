# Component class consisting of component name, units and attribute - required for data input
class Component:
    """A class with access to the generic characteristics of a component."""

    def __init__(self,  **kwargs):
        self.column_name = kwargs.get('component_name')
        self.original_field_name=kwargs.get('original_field_name')
        self.units = kwargs.get('units')
        self.offset = kwargs.get('offset')
        self.datatype = kwargs.get('datatype')
        self.scale = kwargs.get('scale')
        #type specifies the type of component (i.e. wtg, gen)
        self.type = kwargs.get('type')
        self.attribute =kwargs.get('attribute')
        self.filepath = kwargs.get('filepath')

        self.tags=kwargs.get('tags')

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
