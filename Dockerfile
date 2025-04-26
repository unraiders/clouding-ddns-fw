FROM python:3.13-alpine

LABEL maintainer="unraiders"
LABEL description="Control firewall en VPS de Clouding con notificación a Telegram o Discord."

ARG VERSION=0.1.0 
ENV VERSION=${VERSION}

RUN apk add --no-cache dcron mc

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY utils.py .
COPY config.py .
COPY clouding-ddns-fw.py .
COPY entrypoint.sh .
COPY ip_info.py .
COPY firewall_registros.py .
COPY notificaciones.py .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]