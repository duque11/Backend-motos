import os
from flask import Flask
from models import db
from sqlalchemy import text

app = Flask(__name__)
DB_USER = os.getenv('DB_USER', 'taller_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', '') # No default for security
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'taller_motos_db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def add_indexes():
    with app.app_context():
        # List of indexes to add
        sqls = [
            "CREATE INDEX IF NOT EXISTS idx_service_plate ON service (plate_number)",
            "CREATE INDEX IF NOT EXISTS idx_service_entry ON service (entry_date)",
            "CREATE INDEX IF NOT EXISTS idx_part_name ON part (name)",
            "CREATE INDEX IF NOT EXISTS idx_client_name ON client (name)",
            "CREATE INDEX IF NOT EXISTS idx_client_phone ON client (phone)"
        ]
        for sql in sqls:
            try:
                db.session.execute(text(sql))
                db.session.commit()
                print(f"Executed: {sql}")
            except Exception as e:
                db.session.rollback()
                print(f"Error executing {sql}: {e}")
        print("Indexing completed.")

if __name__ == "__main__":
    add_indexes()
