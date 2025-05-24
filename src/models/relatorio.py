from datetime import datetime
from src.models import db

class Relatorio(db.Model):
    __tablename__ = 'relatorios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    negociacoes = db.relationship('Negociacao', backref='relatorio', lazy=True)
    
    def __repr__(self):
        return f'<Relatorio {self.nome_arquivo}>'
