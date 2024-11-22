import pyodbc
from datetime import datetime

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
    
    @classmethod
    def insert_page(cls, db, query, page_count, url):
        print('---------------------------------------------------------------------------------------------')
        print('IN DE DATA')
        conn = cls.get_connection()
        cursor = conn.cursor()        

        cursor.execute("""
            SELECT id FROM Query_status WHERE db = ? AND query = ? AND page_count = ?
            """ , 
            (
                db, 
                query, 
                page_count, 
            )
        )
        row = cursor.fetchone()
        if row is None:
                print('It did not exist')
                cursor.execute("""
                    INSERT INTO Query_status 
                    (DB, Query, Page_count, Url, Time_stamp)            
                    OUTPUT INSERTED.id  
                    VALUES ( ?, ? , ?, ?, ?)
                               
                    """ , 
                    (
                        db, 
                        query, 
                        page_count, 
                        url,
                        datetime.now()
                    )
                )
                #cursor.execute("SELECT SCOPE_IDENTITY()")
                last_id = cursor.fetchone()[0]
                conn.commit()
                cursor.close()
                conn.close()
                print(f'ADDED!! {last_id}')
                return last_id
        else:
            last_id = row[0]
            cursor.close()
            conn.close()
            print(f'It existed  {last_id}')
            return last_id

    # TODO> Currently, the insertion from pages is done in the pipeline, probably better to move it here
    @classmethod
    def upsert_issue(cls, pairs, unique_value):
        """
        If it exists, updates,otherwise inserts
        """
        conn = cls.get_connection()
        cursor = conn.cursor()
        print('Trying to upsert an issue')
        field_to_check, value_to_check = unique_value
        try:
            # Verificar si el registro existe
            print((f"SELECT 1 FROM issues WHERE {field_to_check} = ?", value_to_check))
            cursor.execute(f"SELECT 1 FROM issues WHERE {field_to_check} = ?", value_to_check)
            exists = cursor.fetchone()

            if exists:
                #Update query
                set_clause = ", ".join([f"{field} = ?" for field, _ in pairs])
                values = [value for _, value in pairs]
                query = f"UPDATE issues SET {set_clause} WHERE {field_to_check} = ?"
                cursor.execute(query, *values, value_to_check)
                print(f"Updated \n\t\t {query} ... {field_to_check} = {value_to_check}")
            else:
                # INSERT query
                fields = [field for field, _ in pairs]
                values = [value for _, value in pairs]
                #fields.append(field_to_check)
                #values.append(value_to_check)
                placeholders = ", ".join(["?"] * len(fields))
                query = f"INSERT INTO issues ({', '.join(fields)}) VALUES ({placeholders})"
                cursor.execute(query, *values)
                print("Inserted")
            
            conn.commit()
        except pyodbc.Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()



    @classmethod
    def get_all_unreached_issues_urls(cls,url_field, conditions):
        conn = cls.get_connection()
        cursor = conn.cursor()
        try:
            where_clause = " AND ".join([f" {field} {connector} {('NULL' if value is None  else '?')} " for field, connector, value in conditions])
            values = [value for _, _, value in conditions if value is not None]
            query = f"SELECT {url_field} FROM Issues WHERE {where_clause}"
            print(f'Trying to reach query {query}')
            cursor.execute(query, *values)
            urls = [row[0] for row in cursor.fetchall()] 
            return urls      
        except pyodbc.Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()
        return []