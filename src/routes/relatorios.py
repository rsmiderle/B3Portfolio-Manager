from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_wtf import FlaskForm
from flask_login import login_required, current_user
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os
import pandas as pd
from datetime import datetime
from src.models import db
from src.models.all_models import Relatorio, Negociacao, Acao

relatorios_bp = Blueprint('relatorios', __name__, url_prefix='/relatorios')

class RelatorioForm(FlaskForm):
    arquivo = FileField('Arquivo de Relatório B3', validators=[DataRequired()])
    submit = SubmitField('Enviar')

@relatorios_bp.route('/', methods=['GET'])
@login_required
def listar():
    relatorios = Relatorio.query.filter_by(user_id=current_user.id).order_by(Relatorio.data_upload.desc()).all()
    return render_template('relatorios/listar.html', relatorios=relatorios)

@relatorios_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = RelatorioForm()
    if form.validate_on_submit():
        arquivo = form.arquivo.data
        if arquivo:
            filename = secure_filename(arquivo.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            arquivo.save(filepath)
            
            # Criar registro do relatório
            relatorio = Relatorio(
                nome_arquivo=filename,
                user_id=current_user.id
            )
            db.session.add(relatorio)
            db.session.commit()
            
            # Processar o arquivo
            try:
                processar_relatorio(filepath, relatorio.id)
                flash('Relatório enviado e processado com sucesso!', 'success')
            except Exception as e:
                db.session.delete(relatorio)
                db.session.commit()
                flash(f'Erro ao processar o relatório: {str(e)}', 'danger')
                
            return redirect(url_for('relatorios.listar'))
    
    return render_template('relatorios/upload.html', form=form)

def processar_relatorio(filepath, relatorio_id):
    """Processa o arquivo de relatório da B3 e salva as negociações no banco de dados"""
    # Ler o arquivo Excel
    df = pd.read_excel(filepath)
    
    # Obter o relatório para acessar o user_id
    relatorio = Relatorio.query.get(relatorio_id)
    
    # Processar cada linha do relatório
    for _, row in df.iterrows():
        # Converter a data para o formato correto
        data_str = row['Data do Negócio']
        if isinstance(data_str, str):
            data = datetime.strptime(data_str, '%d/%m/%Y').date()
        else:
            data = data_str.date()
        
        # Verificar se a ação já existe, se não, criar
        codigo_acao = row['Código de Negociação']
        
        # Remover a letra F do final do código da ação, se existir
        if codigo_acao.endswith('F'):
            codigo_acao = codigo_acao[:-1]
            
        acao = Acao.query.filter_by(codigo=codigo_acao, user_id=relatorio.user_id).first()
        if not acao:
            acao = Acao(
                codigo=codigo_acao,
                user_id=relatorio.user_id
            )
            db.session.add(acao)
            db.session.commit()
        
        # Criar a negociação
        negociacao = Negociacao(
            data_negocio=data,
            tipo_movimentacao=row['Tipo de Movimentação'],
            mercado=row['Mercado'],
            prazo_vencimento=row['Prazo/Vencimento'],
            instituicao=row['Instituição'],
            quantidade=row['Quantidade'],
            preco=row['Preço'],
            valor=row['Valor'],
            acao_id=acao.id,
            relatorio_id=relatorio_id,
            user_id=relatorio.user_id
        )
        
        db.session.add(negociacao)
    
    db.session.commit()

@relatorios_bp.route('/detalhes/<int:id>', methods=['GET'])
@login_required
def detalhes(id):
    relatorio = Relatorio.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    negociacoes = Negociacao.query.filter_by(relatorio_id=id, user_id=current_user.id).all()
    return render_template('relatorios/detalhes.html', relatorio=relatorio, negociacoes=negociacoes)
