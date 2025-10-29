from db import get_db_connection

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS countries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            capital VARCHAR(255),
            region VARCHAR(255),
            population BIGINT NOT NULL,
            currency_code VARCHAR(10),
            exchange_rate FLOAT,
            estimated_gdp DOUBLE,
            flag_url TEXT,
            last_refreshed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
