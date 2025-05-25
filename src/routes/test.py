from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.models import db
from src.models.all_models import Acao, Negociacao, SaldoPrecoMedio, Relatorio

# Criar um blueprint para testes de isolamento de dados
test_bp = Blueprint('test', __name__, url_prefix='/test')

@test_bp.route('/validate_isolation')
@login_required
def validate_isolation():
    """
    Rota para validar o isolamento de dados entre usuários.
    Esta função verifica se todas as consultas estão corretamente filtradas por usuário.
    """
    results = {
        'acoes': {
            'status': 'OK',
            'message': 'Isolamento de ações verificado com sucesso'
        },
        'relatorios': {
            'status': 'OK',
            'message': 'Isolamento de relatórios verificado com sucesso'
        },
        'saldos': {
            'status': 'OK',
            'message': 'Isolamento de saldos verificado com sucesso'
        },
        'negociacoes': {
            'status': 'OK',
            'message': 'Isolamento de negociações verificado com sucesso'
        }
    }
    
    # Verificar isolamento de ações
    acoes_total = Acao.query.count()
    acoes_usuario = Acao.query.filter_by(user_id=current_user.id).count()
    if acoes_total > acoes_usuario:
        results['acoes'] = {
            'status': 'FALHA',
            'message': f'Existem ações de outros usuários no banco ({acoes_total} total, {acoes_usuario} do usuário)'
        }
    
    # Verificar isolamento de relatórios
    relatorios_total = Relatorio.query.count()
    relatorios_usuario = Relatorio.query.filter_by(user_id=current_user.id).count()
    if relatorios_total > relatorios_usuario:
        results['relatorios'] = {
            'status': 'FALHA',
            'message': f'Existem relatórios de outros usuários no banco ({relatorios_total} total, {relatorios_usuario} do usuário)'
        }
    
    # Verificar isolamento de saldos
    saldos_total = SaldoPrecoMedio.query.count()
    saldos_usuario = SaldoPrecoMedio.query.filter_by(user_id=current_user.id).count()
    if saldos_total > saldos_usuario:
        results['saldos'] = {
            'status': 'FALHA',
            'message': f'Existem saldos de outros usuários no banco ({saldos_total} total, {saldos_usuario} do usuário)'
        }
    
    # Verificar isolamento de negociações
    negociacoes_total = Negociacao.query.count()
    negociacoes_usuario = Negociacao.query.filter_by(user_id=current_user.id).count()
    if negociacoes_total > negociacoes_usuario:
        results['negociacoes'] = {
            'status': 'FALHA',
            'message': f'Existem negociações de outros usuários no banco ({negociacoes_total} total, {negociacoes_usuario} do usuário)'
        }
    
    return render_template('test_isolation.html', results=results)
