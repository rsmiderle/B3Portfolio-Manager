from datetime import datetime
from src.models import db
from flask_login import current_user

class Negociacao(db.Model):
    __tablename__ = 'negociacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    data_negocio = db.Column(db.Date, nullable=False)
    tipo_movimentacao = db.Column(db.String(50), nullable=False)  # Tipo de dado otimizado
    mercado = db.Column(db.String(50), nullable=False)  # Tipo de dado otimizado
    prazo_vencimento = db.Column(db.String(50), nullable=False)  # Tipo de dado otimizado
    instituicao = db.Column(db.String(100), nullable=False)  # Tipo de dado otimizado
    quantidade = db.Column(db.Integer, nullable=False)
    preco = db.Column(db.Numeric(10, 2), nullable=False)  # Numeric para precisão monetária
    valor = db.Column(db.Numeric(12, 2), nullable=False)  # Numeric para precisão monetária
    corretagem = db.Column(db.Numeric(10, 2), nullable=True)  # Numeric para precisão monetária
    
    # Chaves estrangeiras
    acao_id = db.Column(db.Integer, db.ForeignKey('acoes.id'), nullable=False)
    relatorio_id = db.Column(db.Integer, db.ForeignKey('relatorios.id'), nullable=False)
    user_hash = db.Column(db.String(64), db.ForeignKey('users.hash_id'), nullable=False, index=True)  # Referência anonimizada
    
    # Chave única composta para evitar duplicidades na importação de relatórios
    __table_args__ = (
        db.UniqueConstraint(
            'data_negocio', 'tipo_movimentacao', 'mercado', 'instituicao', 
            'acao_id', 'quantidade', 'preco', 'valor', 'user_hash',
            name='uix_negociacao_completa'
        ),
    )
    
    def __repr__(self):
        return f'<Negociacao {self.id} {self.acao_id} {self.data_negocio}>'
