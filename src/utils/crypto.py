import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CryptoManager:
    """
    Gerencia a criptografia e descriptografia de dados por usuário.
    Cada usuário tem sua própria chave de criptografia derivada da chave mestra.
    """
    
    @staticmethod
    def get_user_key(user_id):
        """
        Deriva uma chave de criptografia única para o usuário a partir da chave mestra.
        
        Args:
            user_id: ID único do usuário (Google ID)
            
        Returns:
            Uma instância de Fernet inicializada com a chave do usuário
        """
        # Obter a chave mestra do ambiente
        master_key = os.environ.get('MASTER_ENCRYPTION_KEY')
        if not master_key:
            raise ValueError("MASTER_ENCRYPTION_KEY não está definida nas variáveis de ambiente")
        
        # Usar o ID do usuário como salt para derivar uma chave única
        salt = str(user_id).encode()
        
        # Derivar uma chave de 32 bytes a partir da chave mestra usando PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        # Converter a chave mestra de base64 para bytes
        try:
            master_key_bytes = base64.b64decode(master_key)
        except Exception:
            # Se a chave não estiver em base64, usar como está (para desenvolvimento)
            master_key_bytes = master_key.encode()
        
        # Derivar a chave do usuário
        key = base64.urlsafe_b64encode(kdf.derive(master_key_bytes))
        
        # Retornar um objeto Fernet inicializado com a chave do usuário
        return Fernet(key)
    
    @staticmethod
    def encrypt(data, user_id):
        """
        Criptografa dados para um usuário específico.
        
        Args:
            data: String a ser criptografada
            user_id: ID único do usuário (Google ID)
            
        Returns:
            String criptografada em base64
        """
        if not data:
            return data
            
        # Obter a chave do usuário
        fernet = CryptoManager.get_user_key(user_id)
        
        # Criptografar os dados
        return fernet.encrypt(data.encode()).decode()
    
    @staticmethod
    def decrypt(encrypted_data, user_id):
        """
        Descriptografa dados para um usuário específico.
        
        Args:
            encrypted_data: String criptografada em base64
            user_id: ID único do usuário (Google ID)
            
        Returns:
            String descriptografada
        """
        if not encrypted_data:
            return encrypted_data
            
        # Obter a chave do usuário
        fernet = CryptoManager.get_user_key(user_id)
        
        # Descriptografar os dados
        try:
            return fernet.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            # Se a descriptografia falhar, pode ser porque os dados não estão criptografados
            # ou porque o usuário não tem permissão para descriptografar
            print(f"Erro ao descriptografar dados: {e}")
            return None
