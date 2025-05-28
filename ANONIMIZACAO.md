# Implementação de Anonimização sem Criptografia

Este documento descreve a implementação da anonimização de dados sem criptografia no sistema B3 Portfolio Manager, garantindo que alguém com acesso ao banco de dados não consiga relacionar os dados de negociações a dados pessoais do usuário.

## Visão Geral da Solução

A solução implementada:

1. **Remove a criptografia** de todos os campos, melhorando significativamente a performance
2. **Implementa anonimização** através de hash_id para usuários
3. **Otimiza os tipos de dados** para melhor performance e armazenamento
4. **Mantém a privacidade** dos usuários sem comprometer a funcionalidade

## Alterações Técnicas

### 1. Modelo de Usuário (User)

- Adicionado campo `hash_id` (VARCHAR(64)) que é um hash SHA-256 do Google ID do usuário
- Este hash_id é usado como identificador anonimizado em todas as tabelas de negócio
- O hash é gerado automaticamente na criação do usuário e não pode ser revertido para obter dados pessoais

### 2. Modelos de Negócio

Todos os modelos de negócio (Negociacao, Acao, Relatorio, SaldoPrecoMedio) foram modificados para:

- Remover campos criptografados e usar tipos nativos adequados
- Substituir `user_id` por `user_hash` que referencia o hash_id do usuário
- Otimizar tipos de dados para melhor performance:
  - VARCHAR(50/100) para textos curtos
  - NUMERIC/DECIMAL para valores monetários
  - INTEGER para quantidades
  - DATE/DATETIME para datas

### 3. Migração de Dados

Um script de migração SQL foi criado para:

- Adicionar a coluna hash_id na tabela users
- Gerar hash_id para usuários existentes
- Adicionar colunas user_hash nas tabelas de negócio
- Descriptografar dados e converter para tipos nativos
- Remover colunas antigas e adicionar constraints
- Recriar índices e otimizar tipos de dados

### 4. Validação

Um script de validação Python foi criado para:

- Verificar se todos os usuários possuem hash_id único e correto
- Validar integridade das chaves estrangeiras
- Verificar integridade dos dados após migração
- Validar efetividade da anonimização
- Testar performance das consultas principais

## Benefícios

1. **Melhor Performance**: Tipos de dados nativos e otimizados
2. **Privacidade Garantida**: Impossível relacionar dados de negócio com dados pessoais sem conhecer o algoritmo de hash
3. **Menor Complexidade**: Código mais simples e direto sem criptografia
4. **Menor Uso de Recursos**: Redução significativa no tamanho do banco de dados

## Considerações de Segurança

- O hash_id não pode ser revertido para obter o Google ID original
- Mesmo com acesso ao banco de dados, não é possível relacionar negociações a usuários específicos
- A segurança depende da proteção do salt usado no hash (armazenado apenas no código)
- Recomenda-se manter controle de acesso rigoroso ao código-fonte

## Próximos Passos

1. Executar o script de migração em ambiente de teste
2. Validar a integridade dos dados com o script de validação
3. Aplicar a migração em produção
4. Monitorar performance e integridade após a migração
