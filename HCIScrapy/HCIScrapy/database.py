import sqlite3
from datetime import datetime
from config import STORAGE_TEST, CONNECTION_STRING, SEARCH_QUERY, TRIAL
#from HCIScrapy.config import STORAGE_TEST, CONNECTION_STRING, SEARCH_QUERY, TRIAL
import pandas as pd
from bs4 import BeautifulSoup


class DatabaseManager:
    

    @classmethod
    def get_connection(cls):
        return sqlite3.connect(CONNECTION_STRING)

    @classmethod
    def insert_page(cls, db, page_count, url, id_query_totals):

        conn = cls.get_connection()
        cursor = conn.cursor()
        
        print(f'Verifying page .... {db} - {page_count} -')
        cursor.execute("""
            SELECT id FROM Query_status WHERE db = ? AND id_query_totals = ? AND page_count = ?
        """, (db, id_query_totals, page_count ))
        row = cursor.fetchone()
        
        if row:
            last_id = row[0]
        else:

            cursor.execute("""
                INSERT INTO Query_status (DB,  Page_count, Url, Time_stamp, id_query_totals)
                VALUES (?, ?, ?, ?, ?)
            """, (db,  page_count, url, datetime.now(), id_query_totals))
            conn.commit()
            last_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return last_id



    @classmethod
    def upsert_issue(cls, pairs, unique_value):

        print(f'Upserting an issue -- {pairs}')

        conn = cls.get_connection()
        cursor = conn.cursor()

        field_to_check, value_to_check = unique_value
        try:
            cursor.execute(f"SELECT 1 FROM issues WHERE {field_to_check} = ?", (value_to_check,))
            exists = cursor.fetchone()

            if exists:
                # Update query
                print(f'Updeting')
                set_clause = ", ".join([f"{field} = ?" for field, _ in pairs])
                values = [value for _, value in pairs] + [value_to_check]
                query = f"UPDATE issues SET {set_clause} WHERE {field_to_check} = ?"
                cursor.execute(query, values)
            else:
                # Insert query
                
                fields = [field for field, _ in pairs]
                values = [value for _, value in pairs]
                placeholders = ", ".join(["?"] * len(fields))
                query = f"INSERT INTO issues ({', '.join(fields)}) VALUES ({placeholders})"
                print(f"QUERY .... {query}")
                print(f'Inserting ... {values}')
                cursor.execute(query, values)
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()


    # TODO outdates with the DB structure
    @classmethod
    def get_issues(cls, select_fields, conditions):

        conn = cls.get_connection()
        cursor = conn.cursor()

        try:
            select_clause = ', '.join(select_fields)
            where_clause = " AND ".join([f"i.{field} {connector} ?" for field, connector, _ in conditions])
            values = [TRIAL] + [value for _, _, value in conditions]
            query = f"""
                SELECT {select_clause} FROM issues_query iq 
                    INNER JOIN issues i ON  i.id_issues = iq.id_issues WHERE 
                    id_trial = ? AND
                    {where_clause}
                """
            print(f'GETTING ISSUESSSS \n\t -- {query} \n\t {values}')
            cursor.execute(query, values)
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_query_totals(cls, db):
        conn = cls.get_connection()
        cursor = conn.cursor()
        try:
            
            cursor.execute("""
                SELECT Id_query_totals, total_results, datetime(timestamp) FROM Query_total_results 
                    WHERE db = ? AND id_trial = ?
            """, (db, TRIAL))
            
            row = cursor.fetchone()
            if row:
                last_query =  row[0], row[1], row[2]
            else:
                last_query = -1, -1, None
        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()
        return last_query
    
    @classmethod
    def insert_query_totals(cls, db, url, query, total_results):

        conn = cls.get_connection()
        cursor = conn.cursor()
        try:
            last_id, _, _ = cls.get_query_totals(db)
            if last_id == -1 :
                cursor.execute("""
                    INSERT INTO Query_total_results (db, timestamp, url, query, total_results, id_trial)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (db, datetime.now(), url, query, total_results, TRIAL))
                conn.commit()
                last_id = cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()
        return last_id

    @classmethod
    def get_query_terms(cls, trial):
        conn = cls.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT query FROM TRIAL WHERE id = ?", (trial,))
            query = cursor.fetchone()[0]
            return query
        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def upsert_issue_query(cls, values, id_issues, trial):

        conn = cls.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT 1 FROM Issues_query WHERE id_issues = ? AND id_trial = ?", (id_issues, trial))
            exists = cursor.fetchone()

            if exists:
                set_clause = ", ".join([f"{field} = ?" for field, _ in values])
                update_values = [value for _, value in values] + [id_issues, trial]
                query = f"UPDATE Issues_query SET {set_clause} WHERE id_issues = ? AND id_trial = ?"
                cursor.execute(query, update_values )
            else:
                fields = [field for field, _ in values]
                insert_values = [value for _, value in values]
                placeholders = ", ".join(["?"] * len(fields))
                query = f"INSERT INTO Issues_query ({', '.join(fields)}) VALUES ({placeholders})"
                cursor.execute(query, insert_values)

            conn.commit()
        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()
    @classmethod
    def get_issues_queries(cls, trial, num_records):
        try:
            # Create connection with proper error handling
            try:
                conn = cls.get_connection()
                cursor = conn.cursor()
                print(f"Successfully connected to database: {CONNECTION_STRING}")
            except sqlite3.Error as e:
                print(f"Failed to connect to database: {e}")
                raise

            # Query using SQLite syntax (LIMIT instead of TOP)
            query = """
            SELECT 
                iss.doi,
                iss.db,
                iss.title,
                iss.abstract,
                iss.keywords,
                iss.venue,
                iss.date
            FROM ISSUES_QUERY iq 
            INNER JOIN ISSUES iss ON iq.id_issues = iss.id_issues
            WHERE id_trial = ? 
                AND title IS NOT  ?
                AND abstract IS NOT  ?
                AND iss.status = 'OK'
            LIMIT ?
            """
            print(f"Executing query with trial={trial}, num_records={num_records}")

            # Execute query with proper parameter handling
            cursor.execute(query, (trial, None, None, num_records))
            records = cursor.fetchall()
            print(f"Retrieved {len(records)} records")

            # Process records
            records_t = []
            for record in records:
                cleaned_title = BeautifulSoup(record[2], "html.parser").get_text().replace('\n', ' ')
                cleaned_abstract = BeautifulSoup(record[3], "html.parser").get_text().replace('\n', ' ')
                records_t.append([record[0], record[1], cleaned_title, cleaned_abstract, record[4], record[5], record[6]])

            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(records_t, columns=columns)
            return df

        except Exception as e:
            print(f"Error in get_issues_queries: {str(e)}")
            raise
        finally:
            if 'conn' in locals() and conn is not None:
                conn.close()


