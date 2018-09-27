import pandas as pd

class ProjectSQLiteHandler:

    def __init__(self, database='project_manager'):
        import sqlite3 as lite
        self.connection = lite.connect(database)
        self.cursor = self.connection.cursor()

    def closeDatabase(self):
        self.cursor.close()
        self.connection.close()
        return

    def getProjectPath(self):
        if self.tableExists('project'):
            projectPath = self.cursor.execute("select project_path from project").fetchone()
            if projectPath is not None:
                return projectPath[0]

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
    #makes the default database associated with every new project.
    def makeDatabase(self):
        print('Making default database')
        refTables = [
            'ref_component_attribute',
            'ref_component_type',
            'ref_date_format',
            'ref_time_format',
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
            'ref_frequency_units',
            'ref_file_type'
        ]
        for r in refTables:
            self.createRefTable(r)
        self.addRefValues('ref_file_type',[(0,'CSV','Comma Seperated Values'), (1,'MET','MET text file'), (2,'TXT','Tab delimited')])
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
        self.addRefValues('ref_date_format',[(0,'MM/DD/YY','MM/DD/YY'),(1,'MM/DD/YYYY','MM/DD/YYYY'),
                                                 (2,'YYYY/MM/DD','YYYY/MM/DD'),(3,'DD/MM/YYYY','DD/MM/YYYY'),
                                             (4, 'MM-DD-YY', 'MM-DD-YY'), (5, 'MM-DD-YYYY', 'MM-DD-YYYY'),
                                             (6, 'YYYY-MM-DD', 'YYYY-MM-DD'), (7, 'DD-MM-YYYY', 'DD-MM-YYYY'),
                                             (8, 'mon dd yyyy', 'mon dd yyyy'),
                                             (9, 'days', 'days')
                                                 ])
        self.addRefValues('ref_time_format',[(0,'HH:MM:SS','HH:MM:SS'),(1,'HH:MM','HH:MM'),
                                             (2,'hours','hours'),
                                                 (3,'minutes','minutes'),(4,'seconds','seconds')
                                                 ])

        self.addRefValues('ref_data_format',[(0,'components + MET', 'Load and component data are seperate from wind data'),
                                             (1,'components', 'All component, load and environemtnal data is within a single timeseries file'),
                                             (2, 'component + load + environment', 'Seperate files for load, component and wind data.')
                            ])

        self.addRefValues('ref_component_type' ,[(0,'wtg', 'windturbine'),
        (1,'gen', 'diesel generator'), (2,'inv','inverter'),(3,'tes','thermal energy storage'),(4, 'ees','energy storage'),(5, 'load', 'total load')])

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
        #project table
        self.cursor.execute("DROP TABLE IF EXISTS project")
        self.cursor.executescript("""CREATE TABLE project
        (_id  integer primary key,
        project_path text,
        project_name text);""")

        #component table
        self.cursor.execute("DROP TABLE IF EXISTS components")
        self.cursor.executescript("""CREATE TABLE components
         (_id integer primary key,
         inputfiledir text,
         original_field_name text,
         component_type text,
         component_name text,
         units text,
         scale numeric,
         offset numeric,
         attribute text,
         tags text,
         
         FOREIGN KEY (component_type) REFERENCES ref_component_type(code),
         FOREIGN KEY (units) REFERENCES ref_universal_units(code),
         FOREIGN KEY (attribute) REFERENCES ref_attributes(code)
         
         );""")

        self.connection.commit()
        self.cursor.execute("DROP TABLE IF EXISTS sets")
        self.cursor.executescript("""
        CREATE TABLE IF NOT EXISTS sets
        (_id integer primary key,
        set_name text , 
        component text ,
        change_tag text,
        to_value text);""")

        self.cursor.execute("DROP TABLE IF EXISTS input_files")
        self.cursor.executescript("""
                CREATE TABLE IF NOT EXISTS input_files
                (_id integer primary key,
                inputfiletypevalue text , 
                datatype text ,
                inputfiledirvalue text,
                timestep text,
                datechannelvalue text,
                datechannelformat text,
                timechannelvalue text,
                timechannelformat text,
                includechannels text,
                timezonevalue text,
                usedstvalue text,
                FOREIGN KEY (timechannelformat) REFERENCES ref_time_format(code),
                FOREIGN KEY (datechannelformat) REFERENCES ref_date_format(code));""")

        #The table optimize input only contains parameters that were changed from the default
        self.cursor.execute("Drop TABLE IF EXISTS optimize_input")
        self.cursor.executescript("""
                     CREATE TABLE IF NOT EXISTS optimizer_input
                     (_id integer primary key,
                     parameter text,
                     parameter_value text);""")

        self.cursor.execute("DROP TABLE IF EXISTS runs")
        self.cursor.executescript("""
                CREATE TABLE IF NOT EXISTS runs
                (_id integer primary key,
                set_id text,
                set_name text
                run_name text);""")

        self.cursor.execute("DROP TABLE IF EXISTS setup")
        self.cursor.executescript("""
                        CREATE TABLE IF NOT EXISTS setup
                        (_id integer primary key,
                        set_name unique,
                        date_start text,
                        date_end text,
                        timestep integer,
                        component_names text
                        );""")

        self.cursor.execute("INSERT INTO setup (set_name,timestep,date_start,date_end) values('default',1,'2016-01-01','2016-12-31')")

        self.cursor.execute("DROP TABLE IF EXISTS environment")
        self.cursor.executescript("""CREATE TABLE IF NOT EXISTS environment
                 (_id integer primary key,
                 inputfiledir text,
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

    #get the set info for a specific set or default values if no set is specified
    #String -> dictionary
    def getSetInfo(self,set='default'):
        setDict = {}
        #get tuple
        values = self.cursor.execute("select timestep, date_start, date_end, component_names from setup where set_name = '" + set + "'").fetchone()
        if values is None:
            values = self.cursor.execute(
                "select timestep, date_start, date_end, component_names from setup where set_name = 'default'").fetchone()

        setDict['timestep'] = values[0]
        setDict['date_start'] = values[1]
        setDict['date_end'] = values[2]
        setDict['component_names'] = values[3]
        values = self.cursor.execute("select date_start, date_end from setup where set_name = 'default'").fetchone()
        setDict['min_date'] = values[0]
        setDict['max_date'] = values[1]
        if setDict.get('component_names') is None:
            setDict['component_names'] = []

        return setDict
    #inserts a single record into a specified table given a list of fields to insert values into and a list of values
    #String, ListOfString, ListOfString
    def insertRecord(self, table, fields, values):
        string_fields = ','.join(fields)
        string_values = ','.join('?' * len(values))
        try:
            self.cursor.execute("INSERT INTO " + table + "(" + string_fields + ")" + "VALUES (" + string_values + ")", values)
            self.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False

    # updates a single record in a specified table given a field to match, value to match, list of fields to insert values into and a list of values
    # String, ListOfString, ListOfString, ListOfString, ListOfString
    def updateRecord(self,table, keyField,keyValue,fields,values):
        updateFields = ', '.join([a + " = '" + b + "'" for a,b in zip(fields,values)])

        keyFields = ', '.join([a + " = '" + b + "'" for a,b in zip(keyField,keyValue)])
        try:
            self.cursor.execute("UPDATE " + table + " SET " + updateFields + " WHERE " + keyFields
                                )
            self.connection.commit()
            return True
        except Exception as e:
            print(e)
            print(type(e))

            return False
        return

    #resturns a string that combines code and descriptor columns from a reference table into a single '-' sepearted string
    #String -> String
    def getRefInput(self, tables):
        #table is a list of tables

        # create list of values for a combo box
        valueStrings = []
        for t in tables:
            values = pd.read_sql_query("SELECT code, description FROM " + t + " ORDER By sort_order", self.connection)

            for v in range(len(values)):
                valueStrings.append(values.loc[v, 'code'] + ' - ' + values.loc[v, 'description'])
        return valueStrings
    #returns the number of components of a specific type withing the component table
    #String -> integer
    def getTypeCount(self,componentType):
        import re
        #get the highest component name (biggest number)
        finalName = self.cursor.execute("SELECT component_name FROM components where component_type = '" + componentType + "' ORDER BY component_name DESC").fetchone()
        if finalName[0] is not None:
            finalName=finalName[0]
            #extract the numbers in the name
            count = re.findall(r'\d+',finalName)
            #if there is more than one number use only the last number and add 1 to it
            #if there aren't any other components of that type return 0
            if len(count) > 0:
                count = int(count[0])
                return count +1
        return 0
    def dataCheck(self,table):
        import re
        #get the highest component name (biggest number)
        data = self.cursor.execute("SELECT * FROM " + table).fetchall()
        return data
    #returns a list of column names for a table
    # String -> list
    def getHeaders(self,table):
        #Todo read from database
        headers = self.cursor.execute("select sql from sqlite_master where name = " + table + " and type = 'table'")

        return headers
    #returns true if a field within the specified table has a reference constraint
    #String, String -> Boolean
    def hasRef(self,column, table):

        sql = self.cursor.execute("SELECT sql FROM sqlite_master WHERE type = 'table' and name = '" + table + "'").fetchone()
        if column + ') references ' in sql[0].lower():
            return True
        return False
    #returns the name of a reference table for a specified column in a table
    #String, String -> String
    def getRef(self,column, table):
        s1 = self.cursor.execute("SELECT sql FROM sqlite_master WHERE type = 'table' and name = '" + table + "'").fetchone()
        s1 = s1[0].lower()
        s2 = column + ") references "
        table = s1[s1.find(s2) + len(s2):].replace("(code)", "")
        table = table.replace(")","")
        table = table.split(",")[0]

        table = table.strip()

        return table
    #updates the component table with a key and values in a dictionary
    #Dictionary -> None
    def updateComponent(self, dict):
        for k in dict.keys():
            try:
                self.cursor.execute("UPDATE components SET " + k + " = ? WHERE component_name = ?", [dict[k],dict['component_name']])
            except:
                print('%s column was not found in the data table' %k)
        self.connection.commit()
    #determines if a component record needs to be created or updated and implements the correct function
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

    #returns a table of values for the code column in a a reference table
    #String -> pandas.Series
    def getCodes(self,table):

        import pandas as pd
        codes = pd.read_sql_query("select code from " + table + " ORDER BY sort_order", self.connection)

        codes = (codes['code']).tolist()

        return codes
    #returns a list of components associated with a project
    def getComponentNames(self):

        names = self.cursor.execute("select component_name from components").fetchall()
        if names is not None:
            names = [''.join(i) for i in names if i is not None]
            print(self.dataCheck('components'))
            return pd.Series(names).tolist()
        return []
    def getComponentsTable(self, filter):
        print(self.dataCheck("components"))
        #sql = """select component_name, original_field_name, units,attribute from components where inputfiledir = ({0})"""
        #sql = sql.format('?', ','.join('?' * len((1))))
        sql = """select component_name, original_field_name, units,attribute from components where inputfiledir = ?"""
        #sql = """select component_name, original_field_name, units,attribute from components"""
        #df = pd.read_sql_query(sql, self.connection)
        df = pd.read_sql_query(sql,self.connection,params=[filter])
        sql = """select component_name, original_field_name, units,attribute from environment where inputfiledir = ?"""
        df.append(pd.read_sql_query(sql,self.connection,params=[filter]))
        return df
    def getInputPath(self, pathNum):
        '''returns the file folder for the given input file number (corrasponds to fileblock in setup page)'''
        path = self.cursor.execute("select inputfiledirvalue from input_files where _id = " + pathNum).fetchone()
        if path is not None:
           return path[0]
        return
    def dataComplete(self):
        required={'components':['original_field_name','component_type','component_name','units','attribute'],
'environment':['original_field_name','component_name','units','attribute'],
'project':['project_path']}
        for k in required.keys():
            condition = ' OR '.join(['{0} IS NULL'.format(x) for x in required[k]])
            m = self.cursor.execute("select * from " + k + " where " + condition).fetchall()
            if len(self.cursor.execute("select * from " + k + " where " + condition).fetchall()) > 1 :
                return False
        return True