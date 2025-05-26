from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from flask_login import LoginManager, current_user, login_required
from flask_migrate import Migrate
from wtforms import StringField, DateField, FloatField, IntegerField, SubmitField, FileField
from wtforms.validators import DataRequired, Optional
import os
from datetime import datetime
import pandas as pd
from src.models import db
from src.models.all_models import Acao, Negociacao, Relatorio, SaldoPrecoMedio, User

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
    
    # Configuração condicional do banco de dados baseada no ambiente
    if os.environ.get('DB_USE_MYSQL', 'False').lower() == 'true':
        # Configuração para MySQL (Google Cloud SQL)
        db_user = os.environ.get('DB_USER', 'root')
        db_password = os.environ.get('DB_PASSWORD', '')
        db_host = os.environ.get('DB_HOST', '127.0.0.1')
        db_port = os.environ.get('DB_PORT', '3306')
        db_name = os.environ.get('DB_NAME', 'portfolio')
        
        # Construir URI de conexão MySQL
        app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        # Configurações adicionais para MySQL
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 5,
            'pool_timeout': 30,
            'pool_recycle': 1800,  # Reconectar após 30 minutos
        }
        
        print(f"Usando MySQL em {db_host}:{db_port}/{db_name}")
    else:
        # Configuração para SQLite (desenvolvimento local)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
        print("Usando SQLite para desenvolvimento local")
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    
    # Configuração condicional de URL scheme baseada no ambiente
    if os.environ.get('FLASK_ENV') == 'production' or not app.debug:
        app.config['PREFERRED_URL_SCHEME'] = 'https'
    else:
        app.config['PREFERRED_URL_SCHEME'] = 'http'
    
    # Garantir que a pasta de uploads exista
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Inicializar extensões
    db.init_app(app)
    csrf = CSRFProtect(app)
    
    # Inicializar Flask-Migrate
    migrate = Migrate(app, db)
    
    # Configurar Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Importar e registrar blueprints
    from src.routes.main import main_bp
    from src.routes.acoes import acoes_bp
    from src.routes.relatorios import relatorios_bp
    from src.routes.saldos import saldos_bp
    from src.routes.negociacoes import negociacoes_bp
    from src.routes.auth import auth_bp
    from src.routes.test import test_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(acoes_bp)
    app.register_blueprint(relatorios_bp)
    app.register_blueprint(saldos_bp)
    app.register_blueprint(negociacoes_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(test_bp)
    
    # Não criamos mais as tabelas diretamente aqui
    # As migrações serão responsáveis por isso
    
    return app
