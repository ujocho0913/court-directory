import streamlit as st
import pandas as pd
import psycopg2
from psycopg2 import pool, sql, OperationalError
from psycopg2.extras import RealDictCursor

# Define get_database_session() 
@st.cache_resource
def get_database_session(database_url):
    try: 
        # Create a database session object that points to the URL.
        return pool.SimpleConnectionPool(1, 10, database_url) # Initialize connection pool
    except OperationalError as e:
        st.error("Network is blocking connection to the database server. Please try again on a different network/internet connection, and reach out to admin at ujcho@jacksongov.org")
        return None
    

# Define get_apa_data()
@st.cache_data
def get_apa_data(_connection_pool):
    # --- Collect APA data --- 

    with _connection_pool.getconn() as conn:

        # Open cursor to perform database operations
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                query = sql.SQL("SELECT * FROM employee_info_view WHERE {where_col} IN (%s, %s, %s, %s) ORDER BY {order_col}").format(
                    where_col=sql.Identifier('Position'),
                    order_col=sql.Identifier('Last Name')
                )

                cur.execute(query, ['Exec', 'CTA', 'TTL', 'APA']) # I - Investigator, VA - Victim Advocate, INTERN - intern
            except psycopg2.Error as e:
                st.error(f"Problem with loading data: {e}")
            else:
                results = cur.fetchall()
                df = pd.DataFrame(results)
                return df

        cur.close()
    conn.close()

# Define fetch_list()
@st.cache_data
def fetch_list(df, col_name):
    """Fetch a column to return as list"""
    try:
        output = df[col_name].tolist() # [row[col_name] for row in df]
    except KeyError as e:
        return []
    else:
        return output
    
# Define external_log_activity()
def external_log_activity(_connection_pool, db_table_name, user_email, user_ip): # police_log, courts_log 

    with _connection_pool.getconn() as conn:

        with conn.cursor() as cur:
            try: 
                query = sql.SQL("INSERT INTO {table_name} (user_email, user_ip) VALUES (%s, %s)").format(
                    table_name=sql.Identifier(db_table_name)
                )
                cur.execute(query, (user_email, user_ip))
            except psycopg2.Error as e:
                st.error(f"An error has occurred.")
            else:
                conn.commit()
        cur.close()
    conn.close()