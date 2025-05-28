from datetime import datetime
from src.models import db
from flask_login import current_user

class SaldoPrecoMedio(db.Model):
    __tablename__ = 'saldos_precos_medios'
    
    id = db.Column(db.Integer, primary_key=True)
    data_base = db.Column(db.Date, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)  # Tipo de dado otimizado
    preco_medio = db.Column(db.Numeric(10, 2), nullable=False)  # Numeric para precisão monetária
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chaves estrangeiras
    acao_id = db.Column(db.Integer, db.ForeignKey('acoes.id'), nullable=False)
    user_hash = db.Column(db.String(64), db.ForeignKey('users.hash_id'), nullable=False, index=True)  # Referência anonimizada
    
    # Comentário: Imposto para garantir unicidade de ação por data base
    __table_args__ = (
        db.UniqueConstraint('acao_id', 'data_base', name='uix_acao_data_base'),
    )
    
    def __repr__(self):
        return f'<SaldoPrecoMedio {self.acao_id} {self.data_base}>'
