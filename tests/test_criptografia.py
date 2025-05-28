import os
import sys
import unittest
from datetime import datetime
from flask_login import login_user

# Adicionar o diretório raiz ao path para importar os módulos corretamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import create_app
from src.models import db
from src.models.user import User
from src.models.acao import Acao
from src.models.negociacao import Negociacao
from src.models.relatorio import Relatorio
from src.utils.crypto import CryptoManager

class TestCriptografia(unittest.TestCase):
    """Testes para validar a criptografia de dados por usuário"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        # Configurar ambiente de teste
        os.environ['FLASK_ENV'] = 'testing'
        os.environ['MASTER_ENCRYPTION_KEY'] = 'chave_teste_123456789012345678901234567890'
        
        # Criar aplicação de teste com SQLite em memória
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        # Criar contexto de aplicação
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Criar tabelas no banco de dados
        db.create_all()
        
        # Criar usuários de teste
        self.user1 = User(
            email='user1@example.com',
            name='Usuário 1',
            google_id='123456789',
            profile_pic='https://example.com/pic1.jpg'
        )
        
        self.user2 = User(
            email='user2@example.com',
            name='Usuário 2',
            google_id='987654321',
            profile_pic='https://example.com/pic2.jpg'
        )
        
        db.session.add(self.user1)
        db.session.add(self.user2)
        db.session.commit()
        
        # Criar contexto de requisição
        self.request_context = self.app.test_request_context()
        self.request_context.push()
    
    def tearDown(self):
        """Limpeza após cada teste"""
        db.session.remove()
        db.drop_all()
        self.request_context.pop()
        self.app_context.pop()
    
    def test_criptografia_acao(self):
        """Testa a criptografia e descriptografia de dados de ação"""
        # Fazer login com o usuário 1
        login_user(self.user1)
        
        # Criar uma ação para o usuário 1
        acao1 = Acao(
            codigo='PETR4',
            cnpj='33.000.167/0001-01',
            user_id=self.user1.id
        )
        
        db.session.add(acao1)
        db.session.commit()
        
        # Verificar se os dados foram criptografados no banco
        acao_db = db.session.query(Acao).filter_by(id=acao1.id).first()
        self.assertNotEqual(acao_db._codigo, 'PETR4')
        self.assertNotEqual(acao_db._cnpj, '33.000.167/0001-01')
        
        # Verificar se os dados são descriptografados corretamente para o usuário 1
        self.assertEqual(acao_db.codigo, 'PETR4')
        self.assertEqual(acao_db.cnpj, '33.000.167/0001-01')
        
        # Fazer login com o usuário 2
        login_user(self.user2)
        
        # Verificar que o usuário 2 não consegue descriptografar os dados do usuário 1
        acao_db = db.session.query(Acao).filter_by(id=acao1.id).first()
        self.assertNotEqual(acao_db.codigo, 'PETR4')
        self.assertNotEqual(acao_db.cnpj, '33.000.167/0001-01')
    
    def test_criptografia_negociacao(self):
        """Testa a criptografia e descriptografia de dados de negociação"""
        # Fazer login com o usuário 1
        login_user(self.user1)
        
        # Criar uma ação para o usuário 1
        acao1 = Acao(
            codigo='VALE3',
            cnpj='33.592.510/0001-54',
            user_id=self.user1.id
        )
        
        db.session.add(acao1)
        db.session.commit()
        
        # Criar um relatório para o usuário 1
        relatorio1 = Relatorio(
            nome_arquivo='relatorio_teste.xlsx',
            user_id=self.user1.id
        )
        
        db.session.add(relatorio1)
        db.session.commit()
        
        # Criar uma negociação para o usuário 1
        negociacao1 = Negociacao(
            data_negocio=datetime.now().date(),
            tipo_movimentacao='Compra',
            mercado='Bovespa',
            prazo_vencimento='Vista',
            instituicao='Corretora XYZ',
            quantidade=100,
            preco=45.67,
            valor=4567.00,
            corretagem=10.00,
            acao_id=acao1.id,
            relatorio_id=relatorio1.id,
            user_id=self.user1.id
        )
        
        db.session.add(negociacao1)
        db.session.commit()
        
        # Verificar se os dados foram criptografados no banco
        negociacao_db = db.session.query(Negociacao).filter_by(id=negociacao1.id).first()
        self.assertNotEqual(negociacao_db._tipo_movimentacao, 'Compra')
        self.assertNotEqual(negociacao_db._mercado, 'Bovespa')
        self.assertNotEqual(negociacao_db._prazo_vencimento, 'Vista')
        self.assertNotEqual(negociacao_db._instituicao, 'Corretora XYZ')
        
        # Verificar se os dados são descriptografados corretamente para o usuário 1
        self.assertEqual(negociacao_db.tipo_movimentacao, 'Compra')
        self.assertEqual(negociacao_db.mercado, 'Bovespa')
        self.assertEqual(negociacao_db.prazo_vencimento, 'Vista')
        self.assertEqual(negociacao_db.instituicao, 'Corretora XYZ')
        
        # Fazer login com o usuário 2
        login_user(self.user2)
        
        # Verificar que o usuário 2 não consegue descriptografar os dados do usuário 1
        negociacao_db = db.session.query(Negociacao).filter_by(id=negociacao1.id).first()
        self.assertNotEqual(negociacao_db.tipo_movimentacao, 'Compra')
        self.assertNotEqual(negociacao_db.mercado, 'Bovespa')
        self.assertNotEqual(negociacao_db.prazo_vencimento, 'Vista')
        self.assertNotEqual(negociacao_db.instituicao, 'Corretora XYZ')

if __name__ == '__main__':
    unittest.main()
