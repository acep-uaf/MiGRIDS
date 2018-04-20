#TODO change module name
class ProjectSQLiteHandler:

    def __init__(self, database):
        import sqlite3 as lite
        self.connection = lite.connect(database)
        self.cursor = self.connection.cursor()


    def getComponentTableCount(self):

        component_count = len(self.cursor.execute("SELECT * FROM components").fetchall())
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

        return

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
        print('Making default database')
        refTables = [
            'ref_component_attribute',
            'ref_component_type',
            'ref_datetime_format',
            'ref_data_format',
            'ref_power_units',
            'ref_attributes',
            'ref_time_units',
            'ref_speed_units',
            'ref_flow_units',
            'ref_voltage_units',
            'ref_current_units',
            'ref_irradiation_units',
            'ref_temperature_units',
            'ref_true_false',
            'ref_env_attributes',
            'ref_frequency_units'
        ]
        for r in refTables:
            self.createRefTable(r)
        self.addRefValues('ref_current_units',[(0,'A','amps'),(1,'kA','kiloamps')])
        self.addRefValues('ref_frequency_units',[(0, 'Hz','hertz')])
        self.addRefValues('ref_temperature_units',[(0,'C','Celcius'),(1,'F','Farhenheit'),(2,'K','Kelvin')])
        self.addRefValues('ref_irradiation_units',[(0,'W/m2','Watts per square meter')])
        self.addRefValues('ref_flow_units',[(0,'m3/s', 'cubic meter per second'),(1, 'L/s', 'liters per second'),
                                            (2, 'cfm', 'cubic feet per meter'),(3,'gal/min','gallon per minute'),(4, 'kg/s', 'killograms per second')])
        self.addRefValues('ref_voltage_units',[(0,'V','volts'),(1, 'kV','kilovolts')])
        self.addRefValues('ref_true_false',[(0,'T','True'),(1,'F','False')])
        self.addRefValues('ref_speed_units', [(0, 'm/s','meters per second'),(1,'ft/s','feet per second'),
                                              (2,'km/hr','kilometers per hour'),(3,'mi/hr','miles per hour')])
        self.addRefValues('ref_time_units',[(0,'S','Seconds'),(1,'m','Minutes')])
        self.addRefValues('ref_datetime_format',[(0,'Ordinal','Ordinal'),(1,'Excel','Excel')])

        self.addRefValues('ref_data_format',[(0,'CSV + wind', 'Load information is in a csv, wind data is in a tab delimmited text file'),
                                             (1,'AVEC CSV', 'All data is within a single CSV file')
                            ])

        self.addRefValues('ref_component_type' ,[(0,'wtg', 'windturbine'),
        (1,'gen', 'diesel generator'), (2,'inv','inverter'),(3,'tes','thermal energy storage'),(4, 'ees','energy storage')])

        self.addRefValues('ref_power_units',[(0,'W', 'watts'), (1,'kW', 'Kilowatts'),(2,'MW','Megawatts'),
                                             (3, 'var', 'vars'),(4,'kvar','kilovars'),(5,'Mvar','Megavars'),
                                             (6, 'VA','volt-ampere'),(7,'kVA','kilovolt-ampere'),(8,'MVA','megavolt-ampere'),(9, 'pu',''),(10,'PU',''),(11,'PU*s','')])

        self.addRefValues('ref_env_attributes', [(0,'WS', 'Windspeed'), (1,'IR', 'Solar Irradiation'),
                                                 (2,'WF','Waterflow'),(3,'Tamb','Ambient Temperature')])
        self.addRefValues('ref_attributes' ,[(0,'P', 'Real Power'), (1,'Q','Reactive Power'),(2,'S','Apparent Power'),
                                             (3,'PF','Power Factor'),(4,'V','Voltage'),(5, 'I', 'Current'),
                                             (6, 'f', 'Frequency'), (7,'TStorage','Internal Temperature Thermal Storage'),
                                             (8,'PAvail','Available Real Power'), (9,'QAvail','Available Reactive Power'),
                                             (10,'SAvail','Available Apparent Power')])

        #merge unit reference tables
        self.cursor.execute("DROP TABLE IF EXISTS ref_units")
        self.cursor.executescript("CREATE TABLE ref_units (_id integer primary key, code text unique, description text)")
        unit_tables_tuple = self.cursor.execute("select name from sqlite_master where type = 'table' and name like '%units'").fetchall()
        for u in unit_tables_tuple:
            self.cursor.execute("INSERT INTO ref_units(code, description) SELECT code, description from " + u[0] + " Where code not in (select code from ref_units)")

        self.connection.commit()
        self.cursor.execute("DROP TABLE IF EXISTS components")
        self.cursor.executescript("""CREATE TABLE components
         (_id integer primary key,
         original_field_name text,
         component_type text,
         component_name text unique,
         units text,
         scale numeric,
         offset numeric,
         attribute text,
        
         tags text,
         FOREIGN KEY (component_type) REFERENCES ref_component_type(code),
         FOREIGN KEY (units) REFERENCES ref_universal_units(code),
         FOREIGN KEY (attribute) REFERENCES ref_attributes(code)
         
         );""")
             # #create a sql function to access the getTypeCount function
        self.connection.create_function("componentName",1,self.getTypeCount)
        self.connection.commit()

        self.cursor.execute("DROP TABLE IF EXISTS environment")
        self.cursor.executescript("""CREATE TABLE IF NOT EXISTS environment
                 (_id integer primary key,
                 original_field_name text,
                 component_name text unique,
                 units text,
                 scale numeric,
                 offset numeric,
                 attribute text,
                 
                 tags text,
                 
                 FOREIGN KEY (units) REFERENCES ref_universal_units(code),
                 FOREIGN KEY (attribute) REFERENCES ref_env_attributes(code)
                 
                 );""")

        self.connection.commit()
    def insertRecord(self, table, fields, values):
        string_fields = ','.join(fields)
        string_values = ','.join('?' * len(values))

        self.cursor.execute("INSERT INTO " + table + "(" + string_fields + ")" + "VALUES (" + string_values + ")", values)
        self.connection.commit()
    def getRefInput(self, tables):
        #table is a list of tables
        import pandas as pd
        # create list of values for a combo box
        valueStrings = []
        for t in tables:
            values = pd.read_sql_query("SELECT code, description FROM " + t + " ORDER By sort_order", self.connection)

            for v in range(len(values)):
                valueStrings.append(values.loc[v, 'code'] + ' - ' + values.loc[v, 'description'])
        return valueStrings

    def getTypeCount(self,finalName):
        import re
        print('Type count called for %s' %finalName)
        count = re.findall(r'\d+', finalName)
        if len(count) > 0:
            count = int(count[0])
            return count +1
        return 0

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
    def updateComponent(self, dict):
        for k in dict.keys():
            try:
                self.cursor.execute("UPDATE components SET " + k + " = ? WHERE component_name = ?", [dict[k],dict['component_name']])
            except:
                print('%s column was not found in the data table' %k)
        self.connection.commit()
    #determines if a componente record needs to be created or updated and implements the correct function
    #returns true if the record is a new record and was added to the table
    #dictionary -> Boolean
    def writeComponent(self,componentDict):
        if len(self.cursor.execute("SELECT * FROM components where component_name = ?", [componentDict['component_name']]).fetchall()) > 0:
            self.updateComponent(componentDict)
        else:
            self.cursor.execute('INSERT INTO components (component_name) VALUES (?)', [componentDict['component_name']])
            self.updateComponent(componentDict)
            return True
        return False
    def getCodes(self,table):

        import pandas as pd
        codes = pd.read_sql_query("select code from " + table + " ORDER BY sort_order", self.connection)

        codes = (codes['code']).tolist()

        return codes
