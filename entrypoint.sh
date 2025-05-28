#!/bin/bash
set -e

echo "=== INICIANDO PROCESSO DE MIGRAÇÃO DE BANCO DE DADOS ==="

# Definir variáveis de ambiente para os comandos Flask
export FLASK_APP=run.py

# Função para verificar saúde do banco após migração
check_db_health() {
  echo "Verificando saúde do banco de dados..."
  python -c "from src.main import create_app; from src.models import db; from sqlalchemy import text; app = create_app(); with app.app_context(): result = db.session.execute(text('SELECT 1')); print('Verificação de saúde do banco: OK')"
  return $?
}

# Aplicar migrações com retry
apply_migrations() {
  MAX_ATTEMPTS=3
  INTERVAL=5
  
  for attempt in $(seq 1 $MAX_ATTEMPTS); do
    echo "Tentativa $attempt/$MAX_ATTEMPTS de aplicar migrações..."
    
    if flask db upgrade; then
      echo "Migrações aplicadas com sucesso!"
      return 0
    else
      echo "Erro ao aplicar migrações."
      
      if [ $attempt -lt $MAX_ATTEMPTS ]; then
        echo "Aguardando $INTERVAL segundos antes de tentar novamente..."
        sleep $INTERVAL
      else
        echo "Número máximo de tentativas excedido."
        return 1
      fi
    fi
  done
}

# Verificar se o diretório de migrações existe
if [ ! -d "migrations" ]; then
  echo "Inicializando repositório de migrações..."
  flask db init
fi

# Verificar se há arquivos de migração
if [ ! -d "migrations/versions" ] || [ -z "$(ls -A migrations/versions 2>/dev/null)" ]; then
  echo "Criando migração inicial..."
  flask db migrate -m "Migração inicial automática"
fi

# Aplicar migrações pendentes
echo "Aplicando migrações pendentes..."
if apply_migrations; then
  # Verificar saúde do banco após migração
  if check_db_health; then
    echo "=== MIGRAÇÃO CONCLUÍDA COM SUCESSO $(date -Iseconds) ==="
    
    # Iniciar a aplicação
    echo "Iniciando aplicação..."
    if [ -z "$PORT" ]; then
      export PORT=8080
    fi
    
    exec gunicorn --bind "0.0.0.0:$PORT" --workers 2 "src.main:create_app()"
  else
    echo "ERRO: Verificação de saúde do banco falhou após migração."
    exit 1
  fi
else
  echo "ERRO: Falha ao aplicar migrações."
  exit 1
fi
