# Desabilitar avisos de SSL para evitar erros de certificado
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import os
from src.main import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
