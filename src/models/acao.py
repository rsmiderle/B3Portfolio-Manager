from datetime import datetime
from src.models import db

class Acao(db.Model):
    __tablename__ = 'acoes'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), nullable=False)
    cnpj = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chave estrangeira para o usuário
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relacionamentos
    negociacoes = db.relationship('Negociacao', backref='acao', lazy=True, cascade="all, delete-orphan")
    saldos = db.relationship('SaldoPrecoMedio', backref='acao', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Acao {self.codigo}>'