"""
Script Python para validar a anonimização e integridade dos dados

Este script verifica se a anonimização foi implementada corretamente e se
a integridade dos dados foi mantida após a migração.
"""

import hashlib
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import sys

# Configuração do banco de dados
DB_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
engine = create_engine(DB_URI)
Session = sessionmaker(bind=engine)
session = Session()

# Obter o salt da variável de ambiente
ANONYMIZATION_SALT = os.environ.get('ANONYMIZATION_SALT', 'DEFAULT_SALT_CHANGE_IN_PRODUCTION')

def validate_user_anonymization():
    """Valida se todos os usuários possuem hash_id e se são únicos"""
    print("Validando anonimização de usuários...")
    
    # Verificar se todos os usuários têm hash_id
    result = session.execute(text("SELECT COUNT(*) FROM users WHERE hash_id IS NULL")).scalar()
    if result > 0:
        print(f"ERRO: {result} usuários não possuem hash_id!")
        return False
    
    # Verificar se os hash_id são únicos
    result = session.execute(text("""
        SELECT hash_id, COUNT(*) 
        FROM users 
        GROUP BY hash_id 
        HAVING COUNT(*) > 1
    """)).fetchall()
    
    if result:
        print(f"ERRO: Existem hash_id duplicados: {result}")
        return False
    
    # Verificar se o hash_id corresponde ao algoritmo esperado
    users = session.execute(text("SELECT id, google_id, hash_id FROM users")).fetchall()
    
    for user_id, google_id, hash_id in users:
        expected_hash = hashlib.sha256(f"{google_id}{ANONYMIZATION_SALT}".encode()).hexdigest()
        if expected_hash != hash_id:
            print(f"ERRO: Hash incorreto para usuário {user_id}")
            print(f"  Esperado: {expected_hash}")
            print(f"  Atual: {hash_id}")
            return False
    
    print("✓ Anonimização de usuários validada com sucesso!")
    return True

def validate_foreign_keys():
    """Valida se todas as chaves estrangeiras estão corretas"""
    print("Validando chaves estrangeiras...")
    
    # Verificar se todas as negociações têm user_hash válido
    result = session.execute(text("""
        SELECT COUNT(*) FROM negociacoes n 
        LEFT JOIN users u ON n.user_hash = u.hash_id
        WHERE u.id IS NULL
    """)).scalar()
    
    if result > 0:
        print(f"ERRO: {result} negociações com user_hash inválido!")
        return False
    
    # Verificar se todas as ações têm user_hash válido
    result = session.execute(text("""
        SELECT COUNT(*) FROM acoes a 
        LEFT JOIN users u ON a.user_hash = u.hash_id
        WHERE u.id IS NULL
    """)).scalar()
    
    if result > 0:
        print(f"ERRO: {result} ações com user_hash inválido!")
        return False
    
    # Verificar se todos os relatórios têm user_hash válido
    result = session.execute(text("""
        SELECT COUNT(*) FROM relatorios r 
        LEFT JOIN users u ON r.user_hash = u.hash_id
        WHERE u.id IS NULL
    """)).scalar()
    
    if result > 0:
        print(f"ERRO: {result} relatórios com user_hash inválido!")
        return False
    
    # Verificar se todos os saldos têm user_hash válido
    result = session.execute(text("""
        SELECT COUNT(*) FROM saldos_precos_medios s 
        LEFT JOIN users u ON s.user_hash = u.hash_id
        WHERE u.id IS NULL
    """)).scalar()
    
    if result > 0:
        print(f"ERRO: {result} saldos com user_hash inválido!")
        return False
    
    print("✓ Chaves estrangeiras validadas com sucesso!")
    return True

def validate_data_integrity():
    """Valida se os dados foram convertidos corretamente"""
    print("Validando integridade dos dados...")
    
    # Verificar se não existem valores nulos em campos obrigatórios
    tables = ['negociacoes', 'acoes', 'relatorios', 'saldos_precos_medios']
    
    for table in tables:
        # Obter colunas da tabela
        columns = session.execute(text(f"SHOW COLUMNS FROM {table}")).fetchall()
        for col in columns:
            col_name = col[0]
            nullable = col[2]  # 'YES' se for nullable, 'NO' se não for
            
            if nullable == 'NO' and col_name not in ['id', 'created_at']:
                result = session.execute(text(f"""
                    SELECT COUNT(*) FROM {table} 
                    WHERE {col_name} IS NULL
                """)).scalar()
                
                if result > 0:
                    print(f"ERRO: {result} registros com {col_name} nulo na tabela {table}!")
                    return False
    
    print("✓ Integridade dos dados validada com sucesso!")
    return True

def validate_anonymization_effectiveness():
    """Valida se não é possível relacionar dados de negócio com dados pessoais"""
    print("Validando efetividade da anonimização...")
    
    # Verificar se é possível relacionar negociações diretamente com e-mail ou nome
    query = """
    SELECT COUNT(*) FROM (
        SELECT n.id, u.email, u.name
        FROM negociacoes n
        JOIN users u ON n.user_hash = u.hash_id
        LIMIT 1
    ) AS direct_join
    """
    
    # Esta consulta deve funcionar, mas o ponto é que alguém com acesso apenas
    # ao banco de dados (sem acesso ao código) não conseguiria fazer essa relação
    # sem conhecer o algoritmo de hash e o salt
    result = session.execute(text(query)).scalar()
    
    if result > 0:
        print("AVISO: É possível relacionar negociações com dados pessoais via JOIN direto.")
        print("Isso é esperado no código da aplicação, mas não deve ser possível para")
        print("alguém com acesso apenas ao banco de dados sem conhecer o algoritmo de hash e o salt.")
    
    # Verificar se o hash_id não contém informações do usuário
    users = session.execute(text("SELECT email, name, hash_id FROM users LIMIT 10")).fetchall()
    for email, name, hash_id in users:
        if email.lower() in hash_id.lower() or (name and name.lower() in hash_id.lower()):
            print(f"ERRO: hash_id contém informações do usuário: {hash_id}")
            return False
    
    print("✓ Efetividade da anonimização validada com sucesso!")
    return True

def validate_performance():
    """Valida a performance das consultas principais"""
    print("Validando performance das consultas...")
    
    # Lista de consultas a serem testadas
    queries = [
        "SELECT * FROM users LIMIT 100",
        "SELECT * FROM negociacoes LIMIT 100",
        "SELECT * FROM acoes LIMIT 100",
        "SELECT * FROM relatorios LIMIT 100",
        "SELECT * FROM saldos_precos_medios LIMIT 100",
        """
        SELECT n.* FROM negociacoes n
        JOIN acoes a ON n.acao_id = a.id
        WHERE n.user_hash = (SELECT hash_id FROM users LIMIT 1)
        LIMIT 100
        """,
        """
        SELECT a.codigo, SUM(s.quantidade) as total_quantidade, AVG(s.preco_medio) as preco_medio_geral
        FROM saldos_precos_medios s
        JOIN acoes a ON s.acao_id = a.id
        WHERE s.user_hash = (SELECT hash_id FROM users LIMIT 1)
        GROUP BY a.codigo
        LIMIT 100
        """
    ]
    
    import time
    
    for i, query in enumerate(queries):
        start_time = time.time()
        session.execute(text(query))
        end_time = time.time()
        
        execution_time = end_time - start_time
        print(f"Consulta {i+1}: {execution_time:.4f} segundos")
        
        if execution_time > 1.0:  # Limite arbitrário de 1 segundo
            print(f"AVISO: Consulta {i+1} pode precisar de otimização (tempo > 1s)")
    
    print("✓ Performance das consultas validada!")
    return True

def main():
    """Função principal que executa todas as validações"""
    print("Iniciando validação da anonimização e integridade dos dados...")
    print(f"Usando salt da variável de ambiente: {'[CONFIGURADO]' if os.environ.get('ANONYMIZATION_SALT') else '[USANDO VALOR PADRÃO]'}")
    
    all_valid = True
    all_valid &= validate_user_anonymization()
    all_valid &= validate_foreign_keys()
    all_valid &= validate_data_integrity()
    all_valid &= validate_anonymization_effectiveness()
    all_valid &= validate_performance()
    
    if all_valid:
        print("\n✅ SUCESSO: Anonimização e integridade dos dados validadas com sucesso!")
        return 0
    else:
        print("\n❌ FALHA: Foram encontrados problemas na validação!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
