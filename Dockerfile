# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instala dependencias del sistema

RUN apt-get update && apt-get install -y build-essential libpq-dev && apt-get clean
# --RUN apt-get update && apt-get install -y netcat-openbsd

# Copia requirements y los instala
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copia todo el código del proyecto
COPY . .

# Copia el archivo entrypoint.sh
# --COPY ./entrypoint.sh /app/entrypoint.sh
# --RUN chmod +x /app/entrypoint.sh


# Establece variables de entorno para Django
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expone el puerto para el contenedor
EXPOSE 8080

# Usa gunicorn para producción
# CMD gunicorn EMX_Users.wsgi:application --bind 0.0.0.0:$PORT
CMD ["gunicorn", "EMX_Users.wsgi:application", "--bind", "0.0.0.0:$PORT"]
# ENTRYPOINT ["./entrypoint.sh"]
# --ENTRYPOINT ["/app/entrypoint.sh"]

