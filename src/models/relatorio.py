from datetime import datetime
from src.models import db
from src.utils.crypto import CryptoManager
from flask_login import current_user

class Relatorio(db.Model):
    __tablename__ = 'relatorios'
    
    id = db.Column(db.Integer, primary_key=True)
    _nome_arquivo = db.Column('nome_arquivo', db.String(200), nullable=False)  # Campo criptografado
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chave estrangeira para o usuário
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relacionamentos
    negociacoes = db.relationship('Negociacao', backref='relatorio', lazy=True, cascade="all, delete-orphan")
    
    @property
    def nome_arquivo(self):
        """Descriptografa o nome do arquivo ao acessar"""
        if not self._nome_arquivo:
            return None
        
        # Obter o usuário atual ou o proprietário do relatório
        user = current_user if current_user.is_authenticated else self.user
        if not user:
            return None
            
        # Descriptografar usando o Google ID do usuário
        return CryptoManager.decrypt(self._nome_arquivo, user.google_id)
    
    @nome_arquivo.setter
    def nome_arquivo(self, value):
        """Criptografa o nome do arquivo ao definir"""
        if not value:
            self._nome_arquivo = None
            return
            
        # Obter o usuário atual ou o proprietário do relatório
        user = current_user if current_user.is_authenticated else self.user
        if not user:
            raise ValueError("Usuário não autenticado ou não associado ao relatório")
            
        # Criptografar usando o Google ID do usuário
        self._nome_arquivo = CryptoManager.encrypt(value, user.google_id)
    
    def __repr__(self):
        return f'<Relatorio {self.id}>'
