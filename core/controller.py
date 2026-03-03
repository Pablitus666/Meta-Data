import os
import webbrowser
from tkinter import filedialog
from core.exif_service import MetadataExtractor
from core.i18n import _
from ui.dialogs import show_error, show_success, show_confirm
from config.settings import BANNER_ASCII
from core.logger import log
from core.report_generator import ReportGenerator

class AppController:
    """
    Controlador central con lógica de robustez, validación y generación de reportes.
    """
    VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.tif', '.tiff')

    def __init__(self, view, image_manager):
        self.view = view
        self.image_manager = image_manager
        
        # Estado de la aplicación
        self.current_path = None
        self.current_gps_url = None
        self.is_metadata_active = False

    def handle_file_selection(self, file_path=None):
        """Gestiona la selección de archivos con lógica inteligente."""
        if file_path is None:
            if self.is_metadata_active:
                return
            file_path = filedialog.askopenfilename(
                filetypes=[(_("filter.image_files"), "*.jpg;*.jpeg;*.png;*.tif;*.tiff")]
            )
            if not file_path:
                return

        if self.is_metadata_active:
            self.handle_clear()

        if not file_path.lower().endswith(self.VALID_EXTENSIONS):
            show_error(self.view.root, _("title.error"), _("error.invalid_image"), self.image_manager)
            return

        if os.path.exists(file_path):
            self._process_image(file_path)

    def _process_image(self, path):
        """Extrae metadatos y actualiza la vista con filtrado profesional."""
        try:
            metadata = MetadataExtractor.extract(path, mode="user")
            
            if "Error" in metadata:
                log.error(f"Error técnico en extracción para {path}: {metadata['Error']}")
                show_error(self.view.root, _("title.error"), _("error.invalid_image"), self.image_manager)
                return

            self.current_path = path
            self.is_metadata_active = True
            self.current_gps_url = metadata.get("Google Maps")
            
            # Formatear datos para la UI
            formatted_data = []
            
            # Claves técnicas ocultas (Google Maps se oculta del texto porque tiene su propio botón)
            hidden_keys = ["forensic_flags", "Google Maps", "_has_thumbnail"]
            
            for key, value in metadata.items():
                if key in hidden_keys or value is None:
                    continue
                
                label = _(f"metadata.{key.lower().replace(' ', '_')}")
                if label.startswith("metadata."):
                    label = key
                
                if key == "Filename":
                    formatted_data.append(f"{label}: {value}\n")
                else:
                    formatted_data.append(f"{label}: {value}")
                
            self.view.update_metadata_display("\n".join(formatted_data))
            
        except Exception as e:
            log.exception(f"Excepción crítica procesando {path}")
            show_error(self.view.root, _("title.error"), f"Error interno: {str(e)}", self.image_manager)

    def handle_view_location(self):
        if not self.is_metadata_active:
            show_error(self.view.root, _("title.warning"), _("warning.no_metadata_location"), self.image_manager)
            return

        if self.current_gps_url:
            try:
                webbrowser.open(self.current_gps_url)
            except Exception as e:
                log.error(f"Error abriendo navegador: {e}")
        else:
            show_error(self.view.root, _("title.warning"), _("warning.no_gps"), self.image_manager)

    def handle_delete(self):
        if not self.current_path:
            show_error(self.view.root, _("title.warning"), _("warning.no_metadata_delete"), self.image_manager)
            return

        if show_confirm(self.view.root, _("title.confirm"), _("warning.confirm_delete"), self.image_manager):
            try:
                new_file = MetadataExtractor.remove(self.current_path)
                show_success(
                    self.view.root, 
                    _("title.success"), 
                    _("success.deleted").format(path=os.path.basename(new_file)), 
                    self.image_manager
                )
                self._process_image(new_file)
            except Exception as e:
                log.exception(f"Error eliminando metadatos de {self.current_path}")
                show_error(self.view.root, _("title.error"), f"{_('error.delete_failed')}\n{str(e)}", self.image_manager)

    def handle_save(self, content):
        if not self.current_path or not self.is_metadata_active:
            show_error(self.view.root, _("title.warning"), _("warning.no_metadata"), self.image_manager)
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt", 
            initialfile=_("filename.default"), 
            filetypes=[(_("filter.text_files"), "*.txt")]
        )
        
        if file_path:
            try:
                forensic_data = MetadataExtractor.extract(self.current_path, mode="forensic")
                full_dump = MetadataExtractor.get_full_raw_dump(self.current_path)
                report_content = ReportGenerator.generate_technical_report(forensic_data, full_dump)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(report_content)
                
                show_success(self.view.root, _("title.success"), _("success.saved"), self.image_manager)
            except Exception as e:
                log.error(f"Error generando reporte forense en {file_path}: {e}")
                show_error(self.view.root, _("title.error"), f"Error al generar reporte: {str(e)}", self.image_manager)

    def handle_clear(self):
        self.current_path = None
        self.current_gps_url = None
        self.is_metadata_active = False
        self.image_manager.clear_cache()
        self.view.reset_ui()
