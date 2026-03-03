import struct
from core.logger import log

class JPEGStructureAnalyzer:
    """
    Analizador estructural de bajo nivel para archivos JPEG.
    Escanea marcadores binarios para detectar anomalías y rastros de software.
    """

    # Marcadores estándar JPEG
    MARKERS = {
        0xFFD8: "SOI (Start of Image)",
        0xFFE0: "APP0 (JFIF/AVI)",
        0xFFE1: "APP1 (EXIF/XMP)",
        0xFFE2: "APP2 (ICC Profile)",
        0xFFED: "APP13 (Photoshop IRB)",
        0xFFEE: "APP14 (Adobe)",
        0xFFDB: "DQT (Define Quantization Table)",
        0xFFC0: "SOF0 (Baseline DCT)",
        0xFFC2: "SOF2 (Progressive DCT)",
        0xFFC4: "DHT (Define Huffman Table)",
        0xFFDA: "SOS (Start of Scan)",
        0xFFD9: "EOI (End of Image)"
    }

    @staticmethod
    def analyze_structure(filepath: str) -> dict:
        """
        Recorre el archivo byte a byte buscando marcadores JPEG.
        Retorna un mapa de la estructura detectada.
        """
        structure = {
            "markers_found": [],
            "anomalies": [],
            "photoshop_detected": False,
            "adobe_app14": False
        }

        try:
            with open(filepath, 'rb') as f:
                data = f.read()
                
                # Verificar si es un JPEG válido (debe empezar con 0xFFD8)
                if not data.startswith(b'\xff\xd8'):
                    return structure

                offset = 0
                while offset < len(data):
                    # Buscar el inicio de un marcador (0xFF)
                    if data[offset] == 0xFF:
                        # Leer los dos bytes del marcador
                        if offset + 1 >= len(data): break
                        marker_code = struct.unpack(">H", data[offset:offset+2])[0]
                        
                        # Si es un marcador conocido, registrarlo
                        if marker_code in JPEGStructureAnalyzer.MARKERS:
                            marker_name = JPEGStructureAnalyzer.MARKERS[marker_code]
                            structure["markers_found"].append(marker_name)
                            
                            # Detecciones específicas
                            if marker_code == 0xFFED: structure["photoshop_detected"] = True
                            if marker_code == 0xFFEE: structure["adobe_app14"] = True

                        # Marcadores sin longitud (SOI, EOI, SOS...)
                        if marker_code in (0xFFD8, 0xFFD9, 0xFFDA):
                            offset += 2
                            if marker_code == 0xFFDA: # Después de SOS vienen los datos comprimidos
                                break # El análisis estructural termina al iniciar el escaneo de imagen
                            continue
                        
                        # Marcadores con longitud definida en los siguientes 2 bytes
                        if offset + 4 <= len(data):
                            length = struct.unpack(">H", data[offset+2:offset+4])[0]
                            offset += 2 + length # Saltar el bloque completo
                        else:
                            break
                    else:
                        offset += 1

            # Detectar anomalías estructurales
            # 1. Doble APP1 (Común en re-guardados con XMP extra)
            if structure["markers_found"].count("APP1 (EXIF/XMP)") > 1:
                structure["anomalies"].append("Segmento APP1 duplicado (Posible inyección XMP externa)")
            
            # 2. Orden anómalo (DQT antes de APPn suele ser raro en cámaras)
            if "DQT (Define Quantization Table)" in structure["markers_found"]:
                dqt_idx = structure["markers_found"].index("DQT (Define Quantization Table)")
                app1_idx = structure["markers_found"].index("APP1 (EXIF/XMP)") if "APP1 (EXIF/XMP)" in structure["markers_found"] else 999
                if dqt_idx < app1_idx:
                    structure["anomalies"].append("Tablas de cuantización antes de metadatos (Estructura no estándar)")

            return structure
        except Exception as e:
            log.error(f"Error en análisis estructural de {filepath}: {e}")
            return structure
