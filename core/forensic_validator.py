import piexif
from core.logger import log

class ForensicValidator:
    """
    Motor de validación de integridad forense.
    Busca inconsistencias lógicas, estructurales y rastros de software.
    """

    @staticmethod
    def analyze_consistency(tags: dict, metadata: dict, image_path: str, structure: dict = None) -> list:
        """
        Realiza un análisis profundo de consistencia.
        Retorna una lista de 'Flags' forenses detectados.
        """
        flags = []

        # 1. Consistencia Temporal
        dto = str(tags.get("EXIF DateTimeOriginal", ""))
        dt = str(tags.get("Image DateTime", ""))
        if dto and dt and dto != dt:
            flags.append({
                "severity": "MEDIUM",
                "issue": "Discrepancia Temporal",
                "evidence": f"Original: {dto} | Modificado: {dt}"
            })

        # 2. Validación de MakerNotes
        make = str(tags.get("Image Make", "")).upper()
        has_makernote = "EXIF MakerNote" in tags
        major_brands = ["CANON", "NIKON", "SONY", "APPLE", "SAMSUNG"]
        if any(brand in make for brand in major_brands) and not has_makernote:
            flags.append({
                "severity": "HIGH",
                "issue": "MakerNotes Ausentes",
                "evidence": f"Cámara {make} detectada pero sin notas de fabricante (Posible re-exportación)"
            })

        # 3. Análisis de Miniatura EXIF
        try:
            exif_dict = piexif.load(image_path)
            if not exif_dict.get("thumbnail") and any(brand in make for brand in major_brands):
                flags.append({
                    "severity": "LOW",
                    "issue": "Miniatura EXIF Ausente",
                    "evidence": "Falta el thumbnail estándar del flujo de cámara"
                })
        except Exception: pass

        # 4. Detección de Software (EXIF + XMP)
        software_detected = []
        for key, val in metadata.items():
            val_str = str(val).lower()
            for sw in ["photoshop", "gimp", "snapseed", "canva", "vsco", "picsart", "lightroom"]:
                if sw in val_str and sw.capitalize() not in software_detected:
                    software_detected.append(sw.capitalize())

        # 5. Análisis Estructural (Fase 5)
        if structure:
            if structure.get("photoshop_detected"):
                if "Photoshop" not in software_detected: software_detected.append("Photoshop (Estructural)")
                flags.append({
                    "severity": "CRITICAL",
                    "issue": "Bloque Photoshop IRB Detectado",
                    "evidence": "Segmento APP13 presente en la estructura binaria"
                })
            
            for anomaly in structure.get("anomalies", []):
                flags.append({
                    "severity": "HIGH",
                    "issue": "Anomalía Estructural",
                    "evidence": anomaly
                })

        if software_detected:
            flags.append({
                "severity": "HIGH",
                "issue": "Rastro de Software de Edición",
                "evidence": f"Detectado: {', '.join(software_detected)}"
            })

        return flags

    @staticmethod
    def format_status(flags: list) -> str:
        if not flags:
            return "Original / Sin inconsistencias detectadas"
        
        severities = [f["severity"] for f in flags]
        highest = "CRITICAL" if "CRITICAL" in severities else ("HIGH" if "HIGH" in severities else "MEDIUM")
        
        issues = sorted(list(set([f["issue"] for f in flags])))
        return f"EVIDENCIA DE MODIFICACIÓN ({highest}): {', '.join(issues)}"
