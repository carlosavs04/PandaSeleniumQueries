import mysql.connector 
from mysql.connector import Error
import pandas as pd

class DbConnection:
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                print("Conexión exitosa a la base de datos")
        except Error as e:
            print(f"Error al conectar a la base de datos: {e}")

    def disconnect(self):
        if self.connection.is_connected():
            self.connection.close()
            print("Conexión cerrada")

    def execute_query(self, query, params=None):
        cursor = None
        results = None

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
        finally:
            if cursor:
                cursor.close()
        
        return results
    
    def execute_query_df(self, query, params=None):
        try:
            return pd.read_sql(query, self.connection, params=params)
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            return None