#!/bin/bash
set -e

echo "=== INICIANDO CONTAINER EM MODO SIMPLIFICADO ==="

# Definir variáveis de ambiente
export FLASK_APP=run.py

# Verificar a porta
if [ -z "$PORT" ]; then
  export PORT=8080
  echo "Porta não definida, usando padrão: 8080"
else
  echo "Usando porta definida pelo ambiente: $PORT"
fi

echo "Verificando ambiente..."
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "Diretório atual: $(pwd)"
echo "Conteúdo do diretório: $(ls -la)"
echo "Variáveis de ambiente: $(env | grep -E 'PORT|FLASK|PYTHON')"

# Iniciar a aplicação diretamente sem migrações
echo "=== INICIANDO APLICAÇÃO EM MODO DIRETO ==="
echo "Comando: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-level debug src.main:create_app()"

# Executar com logs detalhados
exec gunicorn --bind "0.0.0.0:$PORT" --workers 2 --timeout 120 --log-level debug "src.main:create_app()"
