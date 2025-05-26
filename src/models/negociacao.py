from datetime import datetime
from src.models import db
from src.utils.crypto import CryptoManager
from flask_login import current_user

class Negociacao(db.Model):
    __tablename__ = 'negociacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    data_negocio = db.Column(db.Date, nullable=False)
    _tipo_movimentacao = db.Column('tipo_movimentacao', db.String(100), nullable=False)  # Campo criptografado
    _mercado = db.Column('mercado', db.String(100), nullable=False)  # Campo criptografado
    _prazo_vencimento = db.Column('prazo_vencimento', db.String(100), nullable=False)  # Campo criptografado
    _instituicao = db.Column('instituicao', db.String(200), nullable=False)  # Campo criptografado
    quantidade = db.Column(db.Integer, nullable=False)
    preco = db.Column(db.Float, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    corretagem = db.Column(db.Float, nullable=True)  # Valor de corretagem da operação
    
    # Chaves estrangeiras
    acao_id = db.Column(db.Integer, db.ForeignKey('acoes.id'), nullable=False)
    relatorio_id = db.Column(db.Integer, db.ForeignKey('relatorios.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Chave única composta para evitar duplicidades na importação de relatórios
    __table_args__ = (
        db.UniqueConstraint(
            'data_negocio', 'tipo_movimentacao', 'mercado', 'instituicao', 
            'acao_id', 'quantidade', 'preco', 'valor', 'user_id',
            name='uix_negociacao_completa'
        ),
    )
    
    # Propriedades para campos criptografados
    @property
    def tipo_movimentacao(self):
        """Descriptografa o tipo de movimentação ao acessar"""
        if not self._tipo_movimentacao:
            return None
        
        # Obter o usuário atual ou o proprietário da negociação
        user = current_user if current_user.is_authenticated else self.user
        if not user:
            return None
            
        # Descriptografar usando o Google ID do usuário
        return CryptoManager.decrypt(self._tipo_movimentacao, user.google_id)
    
    @tipo_movimentacao.setter
    def tipo_movimentacao(self, value):
        """Criptografa o tipo de movimentação ao definir"""
        if not value:
            self._tipo_movimentacao = None
            return
            
        # Obter o usuário atual ou o proprietário da negociação
        user = current_user if current_user.is_authenticated else self.user
        if not user:
            raise ValueError("Usuário não autenticado ou não associado à negociação")
            
        # Criptografar usando o Google ID do usuário
        self._tipo_movimentacao = CryptoManager.encrypt(value, user.google_id)
    
    @property
    def mercado(self):
        """Descriptografa o mercado ao acessar"""
        if not self._mercado:
            return None
        
        # Obter o usuário atual ou o proprietário da negociação
        user = current_user if current_user.is_authenticated else self.user
        if not user:
            return None
            
        # Descriptografar usando o Google ID do usuário
        return CryptoManager.decrypt(self._mercado, user.google_id)
    
    @mercado.setter
    def mercado(self, value):
        """Criptografa o mercado ao definir"""
        if not value:
            self._mercado = None
            return
            
        # Obter o usuário atual ou o proprietário da negociação
        user = current_user if current_user.is_authenticated else self.user
        if not user:
            raise ValueError("Usuário não autenticado ou não associado à negociação")
            
        # Criptografar usando o Google ID do usuário
        self._mercado = CryptoManager.encrypt(value, user.google_id)
    
    @property
    def prazo_vencimento(self):
        """Descriptografa o prazo de vencimento ao acessar"""
        if not self._prazo_vencimento:
            return None
        
        # Obter o usuário atual ou o proprietário da negociação
        user = current_user if current_user.is_authenticated else self.user
        if not user:
            return None
            
        # Descriptografar usando o Google ID do usuário
        return CryptoManager.decrypt(self._prazo_vencimento, user.google_id)
    
    @prazo_vencimento.setter
    def prazo_vencimento(self, value):
        """Criptografa o prazo de vencimento ao definir"""
        if not value:
            self._prazo_vencimento = None
            return
            
        # Obter o usuário atual ou o proprietário da negociação
        user = current_user if current_user.is_authenticated else self.user
        if not user:
            raise ValueError("Usuário não autenticado ou não associado à negociação")
            
        # Criptografar usando o Google ID do usuário
        self._prazo_vencimento = CryptoManager.encrypt(value, user.google_id)
    
    @property
    def instituicao(self):
        """Descriptografa a instituição ao acessar"""
        if not self._instituicao:
            return None
        
        # Obter o usuário atual ou o proprietário da negociação
        user = current_user if current_user.is_authenticated else self.user
        if not user:
            return None
            
        # Descriptografar usando o Google ID do usuário
        return CryptoManager.decrypt(self._instituicao, user.google_id)
    
    @instituicao.setter
    def instituicao(self, value):
        """Criptografa a instituição ao definir"""
        if not value:
            self._instituicao = None
            return
            
        # Obter o usuário atual ou o proprietário da negociação
        user = current_user if current_user.is_authenticated else self.user
        if not user:
            raise ValueError("Usuário não autenticado ou não associado à negociação")
            
        # Criptografar usando o Google ID do usuário
        self._instituicao = CryptoManager.encrypt(value, user.google_id)
    
    def __repr__(self):
        return f'<Negociacao {self.id} {self.acao_id} {self.data_negocio}>'
