import datetime
from config.settings import BANNER_ASCII
from core.i18n import _

class ReportGenerator:
    """
    Genera reportes forenses profesionales.
    Asegura que las etiquetas estén traducidas y alineadas perfectamente.
    """

    @staticmethod
    def generate_technical_report(forensic_data: dict, full_raw_dump: str) -> str:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Obtener nombre de forma segura
        name_entry = forensic_data.get("Filename", {})
        filename = name_entry.get("interpreted", "Unknown") if isinstance(name_entry, dict) else str(name_entry)

        report = [
            BANNER_ASCII,
            "="*80,
            f"REPORTE DE ANÁLISIS FORENSE DIGITAL - {filename}",
            f"Fecha de generación: {timestamp}",
            "="*80,
            "\n[1. IDENTIFICACIÓN DEL ARCHIVO]",
        ]

        # 1. Identidad con etiquetas traducidas y alineación perfecta
        identity_map = [
            ("Filename", filename),
            ("File Size", forensic_data.get("File Size", {})),
            ("MD5", forensic_data.get("MD5", {})),
            ("SHA-256", forensic_data.get("SHA-256", {}))
        ]

        for key, entry in identity_map:
            label = _(f"metadata.{key.lower().replace(' ', '_')}")
            if label.startswith("metadata."): label = key
            
            # Si el entry ya es el filename (string), usarlo. Si es dict, extraer interpreted.
            val = entry.get("interpreted", "N/A") if isinstance(entry, dict) else str(entry)
            report.append(f"{label:20}: {val}")

        report.append("\n[2. ANÁLISIS DE INTEGRIDAD (FORENSIC FLAGS)]")

        # 2. Banderas Forenses
        flags_entry = forensic_data.get("forensic_flags", {})
        flags = flags_entry.get("raw", []) if isinstance(flags_entry, dict) else []
        
        if not flags:
            report.append("ESTADO: No se detectaron inconsistencias evidentes.")
        else:
            status_entry = forensic_data.get("File Status", {})
            status = status_entry.get("interpreted", "Modificado") if isinstance(status_entry, dict) else str(status_entry)
            report.append(f"ESTADO: {status}")
            report.append("-" * 40)
            for i, flag in enumerate(flags, 1):
                report.append(f"Hallazgo #{i}: [{flag.get('severity', 'UNKNOWN')}] {flag.get('issue', 'Issue')}")
                report.append(f"Evidencia:  {flag.get('evidence', 'N/A')}")
                report.append("")

        report.append("\n[3. METADATOS CLAVE (INTERPRETADOS)]")
        # 3. Metadatos Clave (Alineados a 25 caracteres)
        skip_keys = ["forensic_flags", "MD5", "SHA-256", "Filename", "File Size", "File Status", "Google Maps", "Error"]
        for key, val in sorted(forensic_data.items()):
            if key not in skip_keys and not key.startswith("_") and not key.startswith("XMP:"):
                label = _(f"metadata.{key.lower().replace(' ', '_')}")
                if label.startswith("metadata."): label = key
                
                interp = val.get("interpreted", str(val)) if isinstance(val, dict) else str(val)
                if interp and interp != "N/A":
                    report.append(f"{label:25}: {interp}")

        # 4. Metadatos Adobe XMP
        xmp_keys = [k for k in forensic_data.keys() if k.startswith("XMP:")]
        if xmp_keys:
            report.append("\n[4. METADATOS ADOBE XMP]")
            for k in sorted(xmp_keys):
                val = forensic_data[k]
                interp = val.get("interpreted", str(val)) if isinstance(val, dict) else str(val)
                report.append(f"{k:35}: {interp}")

        report.append("\n" + "="*80)
        report.append("[5. VOLCADO COMPLETO DE TAGS (RAW DUMP)]")
        report.append("="*80)
        report.append(full_raw_dump)
        
        report.append("\n" + "="*80)
        report.append("FIN DEL REPORTE - METADATA FORENSIC TOOL")
        report.append("="*80)

        return "\n".join(report)
