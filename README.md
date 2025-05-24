# Sistema de Portfólio de Ações - Documentação

## Visão Geral

Este sistema foi 100% desenvolvido com uso de IA generativa e tem como objetivo ajudar o usuário a gerenciar um portfólio de ações e automatizar os cálculos para declaração do IRPF com base em relatórios de negociações da B3.
Nenhuma linha de código foi escrita por mim nessa primeira versão. Todo o código foi gerado por IA como parte de uma prova de conceito particular minha. 
Também pretendo evoluir o produto e realizar correções utilizando apenas ferramentas de IA. 

O sistema permite:

1. Upload de relatórios de negociações da B3 em formato Excel (.xlsx)
2. Cadastro de saldos e preços médios de ações em datas base específicas
3. Cadastro de ações e seus CNPJs
4. Geração de relatórios de posição em datas base específicas
5. Busca automática de CNPJ para ações não cadastradas

## Requisitos

- Python 3.11 ou superior
- Bibliotecas Python (instaladas automaticamente):
  - Flask
  - Flask-SQLAlchemy
  - Flask-WTF
  - Pandas
  - Openpyxl
  - Requests
  - BeautifulSoup4
  - Python-dotenv

## Instalação

1. Clone o repositório ou extraia os arquivos para uma pasta
2. Crie um ambiente virtual Python:
   ```
   python -m venv venv
   ```
3. Ative o ambiente virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
5. Execute o aplicativo:
   ```
   python run.py
   ```
6. Acesse o sistema no navegador: `http://localhost:5000`

## Estrutura do Projeto

```
portfolio_acoes/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── all_models.py
│   │   ├── acao.py
│   │   ├── negociacao.py
│   │   ├── relatorio.py
│   │   └── saldo_preco_medio.py
│   ├── routes/
│   │   ├── acoes.py
│   │   ├── main.py
│   │   ├── relatorios.py
│   │   └── saldos.py
│   ├── static/
│   ├── templates/
│   │   ├── acoes/
│   │   ├── relatorios/
│   │   ├── saldos/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── gerar_relatorio.html
│   │   └── relatorio_resultado.html
│   └── main.py
├── uploads/
├── venv/
├── run.py
└── requirements.txt
```

## Funcionalidades

### 1. Upload de Relatórios B3

- Acesse "Relatórios" > "Upload de Relatório"
- Selecione um arquivo Excel (.xlsx) contendo o relatório de negociações da B3
- O sistema processará automaticamente o arquivo e extrairá as negociações

### 2. Cadastro de Ações e CNPJ

- Acesse "Ações" > "Cadastrar Nova Ação"
- Preencha o código da ação (ex: PETR4)
- Opcionalmente, informe o nome da empresa e o CNPJ
- Se o CNPJ não for informado, você pode usar a função "Buscar CNPJ" posteriormente

### 3. Cadastro de Saldos e Preços Médios

- Acesse "Saldos" > "Cadastrar Novo Saldo"
- Selecione a ação, informe a data base, quantidade e preço médio
- Este cadastro será considerado como ponto de partida para cálculos futuros

### 4. Geração de Relatórios

- Acesse "Gerar Relatório"
- Informe a data base para a qual deseja calcular a posição das ações
- O sistema calculará o saldo e preço médio de cada ação na data informada
- O relatório exibirá o código da ação, quantidade, preço médio e CNPJ

## Lógica de Cálculo

- O sistema considera todas as negociações (compras e vendas) até a data base informada
- Para cada ação, o sistema busca o saldo mais recente cadastrado antes da data base
- O preço médio é calculado considerando apenas as operações de compra
- Quando o saldo de uma ação é zerado, o preço médio é reiniciado
- O sistema busca automaticamente o CNPJ de ações não cadastradas

## Observações

- O sistema utiliza SQLite como banco de dados por padrão
- Os relatórios enviados são armazenados na pasta "uploads"
- Para ambientes de produção, recomenda-se configurar um banco de dados mais robusto
