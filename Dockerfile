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

# 7. Copiar o script de entrypoint e torná-lo executável
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 8. Expor a porta em que a aplicação Flask (via Gunicorn) irá rodar
EXPOSE 8080

# 9. Usar o script de entrypoint para gerenciar migrações e iniciar a aplicação
ENTRYPOINT ["/app/entrypoint.sh"]
