import os
import piexif
from PIL import Image

class MetadataCleaner:
    """
    Especialista en la eliminación segura de metadatos.
    """
    
    @staticmethod
    def remove_all(image_path: str) -> str:
        """Elimina metadatos preservando la calidad original en JPEG."""
        base, ext = os.path.splitext(image_path)
        output_path = f"{base}_clean{ext}"
        ext_lower = ext.lower()
        
        try:
            with Image.open(image_path) as img:
                if ext_lower in ('.jpg', '.jpeg'):
                    # Mantiene calidad original y perfiles de color, pero vacía el bloque EXIF
                    img.save(output_path, exif=b"", quality="keep", subsampling=0)
                    try:
                        piexif.remove(output_path)
                    except:
                        pass
                else:
                    # Para PNG/TIFF, recrear desde los datos de píxeles crudos
                    data = list(img.getdata())
                    img_clean = Image.new(img.mode, img.size)
                    img_clean.putdata(data)
                    img_clean.save(output_path)
            
            return output_path
        except Exception as e:
            if os.path.exists(output_path):
                os.remove(output_path)
            raise e
