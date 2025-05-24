# Requisitos de Teste para o Sistema de Portfólio de Ações

## Testes de Correções Implementadas

### 1. Correção do CSRF Token
- **Objetivo**: Verificar se o formulário de geração de relatório está enviando o token CSRF corretamente
- **Passos**:
  1. Acessar a página de geração de relatório
  2. Selecionar uma data base
  3. Submeter o formulário
- **Resultado Esperado**: O formulário deve ser processado sem erros de CSRF token

### 2. Correção da Busca de CNPJ
- **Objetivo**: Verificar se a busca de CNPJ está funcionando mesmo com problemas de SSL
- **Passos**:
  1. Cadastrar uma ação sem CNPJ
  2. Clicar no botão "Buscar CNPJ"
  3. Verificar o resultado retornado
- **Resultado Esperado**: O sistema deve retornar o CNPJ encontrado ou uma mensagem de "CNPJ não disponível" sem interromper o fluxo

## Testes Gerais do Sistema

### 3. Upload de Relatório B3
- **Objetivo**: Verificar se o sistema processa corretamente os relatórios da B3
- **Passos**:
  1. Acessar a página de upload de relatório
  2. Selecionar um arquivo de relatório válido
  3. Submeter o formulário
- **Resultado Esperado**: O sistema deve processar o relatório e exibir as negociações

### 4. Cadastro de Saldo e Preço Médio
- **Objetivo**: Verificar se o sistema permite cadastrar saldos e preços médios
- **Passos**:
  1. Acessar a página de cadastro de saldo
  2. Preencher os campos obrigatórios
  3. Submeter o formulário
- **Resultado Esperado**: O sistema deve salvar o saldo e preço médio

### 5. Geração de Relatório
- **Objetivo**: Verificar se o sistema gera corretamente o relatório de posição
- **Passos**:
  1. Acessar a página de geração de relatório
  2. Selecionar uma data base
  3. Submeter o formulário
- **Resultado Esperado**: O sistema deve exibir o relatório com saldo, preço médio e CNPJ de cada ação

### 6. Cálculo de Preço Médio
- **Objetivo**: Verificar se o sistema calcula corretamente o preço médio
- **Passos**:
  1. Fazer upload de um relatório com operações de compra e venda
  2. Gerar um relatório para uma data após as operações
- **Resultado Esperado**: O preço médio deve ser calculado conforme as regras (reinício após zerar o saldo)

### 7. Integração com Busca de CNPJ
- **Objetivo**: Verificar se o sistema busca e exibe o CNPJ das ações
- **Passos**:
  1. Gerar um relatório com ações que não têm CNPJ cadastrado
- **Resultado Esperado**: O sistema deve tentar buscar o CNPJ online e exibi-lo no relatório

## Observações
- Os testes devem ser executados em um ambiente similar ao de produção
- É importante verificar o comportamento do sistema com diferentes tipos de relatórios da B3
- Verificar se as mensagens de erro são claras e informativas para o usuário
