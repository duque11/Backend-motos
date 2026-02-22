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
    cur.execute("SELECT COUNT(*) FROM service;")
    count = cur.fetchone()[0]
    print(f"COUNT_RESULT: {count}")
    
    if count > 0:
        cur.execute("SELECT id, owner_name, bike_model FROM service LIMIT 5;")
        rows = cur.fetchall()
        for row in rows:
            print(f"RECORD: {row}")
            
    cur.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
