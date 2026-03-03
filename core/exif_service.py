import os
import exifread
import piexif
from .metadata_extractor import MetadataReader
from .metadata_cleaner import MetadataCleaner
from .forensic_validator import ForensicValidator
from .hash_utils import HashCalculator
from .raw_dump import ForensicDumper
from .xmp_extractor import XMPExtractor
from .jpeg_structure_analyzer import JPEGStructureAnalyzer

class MetadataExtractor:
    """
    Fachada central que orquesta la extracción técnica, forense, XMP y estructural.
    """

    @staticmethod
    def extract(image_path: str, mode: str = "user") -> dict:
        """
        Orquesta la extracción técnica, forense, XMP y estructural.
        """
        hashes = HashCalculator.calculate_hashes(image_path)
        file_size = f"{os.path.getsize(image_path) / 1024:.2f} KB"
        
        # Diccionario dual base con campos garantizados en formato de objeto
        internal_metadata = {
            "Filename": {"raw": os.path.basename(image_path), "interpreted": os.path.basename(image_path)},
            "File Size": {"raw": os.path.getsize(image_path), "interpreted": file_size},
            "MD5": {"raw": hashes.get("MD5"), "interpreted": hashes.get("MD5")},
            "SHA-256": {"raw": hashes.get("SHA-256"), "interpreted": hashes.get("SHA-256")},
            "GPS Latitude": {"raw": "N/A", "interpreted": "N/A"},
            "GPS Longitude": {"raw": "N/A", "interpreted": "N/A"},
            "Google Maps": None, # Se mantiene simple porque es para la UI
        }

        tags = {}
        try:
            # 1. Metadatos XMP
            xmp_data = XMPExtractor.extract_xmp(image_path)
            for key, val in xmp_data.items():
                internal_metadata[key] = {"raw": val, "interpreted": val}

            # 2. Análisis Estructural
            structure = {}
            if image_path.lower().endswith(('.jpg', '.jpeg')):
                structure = JPEGStructureAnalyzer.analyze_structure(image_path)
                if structure.get("photoshop_detected"):
                    internal_metadata["JPEG:Photoshop_IRB"] = {"raw": True, "interpreted": "Yes (APP13 Found)"}
                if structure.get("adobe_app14"):
                    internal_metadata["JPEG:Adobe_APP14"] = {"raw": True, "interpreted": "Yes (Adobe Segment)"}

            with open(image_path, "rb") as img_file:
                # 3. Extracción básica
                img_file.seek(0)
                try:
                    tags = exifread.process_file(img_file, details=False)
                except Exception:
                    tags = {}
                MetadataReader.extract_basic_tags(tags, internal_metadata)

                # 4. Extracción avanzada
                if image_path.lower().endswith(('.jpg', '.jpeg', '.tif', '.tiff')):
                    try:
                        img_file.seek(0)
                        exif_dict = piexif.load(img_file.read())
                        MetadataReader.extract_advanced_tags(exif_dict, internal_metadata)
                    except Exception:
                        pass

            # 5. ANÁLISIS DE CONSISTENCIA Y ESTRUCTURA
            forensic_flags = ForensicValidator.analyze_consistency(tags, internal_metadata, image_path, structure)
            internal_metadata["forensic_flags"] = {"raw": forensic_flags, "interpreted": str(forensic_flags)}
            
            status = ForensicValidator.format_status(forensic_flags)
            internal_metadata["File Status"] = {"raw": status, "interpreted": status}

        except Exception as e:
            internal_metadata["Error"] = {"raw": str(e), "interpreted": f"Error interno: {str(e)}"}

        if mode == "forensic":
            return internal_metadata
        
        # Modo 'user': Aplanar para la UI
        user_view = {}
        for key, val in internal_metadata.items():
            if isinstance(val, dict) and "interpreted" in val:
                user_view[key] = val["interpreted"]
            else:
                user_view[key] = val
        
        return user_view

    @staticmethod
    def get_full_raw_dump(image_path: str) -> str:
        dump_data = ForensicDumper.dump_all_tags(image_path)
        return ForensicDumper.format_dump_for_display(dump_data)

    @staticmethod
    def remove(image_path: str) -> str:
        return MetadataCleaner.remove_all(image_path)
