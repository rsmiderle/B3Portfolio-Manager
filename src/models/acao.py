from datetime import datetime
from src.models import db
from flask_login import current_user

class Acao(db.Model):
    __tablename__ = 'acoes'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), nullable=False)  # Tipo de dado otimizado
    cnpj = db.Column(db.String(18), nullable=True)  # Tipo de dado otimizado
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chave estrangeira para o usuário (anonimizada)
    user_hash = db.Column(db.String(64), db.ForeignKey('users.hash_id'), nullable=False, index=True)
    
    # Relacionamentos
    negociacoes = db.relationship('Negociacao', backref='acao', lazy=True, cascade="all, delete-orphan")
    saldos = db.relationship('SaldoPrecoMedio', backref='acao', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Acao {self.id}>'
