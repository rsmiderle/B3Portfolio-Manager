from datetime import datetime
from src.models import db

class SaldoPrecoMedio(db.Model):
    __tablename__ = 'saldos_precos_medios'
    
    id = db.Column(db.Integer, primary_key=True)
    data_base = db.Column(db.Date, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_medio = db.Column(db.Float, nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chave estrangeira
    acao_id = db.Column(db.Integer, db.ForeignKey('acoes.id'), nullable=False)
    
    # Índice composto para garantir unicidade de ação por data base
    __table_args__ = (
        db.UniqueConstraint('acao_id', 'data_base', name='uix_acao_data_base'),
    )
    
    def __repr__(self):
        return f'<SaldoPrecoMedio {self.acao_id} {self.data_base}>'
