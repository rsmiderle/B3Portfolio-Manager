"""
Script de migração para adicionar a coluna hash_id à tabela users

Este script contém as instruções para adicionar a coluna hash_id à tabela users
e preencher essa coluna com valores hash gerados a partir do Google ID.

IMPORTANTE: Execute este script antes de usar o sistema com a nova estrutura anonimizada.
"""

import os
import hashlib
import sqlite3
from pathlib import Path

# Configuração
DB_PATH = os.environ.get('SQLITE_DB_PATH', 'instance/app.db')  # Caminho padrão do SQLite no Flask
SALT = os.environ.get('ANONYMIZATION_SALT', 'DEFAULT_SALT_CHANGE_IN_PRODUCTION')

def main():
    """Função principal que executa a migração"""
    print(f"Iniciando migração para adicionar hash_id à tabela users no banco {DB_PATH}")
    
    # Verificar se o banco existe
    if not Path(DB_PATH).exists():
        print(f"Erro: Banco de dados não encontrado em {DB_PATH}")
        print("Verifique o caminho do banco ou crie o banco antes de executar a migração")
        return False
    
    # Conectar ao banco
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'hash_id' in columns:
            print("A coluna hash_id já existe na tabela users")
        else:
            # Adicionar a coluna hash_id
            print("Adicionando coluna hash_id à tabela users...")
            cursor.execute("ALTER TABLE users ADD COLUMN hash_id VARCHAR(64)")
            
            # Buscar todos os usuários
            cursor.execute("SELECT id, google_id FROM users")
            users = cursor.fetchall()
            
            # Gerar e atualizar hash_id para cada usuário
            for user_id, google_id in users:
                if google_id:
                    # Gerar hash_id
                    hash_input = f"{google_id}{SALT}"
                    hash_id = hashlib.sha256(hash_input.encode()).hexdigest()
                    
                    # Atualizar usuário
                    cursor.execute("UPDATE users SET hash_id = ? WHERE id = ?", (hash_id, user_id))
                    print(f"Atualizado hash_id para usuário {user_id}")
            
            # Adicionar constraint de unicidade
            cursor.execute("CREATE UNIQUE INDEX idx_users_hash_id ON users(hash_id)")
            
            print("Migração concluída com sucesso!")
        
        # Verificar se as tabelas de negócio têm a coluna user_hash
        for table in ['negociacoes', 'acoes', 'relatorios', 'saldos_precos_medios']:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'user_hash' not in columns:
                print(f"Adicionando coluna user_hash à tabela {table}...")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN user_hash VARCHAR(64)")
                
                # Preencher user_hash com base no user_id
                cursor.execute(f"""
                    UPDATE {table} 
                    SET user_hash = (
                        SELECT hash_id FROM users WHERE users.id = {table}.user_id
                    )
                """)
                print(f"Atualizada coluna user_hash na tabela {table}")
        
        # Commit das alterações
        conn.commit()
        print("Todas as alterações foram aplicadas com sucesso!")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Erro durante a migração: {str(e)}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()
