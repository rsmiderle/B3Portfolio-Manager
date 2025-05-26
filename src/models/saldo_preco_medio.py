from datetime import datetime
from src.models import db
from src.utils.crypto import CryptoManager
from flask_login import current_user

class SaldoPrecoMedio(db.Model):
    __tablename__ = 'saldos_precos_medios'
    
    id = db.Column(db.Integer, primary_key=True)
    data_base = db.Column(db.Date, nullable=False)
    _quantidade = db.Column('quantidade', db.String(100), nullable=False)  # Campo criptografado
    _preco_medio = db.Column('preco_medio', db.String(100), nullable=False)  # Campo criptografado
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chaves estrangeiras
    acao_id = db.Column(db.Integer, db.ForeignKey('acoes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Comentário: Imposto para garantir unicidade de ação por data base
    __table_args__ = (
        db.UniqueConstraint('acao_id', 'data_base', name='uix_acao_data_base'),
    )
    
    @property
    def quantidade(self):
        """Descriptografa a quantidade ao acessar"""
        if not self._quantidade:
            return None
        
        # Obter o usuário atual ou o proprietário do saldo
        user = current_user if current_user.is_authenticated else self.user
        if not user:
            return None
            
        # Descriptografar usando o Google ID do usuário
        decrypted = CryptoManager.decrypt(self._quantidade, user.google_id)
        return int(decrypted) if decrypted is not None else None
    
    @quantidade.setter
    def quantidade(self, value):
        """Criptografa a quantidade ao definir"""
        if value is None:
            self._quantidade = None
            return
            
        # Obter o usuário atual ou o proprietário do saldo
        user = current_user if current_user.is_authenticated else self.user
        if not user:
            raise ValueError("Usuário não autenticado ou não associado ao saldo")
            
        # Criptografar usando o Google ID do usuário
        self._quantidade = CryptoManager.encrypt(str(value), user.google_id)
    
    @property
    def preco_medio(self):
        """Descriptografa o preço médio ao acessar"""
        if not self._preco_medio:
            return None
        
        # Obter o usuário atual ou o proprietário do saldo
        user = current_user if current_user.is_authenticated else self.user
        if not user:
            return None
            
        # Descriptografar usando o Google ID do usuário
        decrypted = CryptoManager.decrypt(self._preco_medio, user.google_id)
        return float(decrypted) if decrypted is not None else None
    
    @preco_medio.setter
    def preco_medio(self, value):
        """Criptografa o preço médio ao definir"""
        if value is None:
            self._preco_medio = None
            return
            
        # Obter o usuário atual ou o proprietário do saldo
        user = current_user if current_user.is_authenticated else self.user
        if not user:
            raise ValueError("Usuário não autenticado ou não associado ao saldo")
            
        # Criptografar usando o Google ID do usuário
        self._preco_medio = CryptoManager.encrypt(str(value), user.google_id)
    
    def __repr__(self):
        return f'<SaldoPrecoMedio {self.acao_id} {self.data_base}>'
