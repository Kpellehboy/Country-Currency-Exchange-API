import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection details from environment variables
HOST = os.getenv("DB_HOST")
PORT = int(os.getenv("DB_PORT"))
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASS")
DATABASE = os.getenv("DB_NAME")

def get_db_connection():
    conn = None  # Initialize conn
    cursor = None # Initialize cursor for the inner block
    
    try:
        # 1. Establish the initial connection (without specifying the database)
        conn = mysql.connector.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD
        )
        
        # 2. Use a nested try/finally to handle the temporary cursor
        try:
            cursor = conn.cursor()
        
            # Create the database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DATABASE}`")

            # Select the database for all future operations on this connection
            cursor.execute(f"USE `{DATABASE}`")
            
            # Perform a test query and print success message
            cursor.execute("SELECT NOW();")
            print("Successfully connected and database selected.")
            print("Database time:", cursor.fetchone()[0]) # [0] to get the single value
            
        finally:
            # CRITICAL: Always close the temporary cursor
            if cursor:
                cursor.close()

        # 3. Return the successfully connected and selected connection object
        return conn

    except mysql.connector.Error as e:
        print("Connection failed:", e)
        # CRITICAL: If connection failed, ensure we attempt to close it
        if conn:
            conn.close()
        return None