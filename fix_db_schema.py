import os
from flask import Flask
from models import db, Mechanic, Part, Service, Sale, SaleItem, Client
from sqlalchemy import text

app = Flask(__name__)
DB_USER = os.getenv('DB_USER', 'taller_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Moto2026*')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'taller_motos_db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def fix_schema():
    with app.app_context():
        # Check and add created_at to models
        tables = ['mechanic', 'part', 'service']
        for table in tables:
            try:
                db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
                db.session.commit()
                print(f"Added created_at to {table}")
            except Exception as e:
                db.session.rollback()
                print(f"Column created_at already exists or error in {table}: {e}")
        
        # Add expected_delivery to service
        try:
            db.session.execute(text("ALTER TABLE service ADD COLUMN expected_delivery TIMESTAMP"))
            db.session.commit()
            print("Added expected_delivery to service")
        except Exception as e:
            db.session.rollback()
            print(f"Column expected_delivery already exists or error: {e}")

        # Create Client table if not exists (db.create_all handles new tables better)
        db.create_all()
        print("Schema update completed.")

if __name__ == "__main__":
    fix_schema()
