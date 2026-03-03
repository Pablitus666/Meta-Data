import exifread
import os

class ForensicDumper:
    """
    Especialista en la extracción exhaustiva y sin filtros.
    Detecta y resume datos binarios para evitar ruido en los reportes.
    """

    @staticmethod
    def dump_all_tags(filepath: str) -> dict:
        """
        Realiza un volcado completo de metadatos.
        """
        full_dump = {}
        
        try:
            with open(filepath, 'rb') as f:
                tags = exifread.process_file(f, details=True, debug=False)
                
                # Si no se encuentran tags, devolvemos un grupo vacío descriptivo
                if not tags:
                    return {"STATUS": {"Info": {"value": "No tags found in file", "raw_type": "ASCII"}}}

                for tag_name, tag_value in tags.items():
                    parts = tag_name.split(' ', 1)
                    group = parts[0] if len(parts) > 1 else "General"
                    tag = parts[1] if len(parts) > 1 else parts[0]
                    
                    if group not in full_dump:
                        full_dump[group] = {}
                    
                    val_str = ""
                    if hasattr(tag_value, 'values') and isinstance(tag_value.values, bytes):
                        val_str = f"[Binary Data: {len(tag_value.values)} bytes]"
                    else:
                        val_str = str(tag_value)
                        if len(val_str) > 1000:
                            val_str = f"{val_str[:100]}... [Truncated: {len(val_str)} chars]"

                    full_dump[group][tag] = {
                        "value": val_str,
                        "raw_type": getattr(tag_value, 'field_type', 'Unknown')
                    }
                    
            return full_dump
        except Exception as e:
            # Retornamos una estructura de diccionario incluso en error para evitar fallos de .items()
            return {"ERROR": {"Extraction": {"value": str(e), "raw_type": "Exception"}}}

    @staticmethod
    def format_dump_for_display(dump: dict) -> str:
        """Convierte el dump en un string estructurado. Resiliente a errores."""
        if not isinstance(dump, dict):
            return f"Error: Dump data is not a dictionary ({type(dump)})"

        lines = []
        try:
            for group, tags in sorted(dump.items()):
                lines.append(f"\n[{group}]")
                
                # Verificación extra: tags debe ser un diccionario
                if isinstance(tags, dict):
                    for tag, info in sorted(tags.items()):
                        val = info.get('value', 'N/A')
                        rtype = info.get('raw_type', 'Unknown')
                        lines.append(f"{tag:30} : {val} ({rtype})")
                else:
                    lines.append(f"  Data: {str(tags)}")
                    
            return "\n".join(lines)
        except Exception as e:
            return f"Critical error formatting dump: {str(e)}"
