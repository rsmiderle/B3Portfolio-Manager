from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from flask_login import login_required, current_user
from wtforms import DateField, FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from src.models import db
from src.models.all_models import SaldoPrecoMedio, Acao
from datetime import datetime

saldos_bp = Blueprint('saldos', __name__, url_prefix='/saldos')

class SaldoPrecoMedioForm(FlaskForm):
    acao_id = SelectField('Ação', coerce=int, validators=[DataRequired()])
    data_base = DateField('Data Base', validators=[DataRequired()], format='%Y-%m-%d')
    quantidade = IntegerField('Quantidade', validators=[DataRequired(), NumberRange(min=0)])
    preco_medio = FloatField('Preço Médio', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Salvar')

@saldos_bp.route('/', methods=['GET'])
@login_required
def listar():
    saldos = SaldoPrecoMedio.query.filter_by(user_id=current_user.id).order_by(SaldoPrecoMedio.data_base.desc()).all()
    return render_template('saldos/listar.html', saldos=saldos)

@saldos_bp.route('/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar():
    form = SaldoPrecoMedioForm()
    # Preencher as opções do dropdown de ações - apenas ações do usuário atual
    form.acao_id.choices = [(a.id, a.codigo) for a in Acao.query.filter_by(user_id=current_user.id).order_by(Acao.codigo).all()]
    
    if form.validate_on_submit():
        # Verificar se a ação pertence ao usuário atual
        acao = Acao.query.filter_by(id=form.acao_id.data, user_id=current_user.id).first()
        if not acao:
            flash('Ação não encontrada ou não pertence ao seu cadastro!', 'danger')
            return redirect(url_for('saldos.listar'))
            
        # Verificar se já existe um saldo para esta ação nesta data para este usuário
        saldo_existente = SaldoPrecoMedio.query.filter_by(
            acao_id=form.acao_id.data,
            data_base=form.data_base.data,
            user_id=current_user.id
        ).first()
        
        if saldo_existente:
            flash(f'Já existe um saldo cadastrado para esta ação nesta data!', 'warning')
            return redirect(url_for('saldos.listar'))
        
        saldo = SaldoPrecoMedio(
            acao_id=form.acao_id.data,
            data_base=form.data_base.data,
            quantidade=form.quantidade.data,
            preco_medio=form.preco_medio.data,
            user_id=current_user.id
        )
        
        db.session.add(saldo)
        db.session.commit()
        flash('Saldo e preço médio cadastrados com sucesso!', 'success')
        return redirect(url_for('saldos.listar'))
    
    return render_template('saldos/cadastrar.html', form=form)

@saldos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    # Garantir que o saldo pertence ao usuário atual
    saldo = SaldoPrecoMedio.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = SaldoPrecoMedioForm(obj=saldo)
    # Mostrar apenas ações do usuário atual
    form.acao_id.choices = [(a.id, a.codigo) for a in Acao.query.filter_by(user_id=current_user.id).order_by(Acao.codigo).all()]
    
    if form.validate_on_submit():
        # Verificar se a ação pertence ao usuário atual
        acao = Acao.query.filter_by(id=form.acao_id.data, user_id=current_user.id).first()
        if not acao:
            flash('Ação não encontrada ou não pertence ao seu cadastro!', 'danger')
            return redirect(url_for('saldos.listar'))
            
        # Verificar se já existe outro saldo para esta ação nesta data (exceto o atual)
        saldo_existente = SaldoPrecoMedio.query.filter(
            SaldoPrecoMedio.acao_id == form.acao_id.data,
            SaldoPrecoMedio.data_base == form.data_base.data,
            SaldoPrecoMedio.id != id,
            SaldoPrecoMedio.user_id == current_user.id
        ).first()
        
        if saldo_existente:
            flash(f'Já existe outro saldo cadastrado para esta ação nesta data!', 'warning')
            return redirect(url_for('saldos.listar'))
        
        saldo.acao_id = form.acao_id.data
        saldo.data_base = form.data_base.data
        saldo.quantidade = form.quantidade.data
        saldo.preco_medio = form.preco_medio.data
        
        db.session.commit()
        flash('Saldo e preço médio atualizados com sucesso!', 'success')
        return redirect(url_for('saldos.listar'))
    
    return render_template('saldos/editar.html', form=form, saldo=saldo)

@saldos_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def excluir(id):
    # Garantir que o saldo pertence ao usuário atual
    saldo = SaldoPrecoMedio.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(saldo)
    db.session.commit()
    flash('Saldo excluído com sucesso!', 'success')
    return redirect(url_for('saldos.listar'))
