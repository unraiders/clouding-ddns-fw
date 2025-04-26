import os
import re

from requests import get
from requests.exceptions import RequestException

from utils import setup_logger

logger = setup_logger(__name__)

CHECK_IP_FILE = '/app/data/check_ip.txt'

def obtener_ip_publica():
    def try_get_ip(urls):
        for url in urls:
            try:
                response = get(url.strip())
                if response.status_code == 200:
                    ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
                    ip = response.text.strip()
                    if ip_pattern.match(ip):
                        return ip, url.strip()
            except RequestException:
                continue
        return None, None

    # Leer las URLs del archivo
    try:
        if not os.path.exists(CHECK_IP_FILE):
            logger.error(f"No existe el archivo: {CHECK_IP_FILE}")
            return None

        with open(CHECK_IP_FILE, 'r') as file:
            urls = file.readlines()

            ip, url_usado = try_get_ip(urls)
            if ip:
                logger.debug('Dirección IP pública desde {} es: {}'.format(url_usado, ip))
                logger.info('IP pública obtenida: {}'.format(ip))
                return ip
            else:
                logger.error('No se pudo obtener la IP pública de ninguna de las URLs disponibles')
                return None
    except Exception as e:
        logger.error(f"Error al cargar el archivo check_ip.txt: {e}")
        return None
