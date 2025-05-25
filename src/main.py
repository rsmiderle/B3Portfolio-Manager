from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from flask_login import LoginManager, current_user, login_required
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
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    
    # Garantir que a pasta de uploads exista
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Inicializar extensões
    db.init_app(app)
    csrf = CSRFProtect(app)
    
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
    
    # Criar tabelas do banco de dados
    with app.app_context():
        db.create_all()
    
    return app
