import os
import exifread
import piexif
from .gps_utils import convert_to_decimal

class MetadataReader:
    """
    Especialista en lectura técnica. Mantiene la dualidad Raw/Interpreted.
    """

    EXPOSURE_PROGRAMS = {0: "Unidentified", 1: "Manual", 2: "Normal program", 3: "Aperture priority", 4: "Shutter priority", 5: "Creative program", 6: "Action program", 7: "Portrait mode", 8: "Landscape mode"}
    METERING_MODES = {0: "Unknown", 1: "Average", 2: "CenterWeightedAverage", 3: "Spot", 4: "MultiSpot", 5: "Pattern", 6: "Partial", 255: "Other"}
    FLASH_MODES = {0: "Flash did not fire", 1: "Flash fired", 9: "Flash fired, compulsory mode", 16: "Flash did not fire, compulsory mode", 24: "Flash did not fire, auto mode", 25: "Flash fired, auto mode", 32: "No flash function", 89: "Flash fired, auto mode, red-eye reduction"}
    SCENE_TYPES = {0: "Standard", 1: "Landscape", 2: "Portrait", 3: "Night scene"}
    ORIENTATION_MODES = {1: "Horizontal (normal)", 2: "Mirror horizontal", 3: "Rotate 180", 4: "Mirror vertical", 5: "Mirror horizontal and rotate 270 CW", 6: "Rotate 90 CW", 7: "Mirror horizontal and rotate 90 CW", 8: "Rotate 270 CW"}

    @staticmethod
    def _set_val(metadata, key, raw, interpreted=None):
        """Helper para estandarizar la estructura dual."""
        metadata[key] = {
            "raw": raw,
            "interpreted": interpreted if interpreted is not None else str(raw)
        }

    @staticmethod
    def extract_basic_tags(tags: dict, metadata: dict):
        """Extrae datos GPS y generales manteniendo valores originales."""
        if "GPS GPSLatitude" in tags and "GPS GPSLongitude" in tags:
            try:
                lat_raw = tags["GPS GPSLatitude"].values
                lon_raw = tags["GPS GPSLongitude"].values
                lat = convert_to_decimal(lat_raw, tags["GPS GPSLatitudeRef"].values[0])
                lon = convert_to_decimal(lon_raw, tags["GPS GPSLongitudeRef"].values[0])
                
                MetadataReader._set_val(metadata, "GPS Latitude", lat_raw, f"{lat:.6f}")
                MetadataReader._set_val(metadata, "GPS Longitude", lon_raw, f"{lon:.6f}")
                metadata["Google Maps"] = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
            except Exception: pass

        MetadataReader._set_val(metadata, "Make", tags.get("Image Make", "N/A"))
        MetadataReader._set_val(metadata, "Model", tags.get("Image Model", "N/A"))
        MetadataReader._set_val(metadata, "DateTime", tags.get("Image DateTime", "N/A"))
        MetadataReader._set_val(metadata, "Software", tags.get("Image Software", "N/A"))
        
        # Fallbacks
        if "Exposure Time" not in metadata: 
            MetadataReader._set_val(metadata, "Exposure Time", tags.get("EXIF ExposureTime", "N/A"))
        if "F-Number" not in metadata: 
            MetadataReader._set_val(metadata, "F-Number", tags.get("EXIF FNumber", "N/A"))
        if "ISO Speed" not in metadata: 
            MetadataReader._set_val(metadata, "ISO Speed", tags.get("EXIF ISOSpeedRatings", "N/A"))
        if "Focal Length" not in metadata: 
            MetadataReader._set_val(metadata, "Focal Length", tags.get("EXIF FocalLength", "N/A"))

    @staticmethod
    def extract_advanced_tags(exif_dict: dict, metadata: dict):
        """Extrae datos refinados de piexif."""
        exif = exif_dict.get("Exif", {})
        zeroth = exif_dict.get("0th", {})

        # Software
        soft_raw = zeroth.get(piexif.ImageIFD.Software)
        if soft_raw:
            soft_interp = soft_raw.decode('utf-8', errors='ignore').strip()
            MetadataReader._set_val(metadata, "Software", soft_raw, soft_interp)

        # Dimensiones
        w = exif.get(piexif.ExifIFD.PixelXDimension) or zeroth.get(piexif.ImageIFD.ImageWidth)
        h = exif.get(piexif.ExifIFD.PixelYDimension) or zeroth.get(piexif.ImageIFD.ImageLength)
        if w and h:
            MetadataReader._set_val(metadata, "Dimensions", (w, h), f"{w} x {h} px")

        # Orientación
        orient_raw = zeroth.get(piexif.ImageIFD.Orientation)
        if orient_raw:
            MetadataReader._set_val(metadata, "Orientation", orient_raw, MetadataReader.ORIENTATION_MODES.get(orient_raw))

        # Datos técnicos
        exp_raw = exif.get(piexif.ExifIFD.ExposureTime)
        if exp_raw:
            MetadataReader._set_val(metadata, "Exposure Time", exp_raw, MetadataReader._format_exposure(exp_raw))

        fn_raw = exif.get(piexif.ExifIFD.FNumber)
        if fn_raw:
            MetadataReader._set_val(metadata, "F-Number", fn_raw, f"f/{MetadataReader._format_ratio(fn_raw)}")

        iso_raw = exif.get(piexif.ExifIFD.ISOSpeedRatings)
        if iso_raw:
            MetadataReader._set_val(metadata, "ISO Speed", iso_raw)
        
        foc_raw = exif.get(piexif.ExifIFD.FocalLength)
        if foc_raw:
            MetadataReader._set_val(metadata, "Focal Length", foc_raw, f"{MetadataReader._format_ratio(foc_raw)} mm")

        # Programas y Modos
        prog_raw = exif.get(piexif.ExifIFD.ExposureProgram)
        if prog_raw is not None:
            MetadataReader._set_val(metadata, "Exposure Program", prog_raw, MetadataReader.EXPOSURE_PROGRAMS.get(prog_raw))

        met_raw = exif.get(piexif.ExifIFD.MeteringMode)
        if met_raw is not None:
            MetadataReader._set_val(metadata, "Metering Mode", met_raw, MetadataReader.METERING_MODES.get(met_raw))

        flash_raw = exif.get(piexif.ExifIFD.Flash)
        if flash_raw is not None:
            MetadataReader._set_val(metadata, "Flash", flash_raw, MetadataReader.FLASH_MODES.get(flash_raw))

        scene_raw = exif.get(piexif.ExifIFD.SceneCaptureType)
        if scene_raw is not None:
            MetadataReader._set_val(metadata, "Scene Type", scene_raw, MetadataReader.SCENE_TYPES.get(scene_raw))

        wb_raw = exif.get(piexif.ExifIFD.WhiteBalance)
        if wb_raw is not None:
            MetadataReader._set_val(metadata, "White Balance", wb_raw, "Manual" if wb_raw == 1 else "Auto")
        
        zoom_raw = exif.get(piexif.ExifIFD.DigitalZoomRatio)
        if zoom_raw:
            zoom_val = MetadataReader._format_ratio(zoom_raw)
            if zoom_val and zoom_val > 1:
                MetadataReader._set_val(metadata, "Digital Zoom", zoom_raw, f"{zoom_val}x")

    @staticmethod
    def _format_exposure(value):
        if isinstance(value, tuple) and len(value) == 2:
            if value[1] == 0: return None
            if value[0] == 1: return f"1/{value[1]} s"
            return f"{value[0]/value[1]:.4f} s"
        return str(value)

    @staticmethod
    def _format_ratio(value):
        if isinstance(value, tuple) and len(value) == 2:
            if value[1] == 0: return None
            res = value[0] / value[1]
            return int(res) if res.is_integer() else round(res, 2)
        return value
