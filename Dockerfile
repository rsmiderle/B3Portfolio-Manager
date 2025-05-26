# Dockerfile

# 1. Usar uma imagem base oficial do Python.
FROM python:3.12-slim

# 2. Definir variáveis de ambiente úteis
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Definir o diretório de trabalho dentro do container
WORKDIR /app

# 4. Copiar o arquivo de dependências primeiro para aproveitar o cache do Docker
COPY requirements.txt requirements.txt

# 5. Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar todo o código da aplicação para o diretório de trabalho (/app)
COPY . .

# 7. Expor a porta em que a aplicação Flask (via Gunicorn) irá rodar
EXPOSE 5000

# 8. Comando para iniciar a aplicação, executando primeiro as migrações
# Este comando executa o run.py que contém a lógica de automação das migrações
# antes de iniciar o servidor Gunicorn
CMD python run.py && gunicorn --bind "0.0.0.0:${PORT:-5000}" --workers 2 "src.main:create_app()"
