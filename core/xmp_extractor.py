import re
import xml.etree.ElementTree as ET
from core.logger import log

class XMPExtractor:
    """
    Especialista en la extracción de metadatos XMP (Adobe Standard).
    Busca paquetes XML incrustados en archivos binarios (JPEG, PNG, etc.).
    """

    # Namespaces comunes en XMP para limpieza de etiquetas
    NAMESPACES = {
        'http://purl.org/dc/elements/1.1/': 'dc',
        'http://ns.adobe.com/xap/1.0/': 'xmp',
        'http://ns.adobe.com/xap/1.0/mm/': 'xmpMM',
        'http://ns.adobe.com/pdf/1.3/': 'pdf',
        'http://ns.adobe.com/photoshop/1.0/': 'photoshop',
        'http://ns.adobe.com/tiff/1.0/': 'tiff',
        'http://ns.adobe.com/exif/1.0/': 'exif',
    }

    @staticmethod
    def extract_xmp(filepath: str) -> dict:
        """
        Escanea el archivo en busca de paquetes XMP y los convierte en un diccionario plano.
        """
        xmp_data = {}
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
                
                # Buscar el inicio y fin del paquete XMP (estándar xpacket)
                # Usamos una búsqueda binaria para mayor compatibilidad entre formatos
                start = content.find(b'<x:xmpmeta')
                end = content.find(b'</x:xmpmeta>')
                
                if start != -1 and end != -1:
                    xmp_str = content[start:end+12].decode('utf-8', errors='ignore')
                    xmp_data = XMPExtractor._parse_xmp_str(xmp_str)
                    
            return xmp_data
        except Exception as e:
            log.error(f"Error extrayendo XMP de {filepath}: {e}")
            return {}

    @staticmethod
    def _parse_xmp_str(xmp_str: str) -> dict:
        """Parsea el XML de XMP y extrae atributos clave."""
        results = {}
        try:
            # Usar ElementTree para navegar el XML
            root = ET.fromstring(xmp_str)
            
            # XMP suele usar RDF para organizar los datos
            for desc in root.findall('.//{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description'):
                # Extraer atributos directos del nodo Description
                for attr, value in desc.attrib.items():
                    key = XMPExtractor._clean_tag(attr)
                    if key:
                        results[f"XMP:{key}"] = value
                
                # Extraer elementos hijos (tags anidados)
                for child in desc:
                    key = XMPExtractor._clean_tag(child.tag)
                    if key:
                        # Si tiene texto directo lo tomamos, sino indicamos que es complejo (lista/struct)
                        val = child.text.strip() if child.text else "[Complex Data]"
                        results[f"XMP:{key}"] = val
                        
            return results
        except Exception as e:
            log.error(f"Error parseando XML de XMP: {e}")
            return {}

    @staticmethod
    def _clean_tag(tag: str) -> str:
        """Limpia el namespace del tag para hacerlo legible."""
        # El tag viene como {http://ns.adobe.com/xap/1.0/}CreatorTool
        for ns_url, prefix in XMPExtractor.NAMESPACES.items():
            if tag.startswith(f"{{{ns_url}}}"):
                return tag.replace(f"{{{ns_url}}}", f"{prefix}:")
        
        # Si no está en la lista, intentar una limpieza genérica
        if '}' in tag:
            return tag.split('}')[-1]
        return tag
