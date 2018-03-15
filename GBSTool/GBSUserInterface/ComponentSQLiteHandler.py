class SQLiteHandler:

    def __init__(self, database):
        import sqlite3 as lite
        self.connection = lite.connect(database)
        self.cursor = self.connection.cursor()
        self.makeDatabase()

    def getComponentTableCount(self):

        component_count = len(self.cursor.execute("SELECT component_name FROM components").fetchall())
        # return component_count
        return 3

    def getComponents(self):
        component_tuple = self.cursor.execute("SELECT * FROM components").fetchall()
        return component_tuple

    def tableExists(self, table):
        try:
            self.cursor.execute("select * from " + table + " limit 1").fetchall()
        except:
            return False
        return True

    def makeDatabase(self):

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