import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES
import webbrowser
import os

from core.image_manager import ImageManager
from core.controller import AppController
from core.i18n import _
from ui.dialogs import AboutDialog, center_window, show_error
from ui.widgets import create_image_button
from config.settings import (
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_TEXT_SECONDARY,
    FONT_BODY, LOGO_ICO, TITULO_PNG, BOTON_PNG, MEM_PNG, MEM1_PNG, 
    DRAG_DROP_PNG
)

class MetadataApp:
    """
    Vista principal de la aplicación.
    Se encarga exclusivamente de la representación visual y eventos de UI.
    """
    def __init__(self, root):
        self.root = root
        self.image_manager = ImageManager(self.root)
        
        # Inicializar el Controlador
        self.controller = AppController(self, self.image_manager)

        self._preload_assets()
        self._configure_window()
        self._setup_styles()
        self._build_ui()
        self._setup_drag_and_drop()

    def _preload_assets(self):
        """Carga todas las imágenes de la interfaz en caché al inicio."""
        self.asset_title = self.image_manager.load(TITULO_PNG, size=(400, 70), add_shadow_effect=True, shadow_offset=(3, 3), shadow_color=(0, 0, 0, 180), blur_radius=4)
        self.asset_drag_drop = self.image_manager.load(DRAG_DROP_PNG, size=(120, 120))
        self.asset_mem = self.image_manager.load(MEM_PNG, size=(59, 59))
        self.asset_mem1 = self.image_manager.load(MEM1_PNG, size=(59, 59))

    def _configure_window(self):
        self.root.withdraw()
        self.root.title(_("app.title"))
        self.root.geometry("700x520")
        self.root.configure(bg=COLOR_PRIMARY)
        self.root.resizable(False, False)

        try:
            icon_path = LOGO_ICO
            if os.path.exists(icon_path):
                icon_photo = self.image_manager.load(icon_path, size=(52, 52))
                if icon_photo:
                    self.root.iconphoto(False, icon_photo)
        except Exception:
            pass

        center_window(self.root, 700, 520)
        self.root.deiconify()

    def _setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Custom.Vertical.TScrollbar", 
                             gripcount=0, background="#3FA9C4", troughcolor="#2E6171", 
                             bordercolor="#2E6171", lightcolor="#3FA9C4", darkcolor="#2E6171",
                             arrowcolor="white", width=14)

    def _build_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg=COLOR_PRIMARY, height=100)
        header_frame.pack(fill=tk.X, pady=(5, 0))

        if self.asset_title:
            title_label = tk.Label(header_frame, image=self.asset_title, bg=COLOR_PRIMARY, borderwidth=0, cursor="hand2")
            title_label.place(relx=0.5, rely=0.5, anchor="center")
            title_label.bind("<Button-1>", lambda e: AboutDialog(self.root, self.image_manager))

        self._add_header_decorations(header_frame)

        # Botones
        button_frame = tk.Frame(self.root, bg=COLOR_PRIMARY)
        button_frame.pack(side=tk.BOTTOM, pady=15)

        btn_configs = [
            (_("button.location"), self.controller.handle_view_location, 110, 0),
            (_("button.save"), lambda: self.controller.handle_save(self.info_text.get(1.0, tk.END)), 110, 1),
            (_("button.delete"), self.controller.handle_delete, 110, 2),
            (_("button.clear"), self.controller.handle_clear, 110, 3),
            (_("button.exit"), self.root.destroy, 110, 4)
        ]

        for text, cmd, width, col in btn_configs:
            btn_container = tk.Frame(button_frame, bg=COLOR_PRIMARY, width=width, height=50)
            btn_container.pack_propagate(False)
            btn_container.grid(row=0, column=col, padx=5)
            create_image_button(btn_container, text, cmd, self.image_manager, BOTON_PNG, (width-5, 40)).place(relx=0.5, rely=0.5, anchor="center")

        # Área Central
        self._build_content_area()
        
        # Atajo de teclado: Suprimir para limpiar
        self.root.bind('<Delete>', lambda e: self.controller.handle_clear())

    def _add_header_decorations(self, parent):
        for photo, x in [(self.asset_mem, 30), (self.asset_mem1, 610)]:
            if photo:
                tk.Label(parent, image=photo, bg=COLOR_PRIMARY, borderwidth=0).place(x=x, y=10)

    def _build_content_area(self):
        self.container = tk.Frame(self.root, bg="#2E6171", padx=2, pady=2)
        self.container.pack(fill=tk.BOTH, expand=True, padx=25, pady=10)

        self.wrapper = tk.Frame(self.container, bg=COLOR_ACCENT)
        self.wrapper.pack(fill=tk.BOTH, expand=True)
        self.wrapper.grid_columnconfigure(0, weight=1)
        self.wrapper.grid_rowconfigure(0, weight=1)

        # Text Area
        self.info_text = tk.Text(self.wrapper, wrap="word", font=FONT_BODY, bg=COLOR_ACCENT, fg=COLOR_TEXT_SECONDARY, 
                                highlightthickness=0, borderwidth=0, padx=15, pady=15)
        self.info_text.grid(row=0, column=0, sticky="nsew")
        self.info_text.config(state="disabled")
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.wrapper, orient="vertical", style="Custom.Vertical.TScrollbar", command=self.info_text.yview)
        self.info_text.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.scrollbar.grid_remove()

        # Drop Area (Placeholder)
        self.drop_area = tk.Frame(self.wrapper, bg=COLOR_ACCENT, width=350, height=220, cursor="hand2")
        self.drop_area.pack_propagate(False)
        self.drop_area.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(self.drop_area, image=self.asset_drag_drop, bg=COLOR_ACCENT).pack(pady=(15, 0))
        self.drop_label = tk.Label(self.drop_area, text=_("instruction.drag_drop"), font=("Segoe UI", 11, "bold"), 
                                   bg=COLOR_ACCENT, fg="#023047", justify="center")
        self.drop_label.pack(expand=True, fill="both")

        self._bind_events()

    def _bind_events(self):
        """Registra los eventos de interactividad."""
        # Hover events para todos los widgets centrales
        for w in (self.wrapper, self.info_text, self.drop_area, self.drop_label):
            w.bind("<Enter>", self._on_hover_enter)
            w.bind("<Leave>", self._on_hover_leave)

        # Clic manual: Solo en el wrapper o cuando la app está vacía (drop_area)
        # IMPORTANTE: NO bindeamos <Button-1> al info_text para NO romper la selección de texto nativa
        self.wrapper.bind("<Button-1>", lambda e: self.controller.handle_file_selection())
        self.drop_area.bind("<Button-1>", lambda e: self.controller.handle_file_selection())
        self.drop_label.bind("<Button-1>", lambda e: self.controller.handle_file_selection())

        # Drag & Drop: Siempre activo en todos los widgets centrales
        for w in (self.wrapper, self.info_text, self.drop_area, self.drop_label):
            w.drop_target_register(DND_FILES)
            w.dnd_bind('<<Drop>>', self._on_drop)
            w.dnd_bind('<<DropEnter>>', self._on_drag_enter)
            w.dnd_bind('<<DropLeave>>', self._on_drag_leave)

    def _on_drop(self, event):
        """Maneja el evento de soltar archivos."""
        self._on_drag_leave(None)
        files = self.root.tk.splitlist(event.data)
        if files:
            # Enviamos el archivo directamente al controlador
            self.controller.handle_file_selection(files[0])

    # --- Métodos de Actualización ---

    def update_metadata_display(self, text):
        """Muestra los metadatos en el área de texto."""
        self.drop_area.place_forget()
        self.scrollbar.grid()
        self._set_colors("#B8E1EA") 
        
        self.info_text.config(state="normal")
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, text)
        self.info_text.config(state="disabled")

    def reset_ui(self):
        """Restaura la UI al estado inicial."""
        self.info_text.config(state="normal")
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state="disabled")
        self.scrollbar.grid_remove()
        self.drop_area.place(relx=0.5, rely=0.5, anchor="center")
        self.drop_label.config(text=_("instruction.drag_drop"))
        self._set_colors(COLOR_ACCENT)

    # --- Gestión de Efectos Visuales ---

    def _set_colors(self, color):
        for w in (self.wrapper, self.info_text, self.drop_area, self.drop_label):
            w.config(bg=color)

    def _on_hover_enter(self, event):
        if not self.controller.is_metadata_active:
            self._set_colors("#B8E1EA")

    def _on_hover_leave(self, event):
        if not self.controller.is_metadata_active:
            self._set_colors(COLOR_ACCENT)

    def _on_drag_enter(self, event):
        if not self.controller.is_metadata_active:
            self._set_colors("#B8E1EA")
            self.drop_label.config(text=_("instruction.drop_now"))

    def _on_drag_leave(self, event):
        if not self.controller.is_metadata_active:
            self._set_colors(COLOR_ACCENT)
            self.drop_label.config(text=_("instruction.drag_drop"))

    def _setup_drag_and_drop(self):
        self.root.drop_target_register(DND_FILES)
