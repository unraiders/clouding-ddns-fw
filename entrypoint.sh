#!/bin/sh

validar_cron() {
    if ! echo "$1" | grep -qE '^[*/0-9,-]+ [*/0-9,-]+ [*/0-9,-]+ [*/0-9,-]+ [*/0-9,-]+$'; then
        echo "Error: Formato cron inválido: $1"
        echo "Debe tener 5 campos: minuto hora día-mes mes día-semana"
        exit 1
    fi
}

if [ -z "$CRON" ]; then
    echo "La variable CRON no está definida."
    exit 1
fi

validar_cron "$CRON"

echo "$(date +'%d-%m-%Y %H:%M:%S') - Arrancando entrypoint.sh" >&2
echo "$(date +'%d-%m-%Y %H:%M:%S') - Versión: $VERSION" >&2
echo "$(date +'%d-%m-%Y %H:%M:%S') - Clouding Firewall: $CLOUDING_FW_NAME" >&2
echo "$(date +'%d-%m-%Y %H:%M:%S') - Notificación a: $CLIENTE_NOTIFICACION" >&2
echo "$(date +'%d-%m-%Y %H:%M:%S') - Zona horaria: $TZ" >&2
echo "$(date +'%d-%m-%Y %H:%M:%S') - Programación CRON: $CRON" >&2
echo "$(date +'%d-%m-%Y %H:%M:%S') - Debug: $DEBUG" >&2

# Crear el directorio data si no existe
mkdir -p /app/data

# Ejecutar el script inicialmente
echo "$(date +'%d-%m-%Y %H:%M:%S') - Ejecutando script inicial..."
python3 /app/clouding-ddns-fw.py

# Configurar y arrancar el CRON
CRON_JOB="$CRON python3 /app/clouding-ddns-fw.py >> /proc/1/fd/1 2>> /proc/1/fd/2"
echo "$CRON_JOB" > /etc/crontabs/root

echo "$(date +'%d-%m-%Y %H:%M:%S') - Arrancando cron..."
crond -f -l 2 || { echo "Error arrancando cron"; exit 1; }