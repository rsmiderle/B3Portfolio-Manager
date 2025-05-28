#!/bin/bash
set -e

echo "=== INICIANDO CONTAINER ==="

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
echo "Diretório atual: $(pwd)"
echo "Variáveis de ambiente: $(env | grep -E 'PORT|FLASK|PYTHON|ADMIN')"

# Iniciar a aplicação sem migrações automáticas
echo "=== INICIANDO APLICAÇÃO ==="
echo "Comando: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 src.main:create_app()"

# Executar com timeout aumentado
exec gunicorn --bind "0.0.0.0:$PORT" --workers 2 --timeout 120 "src.main:create_app()"
