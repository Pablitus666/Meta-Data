import logging
import os
from logging.handlers import RotatingFileHandler
from core.resources import get_base_path

def setup_logger():
    """Configura un sistema de logs profesional y silencia librerías ruidosas."""
    # En Windows, usamos %LOCALAPPDATA% para evitar errores de permisos en Program Files
    appdata_path = os.getenv('LOCALAPPDATA')
    if not appdata_path:
        # Fallback para otros SO o si LOCALAPPDATA no está definido
        log_dir = os.path.join(get_base_path(), "logs")
    else:
        log_dir = os.path.join(appdata_path, "MetaData")

    # Crear la carpeta de logs si no existe
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "metadata_app.log")
    except Exception:
        # Si todo falla, intentamos usar la carpeta base (aunque falle el permiso)
        log_path = os.path.join(get_base_path(), "metadata_app.log")
    
    # 1. Configuración de nuestro logger principal
    logger = logging.getLogger("MetaData")
    logger.setLevel(logging.ERROR)
    
    if not logger.handlers:
        handler = RotatingFileHandler(log_path, maxBytes=1024*1024, backupCount=3, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # 2. SILENCIAR LIBRERÍAS EXTERNAS (Evita mensajes como "Possibly corrupted field" en consola)
    # Forzamos a que exifread y otras solo reporten errores críticos
    logging.getLogger("exifread").setLevel(logging.ERROR)
    logging.getLogger("PIL").setLevel(logging.ERROR)
    
    return logger

# Instancia global
log = setup_logger()
