import os
import urllib3
from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from src.models import db
from src.models.user import User
from src.routes.auth import auth_bp
from src.routes.main import main_bp
from src.routes.acoes import acoes_bp
from src.routes.negociacoes import negociacoes_bp
from src.routes.relatorios import relatorios_bp
from src.routes.saldos import saldos_bp
from src.routes.admin import admin_bp

def create_app():
    app = Flask(__name__)
    
    # Configuração do banco de dados
    if os.environ.get('DB_USE_MYSQL', 'false').lower() == 'true':
        # Configuração para MySQL (produção)
        print("Usando MySQL para produção")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
            os.environ.get('DB_USER', 'root'),
            os.environ.get('DB_PASSWORD', ''),
            os.environ.get('DB_HOST', 'localhost'),
            os.environ.get('DB_PORT', '3306'),
            os.environ.get('DB_NAME', 'b3portfolio')
        )
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_recycle': 280,
            'pool_timeout': 100,
            'pool_size': 10,
            'max_overflow': 5,
        }
    else:
        # Configuração para SQLite (desenvolvimento local)
        print("Usando SQLite para desenvolvimento local")
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', 'b3portfolio.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuração de segurança
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_change_in_production')
    
    # Configuração de upload
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Inicialização de extensões
    db.init_app(app)
    migrate = Migrate(app, db)
    csrf = CSRFProtect(app)
    
    # Configuração do login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Registro de blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(acoes_bp)
    app.register_blueprint(negociacoes_bp)
    app.register_blueprint(relatorios_bp)
    app.register_blueprint(saldos_bp)
    app.register_blueprint(admin_bp)
    
    # Adicionar link para o painel de administração no menu principal
    @app.context_processor
    def inject_admin_status():
        if current_user.is_authenticated:
            return {'is_admin': current_user.is_admin()}
        return {'is_admin': False}
    
    # Rota raiz
    @app.route('/')
    def index():
        return redirect(url_for('main.index'))
    
    return app
