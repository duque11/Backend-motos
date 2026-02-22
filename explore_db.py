import os
import psycopg2
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

try:
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432')
    )
    cur = conn.cursor()
    
    # List tables
    print("--- TABLAS EN LA BASE DE DATOS ---")
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public';
    """)
    tables = cur.fetchall()
    for table in tables:
        print(f"Table: {table[0]}")
        
        # List columns for each table
        cur.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = '{table[0]}';
        """)
        columns = cur.fetchall()
        for col in columns:
            null_str = "NULL" if col[2] == 'YES' else "NOT NULL"
            print(f"  -> Column: {col[0]} ({col[1]}, {null_str})")
            
    cur.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
