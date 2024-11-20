import pyodbc
from datetime import datetime



def connect_to_db():
    try:
        connection = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=pchc3112a-04\\SQLEXPRESS;'
            'DATABASE=MultiplatformXR;'
            'Trusted_Connection=yes;'
        )
        return connection
    except pyodbc.Error as e:
        print("Error in connection:", e)
        return None


# Function to insert title and doi
def insert_data_query(query: str, page_count: str, url: str, timestamp : datetime, db: str ,connection) -> int:
    if connection:
        cursor = connection.cursor()
        try:
            # Insert the new record into query_status
            cursor.execute("""
                INSERT INTO query_status (Query, Page_count, Url, Time_stamp, DB)
                OUTPUT INSERTED.Id
                VALUES (?, ?, ?, ?, ?)
            """, (query, page_count, url, timestamp, db))
            
            # Retrieve the auto-incremented Id of the inserted row
            #   cursor.execute("SELECT SCOPE_IDENTITY()")
            query_id = cursor.fetchone()[0]
            
            # Commit the transaction
            connection.commit()
            
            # Return the auto-incremented Id
            return int(query_id)

        except pyodbc.Error as e:
            print("Error inserting query data:", e)
            connection.rollback()
            return -1  # Return a negative number to indicate an error

        finally:
            cursor.close()
    else:
        print("Failed to connect to the database")
        return -1  # Return a negative number if connection fails


# Function to insert title and doi
def insert_data_issue(title: str, doi: str, type: str, date_str: str, date_day : int, date_month: str, date_year: int, id_query: int, db : str, connection):
    if connection:
        cursor = connection.cursor()
        try:

            # Check if an entry with the same Issue_doi already exists
            cursor.execute("SELECT doi FROM Issues WHERE Doi = ?", (doi,))
            existing_record = cursor.fetchone()

            if existing_record:
                # If record exists, update the Comments field
                cursor.execute("""
                    UPDATE Issues 
                    SET Comments = CONCAT(COALESCE(Comments, ''), ' Found again in query with id ', ?)
                    WHERE Issue_doi = ?
                """, (id_query, doi))
                print(f"Record with DOI '{doi}' found, updating Comments field.")
            else:
                # Prepare and execute the insert statement
                cursor.execute("""
                    INSERT INTO Issues (
                                        [Title]
                                        ,[Doi]
                                        ,[Type]
                                        ,[Date]
                                        ,[Date_day]
                                        ,[Date_month]
                                        ,[Date_year]
                                        ,[Id_query]
                                        ,[DB])
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (title, doi, type, date_str, date_day, date_month, date_year, id_query, db))
                # Commit the transaction
                connection.commit()
                #print("Data inserted successfully")
        except pyodbc.Error as e:
            print("Error inserting data: ", title , '--' ,e)
            connection.rollback()
        finally:
            # Close the connection
            cursor.close()
            #connection.close()
    else:
        print("Failed to connect to the database")


def update_data_issue(field_value_pairs, doi, connection):
    """
    Update fields in the Issues table for a given DOI.

    Parameters:
        field_value_pairs (list of tuple): List of (field_name, new_value) pairs.
        doi (str): DOI of the row to update.
        connection: Database connection object.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    if not field_value_pairs:
        print("No fields provided to update.")
        return False

    if connection:
        cursor = connection.cursor()
        try:
            # Create the SET clause dynamically
            set_clause = ", ".join([f"{field_name} = ?" for field_name, _ in field_value_pairs])
            values = [value for _, value in field_value_pairs]

            # Add the DOI to the values list for the WHERE clause
            values.append(doi)

            # Prepare and execute the update statement
            query = f"UPDATE Issues SET {set_clause} WHERE Doi = ?"
            print(f'UPDATING... {doi} \n\t\t\t {query}')
            cursor.execute(query, values)

            # Commit the transaction
            connection.commit()
            return True

        except Exception as e:
            print("Error updating data:", e)
            connection.rollback()
            return False

        finally:
            cursor.close()
    else:
        print("Failed to connect to the database.")
        return False


def get_number_issues_uncomplete(connection, db) ->int:
    cursor = connection.cursor()
    if connection:
        cursor = connection.cursor()
        try:
            # Query to count rows where Abstract is NULL
            query = "SELECT COUNT(*) FROM Issues WHERE Abstract IS NULL AND DB = ?"
            cursor.execute(query, db)
            result = cursor.fetchone()

            # Return the count (first column of the result)
            return result[0] if result else 0
        except pyodbc.Error as e:
            print("Error querying database:", e)
            return -1  # Return -1 to indicate an error
        finally:
            cursor.close()
    else:
        print("Database connection is not available.")
        return -1
    
def get_uncompleted_issues_dois(connection, db) -> list:
    """
    Get a list of DOIs for issues where the Abstract field is NULL.

    Parameters:
        connection: Database connection object.

    Returns:
        list: List of DOIs where Abstract is NULL, or an empty list if an error occurs.
    """
    if connection:
        cursor = connection.cursor()
        try:
            # Query to fetch DOIs where Abstract is NULL
            query = "SELECT doi FROM Issues WHERE Abstract IS NULL AND DB = ? "
            cursor.execute(query,db)
            result = cursor.fetchall()

            # Extract DOIs from the result
            return [row[0] for row in result] if result else []
        except pyodbc.Error as e:
            print("Error querying database:", e)
            return []  # Return an empty list on error
        finally:
            cursor.close()
    else:
        print("Database connection is not available.")
        return []
