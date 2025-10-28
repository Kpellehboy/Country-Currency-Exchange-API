import mariadb
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read from .env
HOST = os.getenv("DB_HOST")
PORT = int(os.getenv("DB_PORT"))
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASS")
DATABASE = os.getenv("DB_NAME")

try:
    # Connect to SkySQL
    conn = mariadb.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        ssl={'verify_server_cert': True}  # ✅ Correct way to enable SSL
    )

    print("✅ Successfully connected to SkySQL database!")

    # Test query
    cur = conn.cursor()
    cur.execute("SELECT NOW();")
    print("Database time:", cur.fetchone())

    # Close connection
    conn.close()

except mariadb.Error as e:
    print("❌ Connection failed:", e)
