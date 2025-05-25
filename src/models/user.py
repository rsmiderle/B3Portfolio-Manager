from datetime import datetime
from flask_login import UserMixin
from src.models import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    profile_pic = db.Column(db.String(200), nullable=True)
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    relatorios = db.relationship('Relatorio', backref='user', lazy=True, cascade="all, delete-orphan")
    acoes = db.relationship('Acao', backref='user', lazy=True, cascade="all, delete-orphan")
    saldos = db.relationship('SaldoPrecoMedio', backref='user', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<User {self.email}>'
