#TODO change module name
class SQLiteHandler:

    def __init__(self, database):
        import sqlite3 as lite
        self.connection = lite.connect(database)
        self.cursor = self.connection.cursor()
        #TODO move to another location
        self.makeDatabase()

    def getComponentTableCount(self):

        component_count = len(self.cursor.execute("SELECT component_name FROM components").fetchall())
        # return component_count
        return 3
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

    def createRefTable(self, tablename):
        self.cursor.execute("DROP TABLE  If EXISTS " + tablename)
        self.cursor.execute("""
        CREATE TABLE """ + tablename +
                            """( 
                            _id integer primary key,
                        code text unique,
                        description text);
                            """
                            )
        self.connection.commit()
    #String, ListOfTuples -> None
    def addRefValues(self, tablename, values):
        self.cursor.executemany("INSERT INTO " + tablename + "(code, description) VALUES (?,?)" ,values)
        self.connection.commit()

    def makeDatabase(self):

        refTables = [
            'ref_component_attribute',
            'ref_component_type',
            'ref_datetime_format',
            'ref_data_format',
            'ref_load_units',
            'ref_attributes',
            'ref_time_units'
        ]
        for r in refTables:
            self.createRefTable(r)


        self.addRefValues('ref_time_units',[('S','Seconds'),('m','Minutes')])
        self.addRefValues('ref_datetime_format',[('Ordinal','Ordinal'),('Excel','Excel')])

        self.addRefValues('ref_data_format',[('CSV + wind', 'Load information is in a csv, wind data is in a tab delimmited text file'),
                                             ('AVEC CSV', 'All data is within a single CSV file')
                            ])

        self.addRefValues('ref_component_type' ,[('wtg', 'windturbine'),
        ('ws', 'windspeed'), ('gen', 'diesel generator'), ('hyg','hydrokinetic generator'), ('hs', 'waterspeed')])

        self.addRefValues('ref_load_units',[('W', 'watts'), ('KW', 'Killowatts'),('MW','Megawatts')])

        self.addRefValues('ref_attributes' ,[('P', 'power'), ('WS', 'windspeed'),('HS','hydrospeed')])

        if not self.tableExists("components"):
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
             tags text
             );""")

    def getHeaders(self,table):
        #Todo read from database
        headers = self.cursor.execute("select sql from sqlite_master where name = 'components' and type = 'table'")
        print(headers)
        return headers