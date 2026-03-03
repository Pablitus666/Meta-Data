import json
import locale
import os
from core.resources import locale_path
from core.logger import log

_translations = {}
_current_lang = "en"

# Fallback interno de emergencia por si fallan todos los archivos JSON (PyInstaller Robustness)
_EMERGENCY_FALLBACK = {
    "app.title": "MetaData - Metadata Extractor",
    "title.error": "Error",
    "button.close": "Close",
    "button.accept": "Accept",
    "error.invalid_image": "Invalid image file."
}

def init_i18n():
    """Detecta el idioma del sistema y carga las traducciones con múltiples niveles de fallback."""
    global _translations, _current_lang
    
    try:
        lang_code, _ = locale.getdefaultlocale()
        if lang_code:
            _current_lang = lang_code.split('_')[0].lower()
    except Exception as e:
        log.error(f"Error detectando idioma del sistema: {e}")
        _current_lang = "en"

    # Intentar cargar idioma detectado -> fallback a inglés -> fallback a diccionario interno
    paths_to_try = [
        locale_path(f"{_current_lang}.json"),
        locale_path("en.json")
    ]

    success = False
    for json_path in paths_to_try:
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    _translations = json.load(f)
                    success = True
                    break
            except Exception as e:
                log.error(f"Error cargando archivo de traducción {json_path}: {e}")
                continue
    
    if not success:
        log.warning("No se pudo cargar ningún archivo de traducción. Usando fallback interno.")
        _translations = _EMERGENCY_FALLBACK

def _(key, **kwargs):
    """Traduce una clave con soporte para placeholders y fallback seguro."""
    text = _translations.get(key, _EMERGENCY_FALLBACK.get(key, key))
    try:
        if kwargs:
            return text.format(**kwargs)
        return text
    except Exception as e:
        log.error(f"Error formateando traducción para clave '{key}': {e}")
        return text

# Inicializar al importar
init_i18n()
