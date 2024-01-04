# Usa una imagen base de Python
FROM python:3.9

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el contenido actual al contenedor en /app
COPY . .

# Instala las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Ejecuta los scripts de Python
CMD ["bash", "-c", "python /app/fillments.py && python /app/programa.py"]


