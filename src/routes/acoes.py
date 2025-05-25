from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_wtf import FlaskForm
from flask_login import login_required, current_user
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from src.models import db
from src.models.all_models import Acao
import requests
from bs4 import BeautifulSoup

acoes_bp = Blueprint('acoes', __name__, url_prefix='/acoes')

class AcaoForm(FlaskForm):
    codigo = StringField('Código da Ação', validators=[DataRequired()])
    cnpj = StringField('CNPJ')
    nome_empresa = StringField('Nome da Empresa')
    submit = SubmitField('Salvar')

@acoes_bp.route('/', methods=['GET'])
@login_required
def listar():
    acoes = Acao.query.filter_by(user_id=current_user.id).all()
    return render_template('acoes/listar.html', acoes=acoes)

@acoes_bp.route('/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar():
    form = AcaoForm()
    if form.validate_on_submit():
        acao = Acao(
            codigo=form.codigo.data.upper(),
            cnpj=form.cnpj.data,
            nome_empresa=form.nome_empresa.data,
            user_id=current_user.id
        )
        
        # Verificar se já existe para este usuário
        acao_existente = Acao.query.filter_by(codigo=acao.codigo, user_id=current_user.id).first()
        if acao_existente:
            flash(f'A ação {acao.codigo} já está cadastrada!', 'warning')
            return redirect(url_for('acoes.listar'))
        
        db.session.add(acao)
        db.session.commit()
        flash(f'Ação {acao.codigo} cadastrada com sucesso!', 'success')
        return redirect(url_for('acoes.listar'))
    
    return render_template('acoes/cadastrar.html', form=form)

@acoes_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    acao = Acao.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = AcaoForm(obj=acao)
    
    if form.validate_on_submit():
        acao.codigo = form.codigo.data.upper()
        acao.cnpj = form.cnpj.data
        acao.nome_empresa = form.nome_empresa.data
        
        db.session.commit()
        flash(f'Ação {acao.codigo} atualizada com sucesso!', 'success')
        return redirect(url_for('acoes.listar'))
    
    return render_template('acoes/editar.html', form=form, acao=acao)

@acoes_bp.route('/buscar_cnpj/<codigo>')
@login_required
def buscar_cnpj(codigo):
    """Função para buscar CNPJ de uma ação na internet"""
    try:
        # Implementação básica - em produção seria necessário um serviço mais robusto
        url = f"https://www.google.com/search?q=cnpj+{codigo}+b3+bovespa"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Desabilitar verificação de SSL para contornar o problema de certificado
        response = requests.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Busca por padrões de CNPJ (XX.XXX.XXX/XXXX-XX)
        text = soup.get_text()
        import re
        cnpj_pattern = r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}'
        cnpj_matches = re.findall(cnpj_pattern, text)
        
        if cnpj_matches:
            return cnpj_matches[0]
        else:
            return "CNPJ não encontrado"
    except Exception as e:
        # Fallback para não interromper o fluxo do sistema
        print(f"Erro ao buscar CNPJ: {str(e)}")
        return "CNPJ não disponível"
