from PIL import Image, ImageTk, ImageEnhance
import os
from typing import Optional, Tuple
from collections import OrderedDict
from core import resources
from core.image_enhancer import add_shadow
from core.logger import log

class ImageManager:
    """
    Gestiona la carga, escalado y caché de imágenes con soporte High-DPI.
    """

    def __init__(self, root, max_cache_size: int = 16):
        self.root = root
        self._photo_cache = OrderedDict()
        self._pil_cache = OrderedDict()
        self.max_cache_size = max_cache_size
        try:
            self.scale = root.winfo_fpixels('1i') / 96.0
        except Exception as e:
            log.error(f"Error detectando escala DPI: {e}")
            self.scale = 1.0

    def load(
        self,
        filename: str,
        size: Optional[Tuple[int, int]] = None,
        add_shadow_effect: bool = False,
        shadow_offset: Tuple[int, int] = (2, 2),
        shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 100),
        blur_radius: int = 3,
        border: int = 5
    ) -> ImageTk.PhotoImage:
        
        cache_key = (filename, size, add_shadow_effect, shadow_offset, shadow_color, blur_radius, border, self.scale)
        
        if cache_key in self._photo_cache:
            self._photo_cache.move_to_end(cache_key)
            return self._photo_cache[cache_key]

        try:
            pil_image = self._get_base_pil(filename)

            if size:
                physical_size = (int(size[0] * self.scale), int(size[1] * self.scale))
                pil_image = pil_image.resize(physical_size, Image.Resampling.LANCZOS)

            if add_shadow_effect:
                pil_image = add_shadow(
                    pil_image, 
                    offset=shadow_offset, 
                    shadow_color=shadow_color,
                    blur_radius=blur_radius,
                    border=border
                )

            tk_img = ImageTk.PhotoImage(pil_image)
            self._store_in_cache(cache_key, tk_img)
            return tk_img
            
        except Exception as e:
            log.error(f"Error cargando imagen {filename}: {e}", exc_info=True)
            return None

    def load_external(self, path: str, size: Tuple[int, int]) -> ImageTk.PhotoImage:
        cache_key = (path, size, "external")
        if cache_key in self._photo_cache:
            return self._photo_cache[cache_key]

        try:
            with Image.open(path) as img:
                img.thumbnail((size[0] * self.scale, size[1] * self.scale), Image.Resampling.BILINEAR)
                tk_img = ImageTk.PhotoImage(img)
                self._store_in_cache(cache_key, tk_img)
                return tk_img
        except Exception as e:
            log.error(f"Error en carga externa rápida para {path}: {e}", exc_info=True)
            return None

    def _store_in_cache(self, key, value):
        self._photo_cache[key] = value
        if len(self._photo_cache) > self.max_cache_size:
            self._photo_cache.popitem(last=False)

    def _get_base_pil(self, filename: str) -> Image.Image:
        if filename in self._pil_cache:
            self._pil_cache.move_to_end(filename)
            return self._pil_cache[filename]

        file_only = os.path.basename(filename)
        base_name = os.path.splitext(file_only)[0]
        
        paths_to_try = [
            resources.master_image_path(f"{base_name}.png"),
            resources.image_path(file_only),
            filename
        ]
        
        for path in paths_to_try:
            if os.path.exists(path):
                try:
                    with Image.open(path) as img:
                        pil_img = img.convert("RGBA")
                        self._pil_cache[filename] = pil_img
                        if len(self._pil_cache) > self.max_cache_size:
                            self._pil_cache.popitem(last=False)
                        return pil_img
                except Exception as e:
                    log.error(f"Error abriendo imagen base {path}: {e}")
                    continue
        
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))

    def clear_cache(self):
        self._photo_cache.clear()
        self._pil_cache.clear()
