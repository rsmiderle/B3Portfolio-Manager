import os
import urllib3
from dotenv import load_dotenv
from src.main import create_app

# Carregar variáveis de ambiente do arquivo .env, se existir
load_dotenv()

# Desabilitar avisos de SSL para evitar erros em requisições
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Verificar se as variáveis de ambiente necessárias estão configuradas
if not os.environ.get('GOOGLE_CLIENT_ID') or not os.environ.get('GOOGLE_CLIENT_SECRET'):
    print("AVISO: Variáveis de ambiente GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET não configuradas.")
    print("A autenticação Google OAuth não funcionará corretamente.")
    print("Consulte o arquivo GOOGLE_AUTH_SETUP.md para instruções de configuração.")

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
