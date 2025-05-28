import os
import sys
import urllib3
import subprocess
import hashlib
import time
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask
from flask.cli import FlaskGroup
from flask_migrate import Migrate
from sqlalchemy import text
from src.main import create_app
from src.models import db

# Carregar variáveis de ambiente do arquivo .env, se existir
load_dotenv()

# Usar variáveis de ambiente (funcionará tanto com .env quanto com Cloud Run)
google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
secret_key = os.environ.get('SECRET_KEY')

# Desabilitar avisos de SSL para evitar erros em requisições
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Verificar se as variáveis de ambiente necessárias estão configuradas
if not os.environ.get('GOOGLE_CLIENT_ID') or not os.environ.get('GOOGLE_CLIENT_SECRET'):
    print("AVISO: Variáveis de ambiente GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET não configuradas.")
    print("A autenticação Google OAuth não funcionará corretamente.")
    print("Consulte o arquivo GOOGLE_AUTH_SETUP.md para instruções de configuração.")

app = create_app()
cli = FlaskGroup(create_app=create_app)

def verificar_saude_banco():
    """Verifica se o banco de dados está funcionando corretamente após a migração"""
    try:
        # Tenta executar uma consulta simples
        db.session.execute(text("SELECT 1"))
        print("Verificação de saúde do banco: OK")
        return True
    except Exception as e:
        print(f"Verificação de saúde do banco: FALHA - {e}")
        return False

def aplicar_migracoes_com_retry(env, max_tentativas=3, intervalo=5):
    """Aplica migrações com mecanismo de retry"""
    for tentativa in range(1, max_tentativas + 1):
        try:
            print(f"Tentativa {tentativa}/{max_tentativas} de aplicar migrações...")
            subprocess.run(["flask", "db", "upgrade"], env=env, check=True, timeout=60)
            print("Migrações aplicadas com sucesso!")
            return True
        except Exception as e:
            print(f"Erro ao aplicar migrações: {e}")
            if tentativa < max_tentativas:
                print(f"Aguardando {intervalo} segundos antes de tentar novamente...")
                time.sleep(intervalo)
            else:
                print("Número máximo de tentativas excedido.")
                raise

def gerar_hash_id_para_usuarios():
    """Gera hash_id para usuários existentes que não possuem"""
    try:
        from src.models.user import User
        usuarios_sem_hash = User.query.filter(User.hash_id.is_(None)).all()
        if usuarios_sem_hash:
            print(f"Encontrados {len(usuarios_sem_hash)} usuários sem hash_id. Gerando...")
            salt = os.environ.get('ANONYMIZATION_SALT', 'DEFAULT_SALT_CHANGE_IN_PRODUCTION')
            for user in usuarios_sem_hash:
                hash_input = f"{user.google_id}{salt}"
                user.hash_id = hashlib.sha256(hash_input.encode()).hexdigest()
            db.session.commit()
            print("Hash IDs gerados com sucesso!")
        else:
            print("Todos os usuários já possuem hash_id.")
    except Exception as e:
        print(f"AVISO: Erro ao gerar hash_id para usuários: {e}")

def verificar_estrutura_tabela(tabela, coluna):
    """Verifica se uma coluna existe em uma tabela"""
    try:
        # Para SQLite
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            result = db.session.execute(text(f"PRAGMA table_info({tabela})")).fetchall()
            for col in result:
                if col[1] == coluna:
                    return True
            return False
        # Para MySQL
        else:
            result = db.session.execute(text(
                f"SELECT COUNT(*) FROM information_schema.columns "
                f"WHERE table_name = '{tabela}' AND column_name = '{coluna}'"
            )).fetchone()
            return result[0] > 0
    except Exception as e:
        print(f"Erro ao verificar estrutura da tabela {tabela}: {e}")
        return False

def forcar_migracao_se_necessario():
    """Força a criação de uma nova migração se a estrutura do banco estiver desatualizada"""
    with app.app_context():
        # Verificar se a coluna hash_id existe na tabela users
        if not verificar_estrutura_tabela('users', 'hash_id'):
            print("Coluna hash_id não encontrada na tabela users. Forçando nova migração...")
            env = os.environ.copy()
            env['FLASK_APP'] = 'run.py'
            
            try:
                # Criar uma nova migração
                subprocess.run(["flask", "db", "migrate", "-m", "Adicionar coluna hash_id e outras alterações"], 
                              env=env, check=True)
                
                # Aplicar a migração
                aplicar_migracoes_com_retry(env)
                
                # Verificar novamente
                if verificar_estrutura_tabela('users', 'hash_id'):
                    print("Migração forçada aplicada com sucesso!")
                else:
                    print("AVISO: A migração forçada não criou a coluna hash_id.")
            except Exception as e:
                print(f"ERRO ao forçar migração: {e}")
                print("Tentando abordagem alternativa...")
                
                # Abordagem alternativa: executar SQL diretamente
                try:
                    if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
                        db.session.execute(text("ALTER TABLE users ADD COLUMN hash_id VARCHAR(64) UNIQUE"))
                        db.session.commit()
                        print("Coluna hash_id adicionada diretamente via SQL.")
                    else:
                        print("Abordagem alternativa só está disponível para SQLite.")
                except Exception as e2:
                    print(f"ERRO na abordagem alternativa: {e2}")
                    print("Não foi possível adicionar a coluna hash_id automaticamente.")
                    print("Você pode precisar executar manualmente: flask db migrate, flask db upgrade")

def init_db():
    """Inicializa o banco de dados automaticamente executando as migrações"""
    print("=== INICIANDO PROCESSO DE MIGRAÇÃO DE BANCO DE DADOS ===")
    
    with app.app_context():
        # Definir variáveis de ambiente para os comandos Flask
        env = os.environ.copy()
        env['FLASK_APP'] = 'run.py'
        
        # Verificar se o diretório de migrações existe
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        if not os.path.exists(migrations_dir):
            print("Inicializando repositório de migrações...")
            subprocess.run(["flask", "db", "init"], env=env, check=True)
            
        # Verificar se há arquivos de migração
        versions_dir = os.path.join(migrations_dir, 'versions')
        if not os.path.exists(versions_dir) or not os.listdir(versions_dir):
            print("Criando migração inicial...")
            subprocess.run(["flask", "db", "migrate", "-m", "Migração inicial automática"], env=env, check=True)
        
        # Aplicar migrações pendentes
        print("Aplicando migrações pendentes...")
        aplicar_migracoes_com_retry(env)
        
        # Verificar se a estrutura está atualizada e forçar migração se necessário
        forcar_migracao_se_necessario()
        
        # Gerar hash_id para usuários existentes
        gerar_hash_id_para_usuarios()
        
        # Verificar saúde do banco
        if verificar_saude_banco():
            print(f"=== MIGRAÇÃO CONCLUÍDA COM SUCESSO EM {datetime.now().isoformat()} ===")
        else:
            print("AVISO: Verificação de saúde do banco falhou após migração.")

if __name__ == '__main__':
    # Inicializar banco de dados automaticamente
    try:
        init_db()
    except Exception as e:
        print(f"AVISO: Erro ao inicializar banco de dados: {e}")
        print("Você pode precisar executar manualmente: flask db init, flask db migrate, flask db upgrade")
    
    # Iniciar a aplicação
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
