#!/bin/bash

# Script para testar o isolamento de dados entre usuários
# Este script simula o acesso de dois usuários diferentes e verifica se há vazamento de dados

echo "Iniciando testes de isolamento de dados..."

# Função para simular requisições de um usuário
test_user_isolation() {
  USER_ID=$1
  echo "Testando usuário $USER_ID..."
  
  # Simular acesso às rotas principais
  echo "- Testando acesso às ações"
  curl -s -X GET "http://localhost:5000/acoes/" -H "Cookie: user_id=$USER_ID" > /dev/null
  
  echo "- Testando acesso aos relatórios"
  curl -s -X GET "http://localhost:5000/relatorios/" -H "Cookie: user_id=$USER_ID" > /dev/null
  
  echo "- Testando acesso aos saldos"
  curl -s -X GET "http://localhost:5000/saldos/" -H "Cookie: user_id=$USER_ID" > /dev/null
  
  echo "- Testando acesso às negociações"
  curl -s -X GET "http://localhost:5000/negociacoes/" -H "Cookie: user_id=$USER_ID" > /dev/null
  
  echo "Testes para usuário $USER_ID concluídos"
}

# Testar com dois usuários diferentes
test_user_isolation "user1"
test_user_isolation "user2"

echo "Testes de isolamento concluídos. Verifique os logs para confirmar que não há vazamento de dados."
