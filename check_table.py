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
    cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'service');")
    exists = cur.fetchone()[0]
    print(f"RESULT: table_exists={exists}")
    
    if not exists:
        print("INFO: Intentando crear tabla manualmente...")
        from main import app
        from models import db
        with app.app_context():
            db.create_all()
        print("SUCCESS: Tablas creadas.")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
