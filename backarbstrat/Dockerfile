# Etapa de construcción para el backend Django
FROM python:3.8 AS build
WORKDIR /app

# Copia solo los archivos necesarios para instalar dependencias
COPY requirements.txt .

# Instala dependencias
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Configurar variables de entorno
ARG SECRET_KEY
#Ethereum Address
ARG ETHEREUM_ADDRESS
ARG ETH_PRIVATE_KEY 
#KEYS - PRODUCTION
#MAINNET
ARG STARK_PRIVATE_KEY_MAINNET 
ARG DYDX_API_KEY_MAINNET 
ARG DYDX_API_SECRET_MAINNET 
ARG DYDX_API_PASSPHRASE_MAINNET 
#KEYS - DEVELOPMENT
# Must be on Testnet
ARG STARK_PRIVATE_KEY_TESTNET 
ARG DYDX_API_KEY_TESTNET 
ARG DYDX_API_SECRET_TESTNET 
ARG DYDX_API_PASSPHRASE_TESTNET 

ENV SECRET_KEY=${SECRET_KEY}
ENV ETHEREUM_ADDRESS=$(ETHEREUM_ADDRESS)
ENV ETH_PRIVATE_KEY=$(ETH_PRIVATE_KEY)
ENV STARK_PRIVATE_KEY_MAINNET=$(STARK_PRIVATE_KEY_MAINNET) 
ENV DYDX_API_KEY_MAINNET=$(DYDX_API_KEY_MAINNET) 
ENV DYDX_API_SECRET_MAINNET=$(DYDX_API_SECRET_MAINNET) 
ENV DYDX_API_PASSPHRASE_MAINNET=$(DYDX_API_PASSPHRASE_MAINNET) 
ENV STARK_PRIVATE_KEY_TESTNET=$(STARK_PRIVATE_KEY_TESTNET) 
ENV DYDX_API_KEY_TESTNET=$(DYDX_API_KEY_TESTNET) 
ENV DYDX_API_SECRET_TESTNET=$(DYDX_API_SECRET_TESTNET) 
ENV DYDX_API_PASSPHRASE_TESTNET=$(DYDX_API_PASSPHRASE_TESTNET) 

# Copia el resto de los archivos de la aplicación
COPY . .

# Ejecuta las migraciones y recolecta archivos estáticos
RUN python manage.py migrate && \
    python manage.py collectstatic --noinput

# Etapa de ejecución para la aplicación Django
FROM python:3.8-slim
WORKDIR /app

# Copia solo los archivos necesarios de la etapa de construcción
COPY --from=build /app /app

# Configura las variables de entorno si es necesario
ENV DJANGO_SETTINGS_MODULE=backarbstrat.settings

# Exponer el puerto en el que la aplicación Django se ejecutará (ajustar según tus necesidades)
EXPOSE 8000

# Comando para iniciar la aplicación Django
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backarbstrat.wsgi:application"]
