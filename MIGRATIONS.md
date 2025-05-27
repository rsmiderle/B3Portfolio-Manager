# Automação de Migrações do Banco de Dados

Este documento explica como as migrações do banco de dados são automatizadas no projeto B3 Portfolio Manager.

## Abordagem de Automação

As migrações do banco de dados são executadas automaticamente no momento da inicialização da aplicação, tanto em ambiente de desenvolvimento quanto em produção. Isso elimina a necessidade de executar comandos manuais e garante que o banco de dados esteja sempre atualizado.

## Como Funciona

1. **No arquivo run.py**:
   - Uma função `init_db()` verifica se o repositório de migrações existe
   - Se não existir, inicializa o repositório e cria a migração inicial
   - Aplica todas as migrações pendentes automaticamente
   - Esta função é executada antes de iniciar o servidor web

2. **No Dockerfile**:
   - O comando de entrada (ENTRYPOINT) executa o run.py
   - Isso garante que as migrações sejam aplicadas antes de iniciar o servidor
   - Não são necessárias etapas adicionais no Cloud Build

## Vantagens desta Abordagem

1. **Simplicidade**: Não requer etapas adicionais no pipeline de CI/CD
2. **Robustez**: Funciona em qualquer ambiente (local, Cloud Run, etc.)
3. **Segurança**: As migrações são executadas dentro do container, com acesso às variáveis de ambiente e dependências corretas
4. **Consistência**: O banco de dados é sempre atualizado antes de iniciar a aplicação

## Resolução de Problemas

Se você encontrar erros relacionados ao banco de dados:

1. Verifique os logs da aplicação para mensagens de erro específicas
2. Certifique-se de que o banco de dados está acessível
3. Se necessário, execute manualmente os comandos de migração:
   ```
   flask db init
   flask db migrate -m "Migração inicial"
   flask db upgrade
   ```

## Importante para Produção

Em ambiente de produção (Cloud Run), as migrações são executadas automaticamente a cada implantação, garantindo que o esquema do banco de dados esteja sempre atualizado.
