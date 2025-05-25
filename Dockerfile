# Dockerfile (Reiterando a versão correta e mais adequada)

# 1. Usar uma imagem base oficial do Python.
FROM python:3.9-slim 

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
# O Gunicorn será configurado para rodar na porta 5000 (ou a porta definida por PORT no Cloud Run)
# A porta exposta aqui é mais para documentação e para o Docker saber qual porta mapear por padrão se usar -P
EXPOSE 5000

# 8. Comando para executar a aplicação com Gunicorn (para produção)
# Gunicorn precisa ser instruído a chamar a factory 'create_app()' no módulo 'src.main'.
# Se você for implantar no Cloud Run, ele define a variável de ambiente PORT.
# Gunicorn respeitará essa variável se você usar $PORT no bind.
# Se PORT não estiver definida (como ao rodar localmente com docker run),
# você pode definir um padrão, ou o Gunicorn usará 8000 por padrão se nenhuma porta for especificada no bind.
# Para alinhar com o seu run.py, vamos usar 5000 como padrão, mas permitir que $PORT a substitua.
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT:-5000}", "--workers", "2", "src.main:create_app()"]