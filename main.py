import os
import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, Service, Mechanic, Part, ServicePart, Sale, SaleItem, Client
from datetime import datetime, timedelta
from dotenv import load_dotenv
from functools import wraps
import smtplib, ssl, threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables (from absolute path to avoid issues)
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Absolute paths for cross-platform compatibility
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app)

# Database Configuration (PostgreSQL)
DB_USER = os.getenv('DB_USER', 'taller_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Moto2026*')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'taller_motos_db')
JWT_SECRET = os.getenv('JWT_SECRET', 'super-secret-key-motos-2026')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# SMTP Config
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 465))
SMTP_USER = os.getenv('SMTP_USER', 'tallerdukepro@gmail.com')
SMTP_PASS = os.getenv('SMTP_PASS', '') # User needs to provide this

def send_welcome_email(mechanic_data):
    if not mechanic_data.get('email'):
        print("Skipping email: No email address provided for mechanic.")
        return
        
    if not SMTP_PASS:
        print("⚠️ Email NOT sent: SMTP_PASS is missing in environment variables.")
        return

    print(f"📧 Attempting to send welcome email to {mechanic_data['email']}...")
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = mechanic_data['email']
        msg['Subject'] = f"🏁 Bienvenido a Taller Duke - {mechanic_data['name']}"

        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
            <h1 style="color: #6366f1;">¡Bienvenido al Equipo! 🏍️</h1>
            <p>Hola <strong>{mechanic_data['name']}</strong>,</p>
            <p>Estamos emocionados de tenerte en <strong>Taller Duke</strong> como <em>{mechanic_data['specialty']}</em>.</p>
            <div style="background: #f4f4f4; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p style="margin: 0;"><strong>Tus credenciales de acceso:</strong></p>
                <p style="margin: 5px 0;">Usuario: <code>{mechanic_data['username']}</code></p>
                <p style="margin: 5px 0;">Contraseña inicial: <code>1234</code></p>
            </div>
            <p>Ya puedes ingresar a la plataforma para gestionar tus servicios.</p>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="font-size: 12px; color: #777;">Taller Duke ERP - Sistema de Gestión Profesional</p>
        </div>
        """
        msg.attach(MIMEText(html, 'html'))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, mechanic_data['email'], msg.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")

# Authentication Decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            # Token usually comes as "Bearer <token>"
            if "Bearer " in token:
                token = token.split(" ")[1]
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except Exception as e:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        return f(*args, **kwargs)
    return decorated

@app.before_request
def create_tables():
    app.before_request_funcs[None].remove(create_tables)
    db.create_all()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Specific credentials requested by user (Admin)
    if username == "BADV" and password == "salva123":
        token = jwt.encode({
            'user': username,
            'role': 'admin',
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, JWT_SECRET, algorithm="HS256")
        return jsonify({'token': token, 'user': 'Bryan Duque', 'role': 'admin'})
    
    # Check if it's a mechanic login (username = IS)
    mechanic = Mechanic.query.filter_by(username=username).first()
    if mechanic and mechanic.password == password:
        token = jwt.encode({
            'user': username,
            'role': 'mechanic',
            'id': mechanic.id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, JWT_SECRET, algorithm="HS256")
        return jsonify({'token': token, 'user': mechanic.name, 'role': 'mechanic', 'id': mechanic.id})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/mechanics', methods=['GET'])
@token_required
def get_mechanics():
    mechanics = Mechanic.query.all()
    return jsonify([m.to_dict() for m in mechanics])

@app.route('/api/mechanics', methods=['POST'])
@token_required
def add_mechanic():
    data = request.json
    new_mechanic = Mechanic(
        name=data.get('name'),
        specialty=data.get('specialty'),
        phone=data.get('phone'),
        email=data.get('email'),
        username=data.get('username'), # This is the IS
        password=data.get('password', '1234') # Default password if not provided
    )
    db.session.add(new_mechanic)
    db.session.commit()
    
    # Send email in background
    mech_dict = new_mechanic.to_dict()
    threading.Thread(target=send_welcome_email, args=(mech_dict,)).start()
    
    return jsonify(mech_dict), 201

@app.route('/api/mechanics/<int:id>', methods=['PATCH'])
@token_required
def update_mechanic(id):
    data = request.json
    mechanic = Mechanic.query.get_or_404(id)
    if 'name' in data: mechanic.name = data['name']
    if 'specialty' in data: mechanic.specialty = data['specialty']
    if 'phone' in data: mechanic.phone = data['phone']
    if 'email' in data: mechanic.email = data['email']
    if 'username' in data: mechanic.username = data['username']
    if 'password' in data: mechanic.password = data['password']
    if 'is_active' in data: mechanic.is_active = data['is_active']
    db.session.commit()
    return jsonify(mechanic.to_dict())

@app.route('/api/mechanics/<int:id>', methods=['DELETE'])
@token_required
def delete_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({'message': 'Mechanic deleted'})

@app.route('/api/parts', methods=['GET'])
@token_required
def get_parts():
    parts = Part.query.order_by(Part.brand).all()
    return jsonify([p.to_dict() for p in parts])

@app.route('/api/parts', methods=['POST'])
@token_required
def add_part():
    data = request.json
    new_part = Part(
        name=data.get('name'),
        brand=data.get('brand'),
        price=data.get('price', 0),
        stock=data.get('stock', 0),
        category=data.get('category')
    )
    db.session.add(new_part)
    db.session.commit()
    return jsonify(new_part.to_dict()), 201

@app.route('/api/parts/<int:id>', methods=['PATCH'])
@token_required
def update_part(id):
    data = request.json
    part = Part.query.get_or_404(id)
    if 'name' in data: part.name = data['name']
    if 'brand' in data: part.brand = data['brand']
    if 'model' in data: part.model = data['model']
    if 'category' in data: part.category = data['category']
    if 'stock' in data: part.stock = data['stock']
    if 'price' in data: part.price = data['price']
    db.session.commit()
    return jsonify(part.to_dict())

@app.route('/api/parts/search', methods=['GET'])
@token_required
def search_parts():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    parts = Part.query.filter(
        (Part.name.ilike(f'%{query}%')) | 
        (Part.model.ilike(f'%{query}%'))
    ).limit(20).all()
    return jsonify([p.to_dict() for p in parts])

@app.route('/api/services', methods=['GET'])
@token_required
def get_services():
    services = Service.query.order_by(Service.entry_date.desc()).all()
    
    total_count = len(services)
    pending = len([s for s in services if s.status == 'Pendiente'])
    completed = len([s for s in services if s.status == 'Completado' or s.status == 'Entregado'])
    in_progress = total_count - pending - completed

    # Calculate revenue for current month
    now = datetime.utcnow()
    try:
        month_services = Service.query.filter(
            db.func.extract('month', Service.entry_date) == now.month,
            db.func.extract('year', Service.entry_date) == now.year
        ).all()
        
        revenue = {
            'labor': sum(s.labor_cost for s in month_services),
            'parts': sum(s.parts_cost for s in month_services),
            'total': sum(s.total_cost for s in month_services)
        }
    except Exception as e:
        print(f"Error calculating revenue: {e}")
        revenue = {'labor': 0, 'parts': 0, 'total': 0}

    return jsonify({
        'services': [s.to_dict() for s in services],
        'stats': {
            'total': total_count,
            'pending': pending,
            'completed': completed,
            'in_progress': in_progress
        },
        'revenue': revenue
    })

@app.route('/api/services', methods=['POST'])
@token_required
def add_service():
    data = request.json
    if not data:
        return jsonify({'error': 'No data received'}), 400
    
    new_service = Service(
        owner_name=data.get('ownerName'),
        bike_model=data.get('bikeModel'),
        plate_number=data.get('plateNumber'),
        issue_description=data.get('issueDescription'),
        status=data.get('status', 'Pendiente'),
        mechanic_id=data.get('mechanicId'),
        labor_cost=data.get('laborCost', 0.0),
        total_cost=data.get('laborCost', 0.0)
    )
    db.session.add(new_service)
    db.session.commit()
    return jsonify(new_service.to_dict()), 201

@app.route('/api/services/<int:id>/costs', methods=['PATCH'])
@token_required
def update_service_costs(id):
    data = request.json
    service = Service.query.get_or_404(id)
    if 'labor_cost' in data:
        service.labor_cost = data['labor_cost']
    
    # Recalculate totals
    service.total_cost = service.labor_cost + service.parts_cost
    db.session.commit()
    return jsonify(service.to_dict())

@app.route('/api/services/<int:id>/status', methods=['PATCH'])
@token_required
def update_status(id):
    data = request.json
    service = Service.query.get_or_404(id)
    service.status = data.get('status')
    if service.status == 'Entregado':
        service.delivery_date = datetime.utcnow()
    db.session.commit()
    return jsonify(service.to_dict())

@app.route('/api/services/<int:service_id>/parts', methods=['POST'])
@token_required
def add_part_to_service(service_id):
    data = request.json
    service = Service.query.get_or_404(service_id)
    part = Part.query.get_or_404(data.get('partId'))
    qty = data.get('quantity', 1)

    if part.stock < qty:
        return jsonify({'error': 'Stock insuficiente'}), 400

    # Create linkage
    subtotal = part.price * qty
    service_part = ServicePart(
        service_id=service.id,
        part_id=part.id,
        quantity=qty,
        unit_price=part.price,
        subtotal=subtotal
    )
    
    # Update costs
    service.parts_cost += subtotal
    service.total_cost = service.labor_cost + service.parts_cost
    
    # Reduce inventory stock automatically
    part.stock -= qty
    
    db.session.add(service_part)
    db.session.commit()
    
    return jsonify(service.to_dict())

@app.route('/api/services/<int:service_id>/parts/<int:link_id>', methods=['DELETE'])
@token_required
def remove_part_from_service(service_id, link_id):
    service = Service.query.get_or_404(service_id)
    link = ServicePart.query.get_or_404(link_id)
    
    # Revert stock
    part = Part.query.get(link.part_id)
    if part:
        part.stock += link.quantity
    
    # Update costs
    service.parts_cost -= link.subtotal
    service.total_cost = service.labor_cost + service.parts_cost
    
    db.session.delete(link)
    db.session.commit()
    return jsonify(service.to_dict())

@app.route('/api/services/<int:id>', methods=['DELETE'])
@token_required
def delete_service(id):
    service = Service.query.get_or_404(id)
    # Revert all parts stock if service is deleted
    for sp in service.parts_used:
        p = Part.query.get(sp.part_id)
        if p:
            p.stock += sp.quantity
            
    db.session.delete(service)
    db.session.commit()
    return jsonify({'message': 'Service deleted successfully'})

@app.route('/api/mechanics/<int:id>/services', methods=['GET'])
@token_required
def get_mechanic_services(id):
    mechanic = Mechanic.query.get_or_404(id)
    services = Service.query.filter_by(mechanic_id=id).order_by(Service.entry_date.desc()).all()
    
    # Calculate performance stats
    stats = {
        'total_jobs': len(services),
        'completed_jobs': len([s for s in services if s.status == 'Completado' or s.status == 'Entregado']),
        'pending_jobs': len([s for s in services if s.status == 'Pendiente']),
        'total_labor': sum([s.labor_cost for s in services if s.status in ['Completado', 'Entregado']])
    }
    
    return jsonify({
        'mechanic': mechanic.to_dict(),
        'services': [s.to_dict() for s in services],
        'stats': stats
    })

# --- Direct Sales (POS) Endpoints ---

@app.route('/api/sales', methods=['POST'])
@token_required
def create_direct_sale():
    data = request.json
    items_data = data.get('items', [])
    customer = data.get('customerName', 'Mostrador')
    
    if not items_data:
        return jsonify({'error': 'El carrito está vacío'}), 400
        
    try:
        new_sale = Sale(customer_name=customer, total_amount=0.0)
        db.session.add(new_sale)
        db.session.flush() # Get ID
        
        total = 0.0
        for item in items_data:
            part = Part.query.get(item['id'])
            qty = int(item.get('qty', 1))
            
            if not part:
                db.session.rollback()
                return jsonify({'error': f'Producto no encontrado (ID {item.get("id")})'}), 404
                
            if part.stock < qty:
                db.session.rollback()
                return jsonify({'error': f'Stock insuficiente para {part.name} (Disponible: {part.stock})'}), 400
                
            subtotal = part.price * qty
            sale_item = SaleItem(
                sale_id=new_sale.id,
                part_id=part.id,
                quantity=qty,
                unit_price=part.price,
                subtotal=subtotal
            )
            total += subtotal
            part.stock -= qty
            db.session.add(sale_item)
            
        new_sale.total_amount = total
        db.session.commit()
        return jsonify(new_sale.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/sales', methods=['GET'])
@token_required
def get_sales_history():
    sales = Sale.query.order_by(Sale.sale_date.desc()).all()
    return jsonify([s.to_dict() for s in sales])

# --- Reports & History Endpoints ---

@app.route('/api/reports/revenue', methods=['GET'])
@token_required
def get_revenue_report():
    # Last 6 months revenue
    now = datetime.utcnow()
    report = []
    for i in range(6):
        month_start = (now.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        
        services = Service.query.filter(Service.entry_date >= month_start, Service.entry_date < month_end).all()
        sales = Sale.query.filter(Sale.sale_date >= month_start, Sale.sale_date < month_end).all()
        
        total_revenue = sum(s.total_cost for s in services) + sum(s.total_amount for s in sales)
        
        report.append({
            'month': month_start.strftime("%b %Y"),
            'revenue': total_revenue,
            'services': len(services),
            'sales': len(sales)
        })
    
    return jsonify(report[::-1])

@app.route('/api/history/search', methods=['GET'])
@token_required
def search_history():
    plate = request.args.get('plate', '').upper()
    if not plate:
        return jsonify([])
    services = Service.query.filter(Service.plate_number.ilike(f'%{plate}%')).order_by(Service.entry_date.desc()).all()
    return jsonify([s.to_dict() for s in services])

# --- Public Status Endpoint (No Token Required) ---
@app.route('/api/public/status/<plate>', methods=['GET'])
def get_public_status(plate):
    service = Service.query.filter(Service.plate_number.ilike(plate)).order_by(Service.entry_date.desc()).first()
    if not service:
        return jsonify({'error': 'No se encontró servicio activo para esta placa'}), 404
        
    return jsonify({
        'owner_name': service.owner_name,
        'bike_model': service.bike_model,
        'status': service.status,
        'entry_date': service.entry_date.strftime("%d/%m/%Y"),
        'issue': service.issue_description,
        'expected': service.expected_delivery.strftime("%d/%m/%Y") if service.expected_delivery else "Pendiente de definir"
    })

# --- Client Management ---
@app.route('/api/clients', methods=['GET'])
@token_required
def get_clients():
    clients = Client.query.all()
    return jsonify([c.to_dict() for c in clients])

@app.route('/api/clients', methods=['POST'])
@token_required
def add_client():
    data = request.json
    new_client = Client(
        name=data.get('name'),
        phone=data.get('phone'),
        email=data.get('email'),
        address=data.get('address')
    )
    db.session.add(new_client)
    db.session.commit()
    return jsonify(new_client.to_dict()), 201

if __name__ == '__main__':
    # Internal API port 8088
    print("INFO: Taller API starting on internal port 8088")
    app.run(debug=True, host='0.0.0.0', port=8088)
