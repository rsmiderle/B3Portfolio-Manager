# Migração Automática de Banco de Dados no Deploy

Este documento explica como as migrações de banco de dados são aplicadas automaticamente durante o deploy do B3Portfolio-Manager-IA, garantindo que o esquema do banco esteja sempre atualizado sem intervenção manual.

## Implementação Atual

O projeto já possui uma implementação robusta para aplicar migrações automaticamente em todos os ambientes:

### 1. Arquivo `run.py`

O arquivo `run.py` contém a função `init_db()` que:

- Verifica se o diretório de migrações existe, criando-o se necessário
- Verifica se há arquivos de migração, criando a migração inicial se necessário
- Aplica todas as migrações pendentes usando `flask db upgrade`
- Trata erros e fornece mensagens informativas

Esta função é executada automaticamente quando a aplicação é iniciada, tanto em ambiente de desenvolvimento quanto em produção.

### 2. Dockerfile

O Dockerfile está configurado para executar o `run.py` antes de iniciar o servidor Gunicorn:

```dockerfile
CMD python run.py && gunicorn --bind "0.0.0.0:${PORT:-5000}" --workers 2 "src.main:create_app()"
```

Isso garante que as migrações sejam aplicadas antes que a aplicação comece a receber tráfego, evitando erros de esquema desatualizado.

### 3. Cloud Build

O arquivo `cloudbuild.yaml` constrói e implanta a imagem Docker, que por sua vez executa o `run.py` durante a inicialização, garantindo que as migrações sejam aplicadas em cada deploy.

## Recomendações para Melhorias

Embora a implementação atual seja funcional, sugiro algumas melhorias para aumentar a robustez e observabilidade:

### 1. Melhorar o Logging

Adicionar logs mais detalhados durante o processo de migração para facilitar o diagnóstico de problemas:

```python
def init_db():
    """Inicializa o banco de dados automaticamente executando as migrações"""
    with app.app_context():
        print("=== INICIANDO PROCESSO DE MIGRAÇÃO DE BANCO DE DADOS ===")
        # ... código existente ...
        print(f"=== MIGRAÇÃO CONCLUÍDA COM SUCESSO EM {datetime.now().isoformat()} ===")
```

### 2. Implementar Verificação de Saúde Pós-Migração

Adicionar uma verificação básica após a migração para confirmar que o banco está funcional:

```python
def verificar_saude_banco():
    """Verifica se o banco de dados está funcionando corretamente após a migração"""
    try:
        # Tenta executar uma consulta simples
        db.session.execute(text("SELECT 1"))
        print("Verificação de saúde do banco: OK")
        return True
    except Exception as e:
        print(f"Verificação de saúde do banco: FALHA - {e}")
        return False
```

### 3. Adicionar Timeout e Retry para Migrações

Em ambientes de produção, pode ser útil adicionar um mecanismo de retry para lidar com problemas temporários de conexão:

```python
def aplicar_migracoes_com_retry(max_tentativas=3, intervalo=5):
    """Aplica migrações com mecanismo de retry"""
    for tentativa in range(1, max_tentativas + 1):
        try:
            print(f"Tentativa {tentativa}/{max_tentativas} de aplicar migrações...")
            subprocess.run(["flask", "db", "upgrade"], env=env, check=True, timeout=60)
            print("Migrações aplicadas com sucesso!")
            return True
        except Exception as e:
            print(f"Erro ao aplicar migrações: {e}")
            if tentativa < max_tentativas:
                print(f"Aguardando {intervalo} segundos antes de tentar novamente...")
                time.sleep(intervalo)
            else:
                print("Número máximo de tentativas excedido.")
                raise
```

### 4. Monitoramento em Produção

Configurar alertas para falhas de migração em produção:

- Integrar com sistemas de monitoramento como Stackdriver ou Sentry
- Configurar alertas para erros durante a inicialização do container
- Implementar endpoints de health check que verifiquem a versão do banco

## Boas Práticas para Manutenção

1. **Sempre teste migrações localmente** antes de fazer deploy em produção
2. **Faça backup do banco** antes de aplicar migrações complexas
3. **Mantenha as migrações idempotentes** (podem ser executadas múltiplas vezes sem efeitos colaterais)
4. **Evite migrações que bloqueiam tabelas** por longos períodos em produção
5. **Documente alterações significativas** no esquema do banco

## Conclusão

O sistema atual já implementa a aplicação automática de migrações durante o deploy, garantindo que o esquema do banco de dados esteja sempre atualizado. As melhorias sugeridas visam aumentar a robustez e observabilidade desse processo, especialmente em ambientes de produção com alta disponibilidade.
