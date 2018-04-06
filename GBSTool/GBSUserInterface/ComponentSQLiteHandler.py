#TODO change module name
class SQLiteHandler:

    def __init__(self, database):
        import sqlite3 as lite
        self.connection = lite.connect(database)
        self.cursor = self.connection.cursor()


    def getComponentTableCount(self):

        component_count = len(self.cursor.execute("SELECT component_name FROM components").fetchall())
        # return component_count
        return component_count

    def closeDatabase(self):
        self.cursor.close()
        self.connection.close()

    def getComponents(self):
        component_tuple = self.cursor.execute("SELECT * FROM components").fetchall()
        return component_tuple

    def tableExists(self, table):
        try:
            self.cursor.execute("select * from " + table + " limit 1").fetchall()
        except:
            return False
        return True
    #String, integer -> String
    def getComponentData(self, column, row):
        if column != '':
            values = self.cursor.execute("select " + column + " from components limit ?", [row+1]).fetchall()

            if (len(values) > row) :
                value = values[row][0]
                if value is not None:
                    return value

        return 0

    def createRefTable(self, tablename):
        self.cursor.execute("DROP TABLE  If EXISTS " + tablename)
        self.cursor.execute("""
        CREATE TABLE """ + tablename +
                            """( 
                            _id integer primary key,
                            sort_order integer,
                        code text unique,
                        description text);
                            """
                            )
        self.connection.commit()
    #String, ListOfTuples -> None
    def addRefValues(self, tablename, values):

        self.cursor.executemany("INSERT INTO " + tablename + "(sort_order,code, description) VALUES (?,?,?)" ,values)
        self.connection.commit()

    def makeDatabase(self):

        refTables = [
            'ref_component_attribute',
            'ref_component_type',
            'ref_datetime_format',
            'ref_data_format',
            'ref_load_units',
            'ref_attributes',
            'ref_time_units',
            'ref_universal_units',
            'ref_true_false'
        ]
        for r in refTables:
            self.createRefTable(r)
        self.addRefValues('ref_true_false',[(0,'T','True'),(1,'F','False')])
        self.addRefValues('ref_universal_units', [(0, 'W', 'Watts'), (1, 'kW', 'kilowatts'),(2, 'MW', 'megawatts'),
                                                  (3, 'm/s','meters per second'),(4,'kn','knots')])
        self.addRefValues('ref_time_units',[(0,'S','Seconds'),(1,'m','Minutes')])
        self.addRefValues('ref_datetime_format',[(0,'Ordinal','Ordinal'),(1,'Excel','Excel')])

        self.addRefValues('ref_data_format',[(0,'CSV + wind', 'Load information is in a csv, wind data is in a tab delimmited text file'),
                                             (1,'AVEC CSV', 'All data is within a single CSV file')
                            ])

        self.addRefValues('ref_component_type' ,[(0,'wtg', 'windturbine'),
        (1,'ws', 'windspeed'), (2,'gen', 'diesel generator'), (3,'hyg','hydrokinetic generator'), (4,'hs', 'waterspeed')])

        self.addRefValues('ref_load_units',[(0,'W', 'watts'), (1,'kW', 'Kilowatts'),(2,'MW','Megawatts')])

        self.addRefValues('ref_attributes' ,[(0,'P', 'power'), (1,'WS', 'windspeed'),(2,'HS','hydrospeed')])
        #TODO stop deleting components

        self.cursor.execute("DROP TABLE IF EXISTS components")
        self.cursor.executescript("""CREATE TABLE components
         (_id integer primary key,
         original_field_name text,
         component_type text,
         component_name text,
         units text,
         scale numeric,
         offset numeric,
         attribute text,
         p_in_maxpa numeric,
         q_in_maxpa numeric, 
         q_out_maxpa numeric,
         is_voltage_source text,
         tags text,
         FOREIGN KEY (component_type) REFERENCES ref_component_type(code),
         FOREIGN KEY (units) REFERENCES ref_universal_units(code),
         FOREIGN KEY (attribute) REFERENCES ref_attributes(code),
         FOREIGN KEY (is_voltage_source) REFERENCES ref_true_false(code)
         );""")

        self.cursor.executemany("INSERT INTO components (original_field_name, component_type, component_name) values (?,?,?)",
                                [('Hank', 'wtg','wtg1P'),('gen1','gen','gen1P')])
    def getRefInput(self, table):
        import pandas as pd
        # create list of values for a combo box
        values = pd.read_sql_query("SELECT code, description FROM " + table + " ORDER By sort_order", self.connection)
        valueStrings = []
        for v in range(len(values)):
            valueStrings.append(values.loc[v, 'code'] + ' - ' + values.loc[v, 'description'])
        return valueStrings

    def getHeaders(self,table):
        #Todo read from database
        headers = self.cursor.execute("select sql from sqlite_master where name = " + table + " and type = 'table'")

        return headers
    #String, String -> Boolean
    def hasRef(self,column):

        sql = self.cursor.execute("SELECT sql FROM sqlite_master WHERE type = 'table' and name = 'components'").fetchone()
        if column + ') references ' in sql[0].lower():
            return True
        return False
    def getRef(self,column):
        s1 = self.cursor.execute("SELECT sql FROM sqlite_master WHERE type = 'table' and name = 'components'").fetchone()
        s1 = s1[0].lower()
        s2 = column + ") references "
        table = s1[s1.find(s2) + len(s2):].replace("(code)", "")
        table = table.replace(")","")
        table = table.split(",")[0]

        table = table.strip()

        return table

    def getCodes(self,table):

        import pandas as pd
        codes = pd.read_sql_query("select code from " + table + " ORDER BY sort_order", self.connection)

        codes = (codes['code']).tolist()

        return codes