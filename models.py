from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Mechanic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True)
    username = db.Column(db.String(50), unique=True, nullable=True)
    password = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'specialty': self.specialty,
            'phone': self.phone,
            'email': self.email,
            'is_active': self.is_active,
            'username': self.username
        }

class Part(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=True) # Added model compatibility
    price = db.Column(db.Float, default=0.0)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'model': self.model,
            'price': self.price,
            'stock': self.stock,
            'category': self.category
        }

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_name = db.Column(db.String(100), nullable=False)
    bike_model = db.Column(db.String(100), nullable=False)
    plate_number = db.Column(db.String(20))
    issue_description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pendiente')
    entry_date = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_date = db.Column(db.DateTime, nullable=True)
    labor_cost = db.Column(db.Float, default=0.0)
    parts_cost = db.Column(db.Float, default=0.0)
    total_cost = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expected_delivery = db.Column(db.DateTime, nullable=True)
    mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanic.id'), nullable=True)
    
    mechanic = db.relationship('Mechanic', backref=db.backref('services', lazy=True))
    parts_used = db.relationship('ServicePart', backref='service', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'owner_name': self.owner_name,
            'bike_model': self.bike_model,
            'plate_number': self.plate_number,
            'issue_description': self.issue_description,
            'status': self.status,
            'entry_date': self.entry_date.strftime("%d/%m/%Y"),
            'delivery_date': self.delivery_date.strftime("%d/%m/%Y") if self.delivery_date else None,
            'labor_cost': self.labor_cost,
            'parts_cost': self.parts_cost,
            'total_cost': self.total_cost,
            'mechanic_name': self.mechanic.name if self.mechanic else "Sin asignar",
            'created_at': self.created_at.strftime("%d/%m/%Y %H:%M"),
            'expected_delivery': self.expected_delivery.strftime("%d/%m/%Y") if self.expected_delivery else None,
            'parts_list': [p.to_dict() for p in self.parts_used]
        }

class ServicePart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    part = db.relationship('Part')

    def to_dict(self):
        return {
            'id': self.id,
            'part_name': self.part.name if self.part else "Repuesto eliminado",
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'subtotal': self.subtotal
        }
class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), default="Mostrador")
    total_amount = db.Column(db.Float, default=0.0)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('SaleItem', backref='sale', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'total_amount': self.total_amount,
            'sale_date': self.sale_date.strftime("%d/%m/%Y %H:%M"),
            'items': [i.to_dict() for i in self.items]
        }

class SaleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    part = db.relationship('Part')

    def to_dict(self):
        return {
            'id': self.id,
            'part_name': self.part.name if self.part else "Producto eliminado",
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'subtotal': self.subtotal
        }

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'created_at': self.created_at.strftime("%d/%m/%Y")
        }
