from datetime import datetime
from src.models import db

class Acao(db.Model):
    __tablename__ = 'acoes'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(10), unique=True, nullable=False)
    cnpj = db.Column(db.String(18), nullable=True)
    nome_empresa = db.Column(db.String(100), nullable=True)
    
    # Relacionamentos
    negociacoes = db.relationship('Negociacao', backref='acao', lazy=True)
    saldos = db.relationship('SaldoPrecoMedio', backref='acao', lazy=True)
    
    def __repr__(self):
        return f'<Acao {self.codigo}>'
