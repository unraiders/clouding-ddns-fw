import json
from typing import Any, Dict, List, Optional, Tuple

import requests

from config import CLOUDING_API_TOKEN, CLOUDING_API_URL, CLOUDING_FW_NAME
from firewall_registros import cargar_registros_fw, guardar_registros_fw
from ip_info import obtener_ip_publica
from notificaciones import send_notification
from utils import generate_trace_id, setup_logger

logger = setup_logger(__name__)

def buscar_regla_existente(rules: List[Dict[str, Any]], description: str, port: int, protocol: str) -> Optional[Dict[str, Any]]:
    """
    Busca una regla existente que coincida con la descripción, puerto y protocolo
    """
    for rule in rules:
        if (rule.get('description') == description and
            rule.get('protocol', '').lower() == protocol.lower() and
            rule.get('portRangeMin') == port and
            rule.get('portRangeMax') == port):
            return rule
    return None

def obtener_firewall_id() -> Tuple[Optional[str], Optional[List[Dict[str, Any]]]]:
    """
    Obtiene el ID del firewall y sus reglas actuales
    """
    try:
        headers = {
            "X-API-KEY": CLOUDING_API_TOKEN,
            "Content-Type": "application/json"
        }

        response = requests.get(
            f"{CLOUDING_API_URL}/firewalls",
            headers=headers
        )

        logger.debug(f"Código de respuesta: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            logger.debug(f"Respuesta API: {json.dumps(data, indent=2)}")

            for fw in data.get('values', []):
                if fw.get('name') == CLOUDING_FW_NAME:
                    firewall_id = fw.get('id')
                    rules = fw.get('rules', [])
                    logger.info(f"Firewall encontrado en API: {CLOUDING_FW_NAME} con ID: {firewall_id}")
                    return firewall_id, rules

            logger.error(f"No se encontró el firewall con nombre {CLOUDING_FW_NAME}")
            return None, None
        else:
            logger.error(f"Error en la API. Código: {response.status_code}")
            logger.error(f"Respuesta: {response.text}")
            return None, None

    except Exception as e:
        logger.error(f"Error al obtener firewall_id: {str(e)}")
        logger.debug("Excepción completa:", exc_info=True)
        return None, None

def borrar_regla_firewall(firewall_id: str, rule_id: str) -> bool:
    """
    Borra una regla específica del firewall
    """
    try:
        url = f"{CLOUDING_API_URL}/firewalls/rules/{rule_id}"
        logger.debug(f"URL para borrar regla: {url}")

        headers = {"X-API-KEY": CLOUDING_API_TOKEN}
        logger.debug(f"Headers: {headers}")

        logger.debug(f"Intentando borrar regla {rule_id} del firewall {firewall_id}")
        response = requests.delete(url, headers=headers)

        logger.debug(f"Código de respuesta: {response.status_code}")
        if hasattr(response, 'text') and response.text:
            logger.debug(f"Respuesta: {response.text}")

        if response.status_code == 204:
            logger.info(f"Regla {rule_id} borrada exitosamente")
            return True
        elif response.status_code == 404:
            logger.error(f"La regla {rule_id} no se encontró en el firewall (404)")
            return False
        else:
            logger.error(f"Error al borrar regla {rule_id}. Código: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Error al borrar la regla: {str(e)}")
        logger.debug("Excepción completa:", exc_info=True)
        return False

def crear_regla_firewall(firewall_id: str, regla: Dict[str, Any], ip_actual: str) -> Optional[str]:
    """
    Crea una nueva regla en el firewall
    """
    try:
        payload = {
            "sourceIp": f"{ip_actual}/32",
            "protocol": regla['protocol'],
            "description": regla['description'],
            "portRangeMin": regla['portRangeMin'],
            "portRangeMax": regla['portRangeMax']
        }

        logger.debug(f"Creando regla con payload: {json.dumps(payload, indent=2)}")

        response = requests.post(
            f"{CLOUDING_API_URL}/firewalls/{firewall_id}/rules",
            headers={"X-API-KEY": CLOUDING_API_TOKEN},
            json=payload
        )

        logger.debug(f"Código respuesta creación regla: {response.status_code}")
        logger.debug(f"Respuesta creación regla: {response.text}")

        if response.status_code == 201:
            data = response.json()
            rule_id = data.get('id')
            logger.info(f"Regla creada exitosamente con ID: {rule_id}")
            return rule_id
        else:
            logger.error(f"Error al crear regla. Código: {response.status_code}")
            logger.error(f"Respuesta: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception al crear regla: {str(e)}")
        logger.debug("Excepción completa:", exc_info=True)
        return None

def limpiar_reglas_antiguas(firewall_id: str, reglas_actuales: List[Dict[str, Any]], registros: List[Dict[str, Any]]) -> None:
    """
    Limpia las reglas antiguas que tienen status 'pending_delete'
    """
    for registro in registros:
        if registro['status'] == 'pending_delete':
            previous_id = registro.get('previous_id')
            if previous_id:
                logger.info(f"Intentando borrar regla antigua con ID {previous_id}")
                if borrar_regla_firewall(firewall_id, previous_id):
                    registro['previous_id'] = ''
                    registro['status'] = 'active'

def actualizar_reglas_firewall() -> None:
    """
    Función principal que gestiona la actualización de las reglas del firewall
    """
    generate_trace_id()

    logger.info("Iniciando actualización de reglas del firewall")

    # Obtener ID del firewall y sus reglas actuales
    firewall_id, reglas_actuales = obtener_firewall_id()
    if not firewall_id or reglas_actuales is None:
        logger.error("No se pudo obtener el ID del firewall o sus reglas")
        return

    # Obtener IP pública actual
    logger.debug("Obteniendo IP pública actual...")
    ip_actual = obtener_ip_publica()
    if not ip_actual:
        logger.error("No se pudo obtener la IP pública actual")
        return

    logger.debug(f"IP actual obtenida: {ip_actual}")

    # Cargar registros actuales
    logger.debug("Cargando registros del archivo...")
    registros = cargar_registros_fw()
    if not registros:
        logger.error("No se pudieron cargar los registros")
        return

    logger.debug(f"Registros cargados: {json.dumps(registros, indent=2)}")
    cambios_realizados = False

    ip_anterior = registros[0].get('sourceIp', '').split('/')[0] if registros[0].get('sourceIp') else ''

    # Procesar cada registro
    for registro in registros:
        logger.debug(f"Procesando registro: {json.dumps(registro, indent=2)}")

        # Si el registro tiene un ID y la IP es diferente, borrar la regla antigua
        if registro.get('id') and registro.get('sourceIp'):
            ip_registro = registro['sourceIp'].split('/')[0]
            if ip_registro != ip_actual:
                logger.info(f"La IP ha cambiado para {registro['description']} de {ip_registro} a {ip_actual}")

                # Intentar borrar la regla antigua usando su ID
                if borrar_regla_firewall(firewall_id, registro['id']):
                    logger.info(f"Regla antigua con ID {registro['id']} borrada exitosamente")

                    # Crear nueva regla
                    nuevo_id = crear_regla_firewall(firewall_id, registro, ip_actual)
                    if nuevo_id:
                        # Actualizar el registro con la nueva información
                        registro['id'] = nuevo_id
                        registro['sourceIp'] = f"{ip_actual}/32"
                        cambios_realizados = True
                        logger.info(f"Nueva regla creada con ID {nuevo_id}")
                else:
                    logger.error(f"No se pudo borrar la regla antigua con ID {registro['id']}")
        else:
            # Si es un registro nuevo sin ID, crear la regla
            logger.info(f"Creando nueva regla para {registro['description']}")
            nuevo_id = crear_regla_firewall(firewall_id, registro, ip_actual)
            if nuevo_id:
                registro['id'] = nuevo_id
                registro['sourceIp'] = f"{ip_actual}/32"
                registro['firewall_id'] = firewall_id
                cambios_realizados = True
                logger.info(f"Nueva regla creada con ID {nuevo_id}")

    # Guardar cambios si se realizaron modificaciones
    if cambios_realizados:
        logger.info("Guardando cambios en registros_fw.json")
        logger.debug(f"Nuevos registros a guardar: {json.dumps(registros, indent=2)}")
        if guardar_registros_fw(registros):
            logger.info("Registros actualizados correctamente")
            if not ip_anterior:  # Si no hay IP anterior, es primera configuración
                send_notification(
                    f"🌍 *Clouding*: Primera configuración:\n"
                    f"IP Actual: {ip_actual}\n"
                    f"Creando reglas del Firewall.",
                    "Estado CLOUDING",
                    parse_mode="Markdown"
                )
            else:
                send_notification(
                    f"🌍 *Clouding*: Cambio de IP detectado:\n"
                    f"Anterior: {ip_anterior}\n"
                    f"Actual: {ip_actual}\n"
                    f"Cambiando reglas del Firewall.",
                    "Estado CLOUDING",
                    parse_mode="Markdown"
                )
        else:
            logger.error("Error al guardar los registros actualizados")
    else:
        logger.info("No se requirieron cambios en las reglas")

if __name__ == "__main__":
    actualizar_reglas_firewall()
