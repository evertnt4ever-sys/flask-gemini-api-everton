FROM python:3.12-slim

WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia o código
COPY appRCIA.py .

# Expõe a porta
EXPOSE 5000

# Comando para iniciar
CMD ["python", "appRCIA.py"]
