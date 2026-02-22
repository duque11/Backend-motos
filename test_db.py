import os
import psycopg2
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"INFO: .env cargado desde {env_path}")
else:
    print(f"ERROR: No se encontro el archivo .env en {env_path}")

try:
    dbname = os.getenv('DB_NAME')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')

    print(f"INFO: Intentando conectar a: {dbname} en {host}:{port} con usuario {user}...")
    
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    print("SUCCESS: Conexion exitosa a PostgreSQL!")
    
    cur = conn.cursor()
    cur.execute("SELECT version();")
    record = cur.fetchone()
    print(f"INFO: Version del servidor: {record}")
    
    cur.close()
    conn.close()
    print("INFO: Conexion cerrada correctamente.")

except Exception as error:
    print(f"ERROR de conexion: {error}")
