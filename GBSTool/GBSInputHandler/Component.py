# Component class consisting of component name, units and attribute - required for data input
class Component:
    """A class with access to the generic characteristics of a component."""

    def __init__(self, *args, **kwargs):
        self.component_name = kwargs.get('component_name')
        self.original_field_name=kwargs.get('original_field_name')
        self.units = kwargs.get('units')
        self.offset = kwargs.get('offset')
        self.datatype = kwargs.get('datatype')
        self.scale = kwargs.get('scale')
        #type specifies the type of component (i.e. wtg, gen)
        self.type = kwargs.get('type')
        self.filepath = kwargs.get('filepath')
        self.pinmaxpa = kwargs.get('pinmaxpa')
        self.qinmaxpa = kwargs.get('qinmaxpa')
        self.qoutmaxpa = kwargs.get('qoutmaxpa')
        self.voltagesource=kwargs.get('voltagesource')
        self.tags=kwargs.get('tags')


    def setDatatype(self, df):
        if self.datatype[0][0:3] == 'int':
            df[self.component_name] = round(df[self.component_name].astype('float'), 0)
        else:
            df[self.name] = df[self.name].astype(self.datatype[0])
        return df

    # Component, dictionary -> dictionary
    def toDictionary(self):
        d = {}
        d[self.component_name] = self.__dict__
        #append tags to dictionary as keys and values
        for t in self.tags.keys():
            d[self.component_name][t]=self.tags[t]

        return d