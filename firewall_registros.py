import json
import os
from typing import Any, Dict, List, Optional

from utils import setup_logger

logger = setup_logger(__name__)

REGISTROS_FILE = '/app/data/registros_fw.json'

def cargar_registros_fw() -> Optional[List[Dict[str, Any]]]:
    """
    Carga las configuraciones de registros del firewall desde el archivo registros_fw.json.

    Returns:
        List[Dict[str, Any]]: Lista de reglas del firewall, o None si hay error
    """
    try:
        if not os.path.exists(REGISTROS_FILE):
            logger.error(f"No existe el archivo: {REGISTROS_FILE}")
            return None

        with open(REGISTROS_FILE, 'r') as f:
            registros = json.load(f)
            if not isinstance(registros, list):
                logger.error("El archivo de registros no tiene el formato correcto")
                return None
            return registros
    except Exception as e:
        logger.error(f"Error al cargar el archivo registros_fw.json: {e}")
        return None

def guardar_registros_fw(registros: List[Dict[str, Any]]) -> bool:
    """
    Guarda las configuraciones de registros del firewall en el archivo registros_fw.json.

    Args:
        registros (List[Dict[str, Any]]): Lista de reglas del firewall

    Returns:
        bool: True si se guardó correctamente, False en caso contrario.
    """
    try:
        os.makedirs(os.path.dirname(REGISTROS_FILE), exist_ok=True)
        with open(REGISTROS_FILE, 'w') as f:
            json.dump(registros, f, indent=4)
        logger.debug(f"Registros guardados correctamente: {json.dumps(registros, indent=2)}")
        return True
    except Exception as e:
        logger.error(f"Error al guardar en el archivo registros_fw.json: {e}")
        return False



