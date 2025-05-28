from datetime import datetime
from src.models import db
from flask_login import current_user

class Relatorio(db.Model):
    __tablename__ = 'relatorios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_arquivo = db.Column(db.String(255), nullable=False)  # Tipo de dado otimizado
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chave estrangeira para o usuário (anonimizada)
    user_hash = db.Column(db.String(64), db.ForeignKey('users.hash_id'), nullable=False, index=True)
    
    # Relacionamentos
    negociacoes = db.relationship('Negociacao', backref='relatorio', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Relatorio {self.id}>'
