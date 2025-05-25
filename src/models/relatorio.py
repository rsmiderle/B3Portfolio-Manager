from datetime import datetime
from src.models import db

class Relatorio(db.Model):
    __tablename__ = 'relatorios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_arquivo = db.Column(db.String(100), nullable=False)
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chave estrangeira para o usuário
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relacionamentos
    negociacoes = db.relationship('Negociacao', backref='relatorio', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Relatorio {self.nome_arquivo}>'