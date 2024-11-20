import pyodbc

class DatabaseConfig:
    CONNECTION_STRING = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=pchc3112a-04\\SQLEXPRESS;'
        'DATABASE=MultiplatformXR;'
        'Trusted_Connection=yes;'
    )

    @classmethod
    def get_connection(cls):
        return pyodbc.connect(cls.CONNECTION_STRING)