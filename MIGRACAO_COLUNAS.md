# Instruções para Migração do Banco de Dados

Este documento contém instruções para aplicar as alterações no tamanho das colunas criptografadas no banco de dados MySQL.

## Problema Resolvido

O erro `Data too long for column 'mercado' at row 1` ocorria porque os dados criptografados ocupam mais espaço do que os dados originais, e o tamanho das colunas no MySQL não era suficiente para armazenar os valores criptografados.

## Alterações Realizadas

Aumentamos o tamanho de todas as colunas criptografadas nos modelos:

1. **Negociacao**:
   - tipo_movimentacao: de String(100) para String(512)
   - mercado: de String(100) para String(512)
   - prazo_vencimento: de String(100) para String(512)
   - instituicao: de String(200) para String(512)

2. **Acao**:
   - codigo: de String(100) para String(512)
   - cnpj: de String(100) para String(512)

3. **Relatorio**:
   - nome_arquivo: de String(200) para String(512)

4. **SaldoPrecoMedio**:
   - quantidade: de String(100) para String(512)
   - preco_medio: de String(100) para String(512)

## Como Aplicar a Migração

### Em Ambiente de Desenvolvimento

1. Execute os comandos do Flask-Migrate para gerar e aplicar a migração:

```bash
flask db migrate -m "Aumentar tamanho das colunas criptografadas"
flask db upgrade
```

### Em Ambiente de Produção

1. Gere a migração em ambiente de desenvolvimento:

```bash
flask db migrate -m "Aumentar tamanho das colunas criptografadas"
```

2. Revise o arquivo de migração gerado para garantir que apenas as alterações de tamanho de coluna estejam incluídas.

3. Aplique a migração no ambiente de produção:

```bash
flask db upgrade
```

4. Alternativamente, você pode executar os seguintes comandos SQL diretamente no banco de dados MySQL:

```sql
ALTER TABLE negociacoes 
    MODIFY COLUMN tipo_movimentacao VARCHAR(512) NOT NULL,
    MODIFY COLUMN mercado VARCHAR(512) NOT NULL,
    MODIFY COLUMN prazo_vencimento VARCHAR(512) NOT NULL,
    MODIFY COLUMN instituicao VARCHAR(512) NOT NULL;

ALTER TABLE acoes 
    MODIFY COLUMN codigo VARCHAR(512) NOT NULL,
    MODIFY COLUMN cnpj VARCHAR(512) NULL;

ALTER TABLE relatorios 
    MODIFY COLUMN nome_arquivo VARCHAR(512) NOT NULL;

ALTER TABLE saldos_precos_medios 
    MODIFY COLUMN quantidade VARCHAR(512) NOT NULL,
    MODIFY COLUMN preco_medio VARCHAR(512) NOT NULL;
```

## Observações Importantes

1. Faça backup do banco de dados antes de aplicar a migração.
2. Teste a migração em ambiente de desenvolvimento antes de aplicar em produção.
3. Se houver dados existentes, eles serão preservados durante a migração.
4. Após a migração, verifique se a importação de relatórios funciona corretamente.
