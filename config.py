import os

from dotenv import load_dotenv

load_dotenv()

CLOUDING_API_URL = os.getenv('CLOUDING_API_URL', 'https://api.clouding.io/v1')
CLOUDING_API_TOKEN = os.getenv('CLOUDING_API_TOKEN')
CLOUDING_FW_NAME = os.getenv('CLOUDING_FW_NAME')

CLIENTE_NOTIFICACION = os.getenv('CLIENTE_NOTIFICACION')

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')

INITIAL_DELAY = int(os.getenv('INITIAL_DELAY', '2'))

TZ = os.getenv('TZ', 'Europe/Madrid')
DEBUG = os.getenv('DEBUG', '0') == '1'

IMG_DISCORD_URL = 'https://github.com/unraiders/clouding-ddns-fw/blob/main/imagenes/clouding-ddns-fw.png?raw=true'
