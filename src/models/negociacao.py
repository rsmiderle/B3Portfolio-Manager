from datetime import datetime
from src.models import db

class Negociacao(db.Model):
    __tablename__ = 'negociacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    data_negocio = db.Column(db.Date, nullable=False)
    tipo_movimentacao = db.Column(db.String(20), nullable=False)  # Compra ou Venda
    mercado = db.Column(db.String(50), nullable=False)
    prazo_vencimento = db.Column(db.String(50), nullable=False)
    instituicao = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco = db.Column(db.Float, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    corretagem = db.Column(db.Float, nullable=True)  # Valor de corretagem da operação
    
    # Chaves estrangeiras
    acao_id = db.Column(db.Integer, db.ForeignKey('acoes.id'), nullable=False)
    relatorio_id = db.Column(db.Integer, db.ForeignKey('relatorios.id'), nullable=False)
    
    def __repr__(self):
        return f'<Negociacao {self.acao_id} {self.tipo_movimentacao} {self.data_negocio}>'
