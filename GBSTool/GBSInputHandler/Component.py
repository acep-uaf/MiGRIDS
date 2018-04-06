# Component class consisting of component name, units and attribute - required for data input
class Component:
    """A class with access to the generic characteristics of a component."""

    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('component')
        self.units = kwargs.get('units')
        self.offset = kwargs.get('offset')
        self.datatype = kwargs.get('datatype')
        self.scale = kwargs.get('scale')
        #type specifies the type of component (i.e. wtg, gen)
        self.type = kwargs.get('type')

    def setDatatype(self, df):
        if self.datatype[0][0:3] == 'int':
            df[self.name] = round(df[self.name].astype('float'), 0)
        else:
            df[self.name] = df[self.name].astype(self.datatype[0])
        return df

    # Component, dictionary -> dictionary
    def toDictionary(self, d):
        d[self.name] = self.__dict__()

        return d