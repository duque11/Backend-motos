import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('Backend-motos/.env')

def migrate_model_column():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        cur = conn.cursor()
        print("INFO: Iniciando migración para columna 'model' en tabla 'part'...")

        # Add model column if it doesn't exist
        cur.execute("""
            ALTER TABLE part 
            ADD COLUMN IF NOT EXISTS model VARCHAR(100);
        """)

        conn.commit()
        print("SUCCESS: Columna 'model' añadida exitosamente.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    migrate_model_column()
