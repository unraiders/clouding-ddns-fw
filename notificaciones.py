import time

import requests
import telebot

from config import (
    CLIENTE_NOTIFICACION,
    DISCORD_WEBHOOK,
    IMG_DISCORD_URL,
    INITIAL_DELAY,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)
from utils import setup_logger

logger = setup_logger(__name__)

def send_notification(message, title, parse_mode=None, retries=4, delay=2.0, initial_delay=INITIAL_DELAY):
    if CLIENTE_NOTIFICACION:
        if CLIENTE_NOTIFICACION == "telegram":
            if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:

                if initial_delay > 0:
                    time.sleep(initial_delay)

                for attempt in range(retries):
                    try:
                        bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
                        bot.send_message(TELEGRAM_CHAT_ID, message, parse_mode=parse_mode)
                        logger.info("Notificación enviada a Telegram correctamente.")
                        return True
                    except Exception as e:
                        logger.debug(f"Notificación enviada a Telegram: {message}.")
                        logger.debug(f"Intento {attempt+1}/{retries}: Error al enviar notificación a Telegram: {str(e)}.")
                        if attempt < retries - 1:
                            time.sleep(delay)
                        else:
                            logger.error(f"Error al enviar notificación a Telegram después de {retries} intentos: {str(e)}.")
                            return False
            return False
        elif CLIENTE_NOTIFICACION == "discord":
            try:
                    message = message.replace("<b>", "**").replace("</b>", "**")

                    # Payload con embeds para incluir imagen
                    payload = {
                        "avatar_url": IMG_DISCORD_URL,
                        "embeds": [
                            {
                                "title": title,
                                "description": message,
                                "color": 6018047,
                                "thumbnail": {"url": IMG_DISCORD_URL}
                            }
                        ]
                    }

                    response = requests.post(DISCORD_WEBHOOK, json=payload)

                    if response.status_code == 204:  # Discord devuelve 204 cuando es exitoso
                        logger.info("Notificación enviada a Discord correctamente.")
                    else:
                        logger.error(f"Error al enviar mensaje a Discord. Status code: {response.status_code}")

            except Exception as e:
                logger.error(f"Error al enviar mensaje a Discord: {str(e)}")
        else:
            logger.error(f"Cliente de notificación no soportado: {CLIENTE_NOTIFICACION}")
