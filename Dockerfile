
# Utiliza uma imagem oficial do Python
FROM python:3.12-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências
COPY requirements.txt .

# Instala as dependências da aplicação
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos do projeto
COPY app.py .

# Expõe a porta utilizada pela aplicação
EXPOSE 5000

# Inicia o servidor Flask
CMD ["python", "app.py"]
