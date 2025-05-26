from datetime import datetime
from src.models import db
from src.utils.crypto import CryptoManager
from flask_login import current_user

class Acao(db.Model):
    __tablename__ = 'acoes'
    
    id = db.Column(db.Integer, primary_key=True)
    _codigo = db.Column('codigo', db.String(100), nullable=False)  # Campo criptografado
    _cnpj = db.Column('cnpj', db.String(100), nullable=True)  # Campo criptografado
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chave estrangeira para o usuário
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relacionamentos
    negociacoes = db.relationship('Negociacao', backref='acao', lazy=True, cascade="all, delete-orphan")
    saldos = db.relationship('SaldoPrecoMedio', backref='acao', lazy=True, cascade="all, delete-orphan")
    
    @property
    def codigo(self):
        """Descriptografa o código da ação ao acessar"""
        if not self._codigo:
            return None
        
        # Obter o usuário atual ou o proprietário da ação
        user = current_user if current_user.is_authenticated else self.user
        if not user:
            return None
            
        # Descriptografar usando o Google ID do usuário
        return CryptoManager.decrypt(self._codigo, user.google_id)
    
    @codigo.setter
    def codigo(self, value):
        """Criptografa o código da ação ao definir"""
        if not value:
            self._codigo = None
            return
            
        # Obter o usuário atual ou o proprietário da ação
        user = current_user if current_user.is_authenticated else self.user
        if not user:
            raise ValueError("Usuário não autenticado ou não associado à ação")
            
        # Criptografar usando o Google ID do usuário
        self._codigo = CryptoManager.encrypt(value, user.google_id)
    
    @property
    def cnpj(self):
        """Descriptografa o CNPJ ao acessar"""
        if not self._cnpj:
            return None
            
        # Obter o usuário atual ou o proprietário da ação
        user = current_user if current_user.is_authenticated else self.user
        if not user:
            return None
            
        # Descriptografar usando o Google ID do usuário
        return CryptoManager.decrypt(self._cnpj, user.google_id)
    
    @cnpj.setter
    def cnpj(self, value):
        """Criptografa o CNPJ ao definir"""
        if not value:
            self._cnpj = None
            return
            
        # Obter o usuário atual ou o proprietário da ação
        user = current_user if current_user.is_authenticated else self.user
        if not user:
            raise ValueError("Usuário não autenticado ou não associado à ação")
            
        # Criptografar usando o Google ID do usuário
        self._cnpj = CryptoManager.encrypt(value, user.google_id)
    
    def __repr__(self):
        return f'<Acao {self.id}>'
