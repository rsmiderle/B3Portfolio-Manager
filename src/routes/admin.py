from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import DataRequired
import subprocess
import os
from datetime import datetime
from src.models import db
from sqlalchemy import text, func
from src.models.all_models import User, Negociacao

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

class MigrationForm(FlaskForm):
    submit = SubmitField('Executar Migrações')

@admin_bp.route('/', methods=['GET'])
@login_required
def index():
    """Página inicial do painel de administração"""
    # Verificar se o usuário é administrador
    if not current_user.is_admin():
        flash('Acesso negado. Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('main.index'))
    
    # Obter informações sobre o banco de dados
    db_info = get_db_info()
    
    # Obter informações sobre as migrações
    migration_info = get_migration_info()
    
    # Obter estatísticas do sistema
    system_stats = get_system_stats()
    
    return render_template('admin/index.html', 
                          db_info=db_info,
                          migration_info=migration_info,
                          system_stats=system_stats)

@admin_bp.route('/migrations', methods=['GET', 'POST'])
@login_required
def migrations():
    """Página para gerenciar migrações do banco de dados"""
    # Verificar se o usuário é administrador
    if not current_user.is_admin():
        flash('Acesso negado. Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('main.index'))
    
    form = MigrationForm()
    
    # Obter informações sobre as migrações
    migration_info = get_migration_info()
    
    if form.validate_on_submit():
        # Executar migrações
        result = run_migrations()
        
        if result['success']:
            flash(f'Migrações executadas com sucesso! {result["message"]}', 'success')
        else:
            flash(f'Erro ao executar migrações: {result["message"]}', 'danger')
        
        # Atualizar informações sobre as migrações após a execução
        migration_info = get_migration_info()
    
    return render_template('admin/migrations.html', 
                          form=form,
                          migration_info=migration_info)

def get_system_stats():
    """Obtém estatísticas do sistema"""
    stats = {
        'total_users': 0,
        'total_transactions_value': 0,
        'total_transactions': 0,
        'avg_transaction_value': 0
    }
    
    try:
        with current_app.app_context():
            # Contar número total de usuários
            stats['total_users'] = User.query.count()
            
            # Calcular valor total de todas as negociações
            result = db.session.query(
                func.sum(Negociacao.valor).label('total_value'),
                func.count(Negociacao.id).label('total_count')
            ).first()
            
            if result and result.total_value:
                stats['total_transactions_value'] = float(result.total_value)
                stats['total_transactions'] = int(result.total_count)
                
                if stats['total_transactions'] > 0:
                    stats['avg_transaction_value'] = stats['total_transactions_value'] / stats['total_transactions']
            
    except Exception as e:
        current_app.logger.error(f"Erro ao obter estatísticas do sistema: {str(e)}")
    
    return stats

def get_db_info():
    """Obtém informações sobre o banco de dados"""
    info = {
        'type': 'Desconhecido',
        'tables': [],
        'status': 'Desconhecido'
    }
    
    try:
        with current_app.app_context():
            # Verificar o tipo de banco de dados
            if 'sqlite' in current_app.config['SQLALCHEMY_DATABASE_URI']:
                info['type'] = 'SQLite'
                
                # Obter lista de tabelas
                result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
                info['tables'] = [row[0] for row in result if not row[0].startswith('sqlite_')]
                
            else:
                info['type'] = 'MySQL'
                
                # Obter lista de tabelas
                result = db.session.execute(text("SHOW TABLES")).fetchall()
                info['tables'] = [row[0] for row in result]
            
            # Verificar status do banco
            db.session.execute(text("SELECT 1"))
            info['status'] = 'Conectado'
            
    except Exception as e:
        info['status'] = f'Erro: {str(e)}'
    
    return info

def get_migration_info():
    """Obtém informações sobre as migrações"""
    info = {
        'has_migrations': False,
        'versions': [],
        'current_version': 'Nenhuma',
        'last_migration_date': 'Nunca'
    }
    
    # Verificar se o diretório de migrações existe
    migrations_dir = os.path.join(current_app.root_path, '..', 'migrations')
    if not os.path.exists(migrations_dir):
        return info
    
    info['has_migrations'] = True
    
    # Verificar se há arquivos de migração
    versions_dir = os.path.join(migrations_dir, 'versions')
    if not os.path.exists(versions_dir):
        return info
    
    # Obter lista de versões
    try:
        for filename in os.listdir(versions_dir):
            if filename.endswith('.py'):
                version_id = filename.split('_')[0]
                
                # Ler o arquivo para obter a descrição
                with open(os.path.join(versions_dir, filename), 'r') as f:
                    content = f.read()
                    
                    # Extrair a descrição da migração
                    description = 'Sem descrição'
                    for line in content.split('\n'):
                        if 'revision =' in line and 'down_revision' not in line:
                            revision = line.split('=')[1].strip().strip('"\'')
                        if 'Revision ID:' in line:
                            revision = line.split(':')[1].strip()
                        if '"""' in line and 'Create' not in line and 'Alembic' not in line:
                            description = line.strip(' "\'')
                            break
                
                # Obter data de modificação do arquivo
                mod_time = os.path.getmtime(os.path.join(versions_dir, filename))
                mod_date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
                
                info['versions'].append({
                    'id': version_id,
                    'filename': filename,
                    'description': description,
                    'date': mod_date
                })
        
        # Ordenar versões por ID
        info['versions'].sort(key=lambda x: x['id'])
        
        # Obter versão atual
        if info['versions']:
            info['current_version'] = info['versions'][-1]['id']
            info['last_migration_date'] = info['versions'][-1]['date']
    
    except Exception as e:
        info['error'] = str(e)
    
    return info

def run_migrations():
    """Executa as migrações do banco de dados"""
    result = {
        'success': False,
        'message': ''
    }
    
    try:
        # Definir variáveis de ambiente para os comandos Flask
        env = os.environ.copy()
        env['FLASK_APP'] = 'run.py'
        
        # Verificar se o diretório de migrações existe
        migrations_dir = os.path.join(current_app.root_path, '..', 'migrations')
        if not os.path.exists(migrations_dir):
            # Inicializar repositório de migrações
            subprocess.run(["flask", "db", "init"], env=env, check=True)
            result['message'] += "Repositório de migrações inicializado. "
            
        # Verificar se há arquivos de migração
        versions_dir = os.path.join(migrations_dir, 'versions')
        if not os.path.exists(versions_dir) or not os.listdir(versions_dir):
            # Criar migração inicial
            subprocess.run(["flask", "db", "migrate", "-m", "Migração inicial automática"], env=env, check=True)
            result['message'] += "Migração inicial criada. "
        
        # Aplicar migrações pendentes
        output = subprocess.run(["flask", "db", "upgrade"], env=env, check=True, 
                              capture_output=True, text=True)
        
        if "No migrations to apply" in output.stdout:
            result['message'] += "Não há migrações pendentes para aplicar."
        else:
            result['message'] += "Migrações aplicadas com sucesso."
        
        result['success'] = True
        
    except subprocess.CalledProcessError as e:
        result['message'] = f"Erro ao executar comando: {e.stderr if e.stderr else str(e)}"
    except Exception as e:
        result['message'] = f"Erro inesperado: {str(e)}"
    
    return result
