import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('Backend-motos/.env')

def migrate_professional_features():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        cur = conn.cursor()
        print("INFO: Iniciando migración profesional (Costos, Entregas y Repuestos Utilizados)...")

        # Add columns to service table
        cur.execute("""
            ALTER TABLE service 
            ADD COLUMN IF NOT EXISTS delivery_date TIMESTAMP,
            ADD COLUMN IF NOT EXISTS labor_cost FLOAT DEFAULT 0.0,
            ADD COLUMN IF NOT EXISTS parts_cost FLOAT DEFAULT 0.0,
            ADD COLUMN IF NOT EXISTS total_cost FLOAT DEFAULT 0.0;
        """)

        # Create service_part table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS service_part (
                id SERIAL PRIMARY KEY,
                service_id INTEGER REFERENCES service(id) ON DELETE CASCADE,
                part_id INTEGER REFERENCES part(id),
                quantity INTEGER DEFAULT 1,
                unit_price FLOAT NOT NULL,
                subtotal FLOAT NOT NULL
            );
        """)

        conn.commit()
        print("SUCCESS: Migración profesional completada exitosamente.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    migrate_professional_features()
