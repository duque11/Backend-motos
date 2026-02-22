import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('Backend-motos/.env')

def migrate():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        cur = conn.cursor()
        print("INFO: Iniciando migración de base de datos...")
        
        # Add columns
        cur.execute("ALTER TABLE mechanic ADD COLUMN IF NOT EXISTS username VARCHAR(50) UNIQUE;")
        cur.execute("ALTER TABLE mechanic ADD COLUMN IF NOT EXISTS password VARCHAR(100);")
        cur.execute("ALTER TABLE service ADD COLUMN IF NOT EXISTS mechanic_id INTEGER REFERENCES mechanic(id);")
        
        conn.commit()
        print("SUCCESS: Columnas 'username', 'password' y 'mechanic_id' agregadas con éxito.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    migrate()
