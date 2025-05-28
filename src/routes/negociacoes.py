from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from flask_login import login_required, current_user
from wtforms import FloatField, HiddenField, BooleanField, SubmitField
from wtforms.validators import Optional
from src.models import db
from src.models.all_models import Negociacao, Acao

negociacoes_bp = Blueprint('negociacoes', __name__, url_prefix='/negociacoes')

class NegociacaoForm(FlaskForm):
    id = HiddenField('ID')
    corretagem = FloatField('Valor de Corretagem', validators=[Optional()])
    submit = SubmitField('Salvar')

@negociacoes_bp.route('/', methods=['GET'])
@login_required
def listar():
    # Parâmetro para filtrar apenas negociações sem corretagem
    filtro_sem_corretagem = request.args.get('sem_corretagem', 'false') == 'true'
    
    # Consulta base - filtrar apenas negociações do usuário atual
    query = Negociacao.query.join(Acao, Negociacao.acao_id == Acao.id).filter(Negociacao.user_hash == current_user.hash_id)
    
    # Aplicar filtro se solicitado
    if filtro_sem_corretagem:
        query = query.filter(Negociacao.corretagem == None)
    
    # Ordenar por data mais recente
    negociacoes = query.order_by(Negociacao.data_negocio.desc()).all()
    
    return render_template('negociacoes/listar.html', 
                          negociacoes=negociacoes, 
                          filtro_sem_corretagem=filtro_sem_corretagem)

@negociacoes_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    # Garantir que a negociação pertence ao usuário atual
    negociacao = Negociacao.query.filter_by(id=id, user_hash=current_user.hash_id).first_or_404()
    form = NegociacaoForm(obj=negociacao)
    
    if form.validate_on_submit():
        negociacao.corretagem = form.corretagem.data
        db.session.commit()
        flash('Valor de corretagem atualizado com sucesso!', 'success')
        return redirect(url_for('negociacoes.listar'))
    
    return render_template('negociacoes/editar.html', form=form, negociacao=negociacao)
