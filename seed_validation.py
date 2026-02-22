import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

def seed_data():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        cur = conn.cursor()
        
        print("INFO: Limpiando datos previos de prueba...")
        cur.execute("DELETE FROM service WHERE owner_name LIKE 'TEST%';")
        cur.execute("DELETE FROM mechanic WHERE name LIKE 'TEST%';")
        
        # 1. Create Test Mechanics
        print("INFO: Creando mecánicos de prueba...")
        mechanics = [
            ('TEST: Carlos Pérez', 'Motores de Carrera', '+57 300 111 2222', 'CP', '1234'),
            ('TEST: Ana Sánchez', 'Electrónica Avanzada', '+57 300 333 4444', 'AS', '1234')
        ]
        
        mech_ids = []
        for name, spec, phone, user, pw in mechanics:
            cur.execute("""
                INSERT INTO mechanic (name, specialty, phone, username, password, is_active) 
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            """, (name, spec, phone, user, pw, True))
            mech_ids.append(cur.fetchone()[0])
            
        # 2. Create Test Services (assigned to mechanics)
        print("INFO: Creando servicios vinculados...")
        services = [
            ('TEST Alex', 'Yamaha R6', 'YAM-06R', 'Ajuste de válvulas y sincronización', 'Completado', mech_ids[0]),
            ('TEST Sofia', 'Honda CBR 1000', 'HND-100', 'Cambio de kit de arrastre', 'Pendiente', mech_ids[0]),
            ('TEST Mateo', 'BMW S1000RR', 'BMW-RRR', 'Falla en sensor de inclinación', 'En Reparación', mech_ids[1])
        ]
        
        for owner, bike, plate, desc, status, m_id in services:
            cur.execute("""
                INSERT INTO service (owner_name, bike_model, plate_number, issue_description, status, mechanic_id, entry_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (owner, bike, plate, desc, status, m_id, datetime.utcnow()))
            
        # 3. Create Test Parts
        print("INFO: Cargando repuestos de prueba...")
        parts = [
            ('Filtro de Aceite K&N', 'Yamaha', 45.50, 15, 'Repuesto'),
            ('Pastillas de Freno Brembo', 'Brembo', 85.00, 8, 'Frenos'),
            ('Cadena Reforzada DID', 'DID', 120.00, 3, 'Transmisión')
        ]
        
        for name, brand, price, stock, cat in parts:
            cur.execute("INSERT INTO part (name, brand, price, stock, category) VALUES (%s, %s, %s, %s, %s)", (name, brand, price, stock, cat))
            
        conn.commit()
        print("SUCCESS: Base de datos poblada con éxito. Puedes validar los perfiles de Carlos y Ana.")
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    seed_data()
