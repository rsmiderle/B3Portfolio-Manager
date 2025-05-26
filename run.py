import os
import urllib3
import subprocess
from dotenv import load_dotenv
from flask import Flask
from flask.cli import FlaskGroup
from flask_migrate import Migrate
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

def init_db():
    """Inicializa o banco de dados automaticamente executando as migrações"""
    with app.app_context():
        # Verificar se o diretório de migrações existe
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        if not os.path.exists(migrations_dir):
            print("Inicializando repositório de migrações...")
            subprocess.run(["flask", "db", "init"], check=True)
            
        # Verificar se há arquivos de migração
        versions_dir = os.path.join(migrations_dir, 'versions')
        if not os.path.exists(versions_dir) or not os.listdir(versions_dir):
            print("Criando migração inicial...")
            subprocess.run(["flask", "db", "migrate", "-m", "Migração inicial automática"], check=True)
        
        # Aplicar migrações pendentes
        print("Aplicando migrações pendentes...")
        subprocess.run(["flask", "db", "upgrade"], check=True)
        print("Banco de dados inicializado com sucesso!")

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
