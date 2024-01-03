# Usa la imagen base oficial de Python
FROM python:3.9

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo requirements.txt al contenedor
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el contenido del directorio actual al contenedor
COPY config.py .
COPY fillments.py .
COPY programa.py .


# Define el comando predeterminado para ejecutar tu aplicación
CMD python fillments.py && python programa.py

