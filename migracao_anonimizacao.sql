"""
Script de migração para remover criptografia e implementar anonimização

Este script contém as instruções SQL para migrar o banco de dados da versão
com criptografia para a versão sem criptografia, mas com anonimização.

IMPORTANTE: Faça backup do banco de dados antes de executar este script!
"""

# Migração para MySQL

# 1. Adicionar coluna hash_id na tabela users
ALTER TABLE users ADD COLUMN hash_id VARCHAR(64) UNIQUE;

# 2. Preencher hash_id para usuários existentes
# Este comando deve ser executado via Python para garantir o mesmo algoritmo de hash
# Exemplo de código Python:
"""
import hashlib
import os
from app import db
from src.models.user import User

# Obter o salt da variável de ambiente ou usar valor padrão
salt = os.environ.get('ANONYMIZATION_SALT', 'DEFAULT_SALT_CHANGE_IN_PRODUCTION')

# Atualizar hash_id para todos os usuários
users = User.query.all()
for user in users:
    hash_input = f"{user.google_id}{salt}"
    user.hash_id = hashlib.sha256(hash_input.encode()).hexdigest()
db.session.commit()
"""

# 3. Adicionar colunas temporárias nas tabelas de negócio
ALTER TABLE negociacoes ADD COLUMN user_hash VARCHAR(64);
ALTER TABLE acoes ADD COLUMN user_hash VARCHAR(64);
ALTER TABLE relatorios ADD COLUMN user_hash VARCHAR(64);
ALTER TABLE saldos_precos_medios ADD COLUMN user_hash VARCHAR(64);

# 4. Preencher user_hash com base no user_id
# Este comando deve ser executado via Python para garantir integridade referencial
# Exemplo de código Python:
"""
from app import db
from src.models.user import User
from src.models.all_models import Negociacao, Acao, Relatorio, SaldoPrecoMedio

# Mapear user_id para hash_id
user_map = {user.id: user.hash_id for user in User.query.all()}

# Atualizar negociações
for neg in Negociacao.query.all():
    neg.user_hash = user_map.get(neg.user_id)

# Atualizar ações
for acao in Acao.query.all():
    acao.user_hash = user_map.get(acao.user_id)

# Atualizar relatórios
for rel in Relatorio.query.all():
    rel.user_hash = user_map.get(rel.user_id)

# Atualizar saldos
for saldo in SaldoPrecoMedio.query.all():
    saldo.user_hash = user_map.get(saldo.user_id)

db.session.commit()
"""

# 5. Descriptografar dados e converter para tipos nativos
# Este comando deve ser executado via Python para usar o CryptoManager existente
# Exemplo de código Python:
"""
from app import db
from src.models.all_models import Negociacao, Acao, Relatorio, SaldoPrecoMedio
from src.utils.crypto import CryptoManager

# Descriptografar negociações
for neg in Negociacao.query.all():
    user = neg.user
    if user:
        # Descriptografar e salvar em variáveis temporárias
        tipo_mov = CryptoManager.decrypt(neg._tipo_movimentacao, user.google_id)
        mercado = CryptoManager.decrypt(neg._mercado, user.google_id)
        prazo = CryptoManager.decrypt(neg._prazo_vencimento, user.google_id)
        inst = CryptoManager.decrypt(neg._instituicao, user.google_id)
        
        # Atualizar colunas diretas (sem underscore)
        neg.tipo_movimentacao = tipo_mov
        neg.mercado = mercado
        neg.prazo_vencimento = prazo
        neg.instituicao = inst

# Descriptografar ações
for acao in Acao.query.all():
    user = acao.user
    if user:
        acao.codigo = CryptoManager.decrypt(acao._codigo, user.google_id)
        if acao._cnpj:
            acao.cnpj = CryptoManager.decrypt(acao._cnpj, user.google_id)

# Descriptografar relatórios
for rel in Relatorio.query.all():
    user = rel.user
    if user:
        rel.nome_arquivo = CryptoManager.decrypt(rel._nome_arquivo, user.google_id)

# Descriptografar saldos
for saldo in SaldoPrecoMedio.query.all():
    user = saldo.user
    if user:
        qtd_str = CryptoManager.decrypt(saldo._quantidade, user.google_id)
        preco_str = CryptoManager.decrypt(saldo._preco_medio, user.google_id)
        
        saldo.quantidade = int(qtd_str) if qtd_str else 0
        saldo.preco_medio = float(preco_str) if preco_str else 0.0

db.session.commit()
"""

# 6. Remover colunas antigas e adicionar constraints
ALTER TABLE negociacoes 
    DROP COLUMN _tipo_movimentacao,
    DROP COLUMN _mercado,
    DROP COLUMN _prazo_vencimento,
    DROP COLUMN _instituicao,
    DROP COLUMN user_id,
    MODIFY COLUMN user_hash VARCHAR(64) NOT NULL,
    ADD CONSTRAINT fk_negociacao_user FOREIGN KEY (user_hash) REFERENCES users(hash_id);

ALTER TABLE acoes
    DROP COLUMN _codigo,
    DROP COLUMN _cnpj,
    DROP COLUMN user_id,
    MODIFY COLUMN user_hash VARCHAR(64) NOT NULL,
    ADD CONSTRAINT fk_acao_user FOREIGN KEY (user_hash) REFERENCES users(hash_id);

ALTER TABLE relatorios
    DROP COLUMN _nome_arquivo,
    DROP COLUMN user_id,
    MODIFY COLUMN user_hash VARCHAR(64) NOT NULL,
    ADD CONSTRAINT fk_relatorio_user FOREIGN KEY (user_hash) REFERENCES users(hash_id);

ALTER TABLE saldos_precos_medios
    DROP COLUMN _quantidade,
    DROP COLUMN _preco_medio,
    DROP COLUMN user_id,
    MODIFY COLUMN user_hash VARCHAR(64) NOT NULL,
    ADD CONSTRAINT fk_saldo_user FOREIGN KEY (user_hash) REFERENCES users(hash_id);

# 7. Recriar índices e constraints
ALTER TABLE negociacoes 
    DROP INDEX uix_negociacao_completa,
    ADD CONSTRAINT uix_negociacao_completa UNIQUE (
        data_negocio, tipo_movimentacao, mercado, instituicao, 
        acao_id, quantidade, preco, valor, user_hash
    );

# 8. Otimizar tipos de dados
ALTER TABLE negociacoes
    MODIFY COLUMN tipo_movimentacao VARCHAR(50) NOT NULL,
    MODIFY COLUMN mercado VARCHAR(50) NOT NULL,
    MODIFY COLUMN prazo_vencimento VARCHAR(50) NOT NULL,
    MODIFY COLUMN instituicao VARCHAR(100) NOT NULL,
    MODIFY COLUMN preco DECIMAL(10,2) NOT NULL,
    MODIFY COLUMN valor DECIMAL(12,2) NOT NULL,
    MODIFY COLUMN corretagem DECIMAL(10,2) NULL;

ALTER TABLE acoes
    MODIFY COLUMN codigo VARCHAR(20) NOT NULL,
    MODIFY COLUMN cnpj VARCHAR(18) NULL;

ALTER TABLE relatorios
    MODIFY COLUMN nome_arquivo VARCHAR(255) NOT NULL;

ALTER TABLE saldos_precos_medios
    MODIFY COLUMN quantidade INT NOT NULL,
    MODIFY COLUMN preco_medio DECIMAL(10,2) NOT NULL;
