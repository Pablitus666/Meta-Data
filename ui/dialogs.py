import tkinter as tk
from tkinter import Toplevel
import os
from config.settings import (
    COLOR_PRIMARY, COLOR_TEXT_PRIMARY, COLOR_GOLD,
    LOGO_ICO, ROBOT_PNG, BOTON_PNG, FONT_DIALOG
)
from .widgets import create_image_button
from core.i18n import _

def center_window(ventana, ancho=None, alto=None):
    """Centra la ventana en la pantalla. Si no se pasan dimensiones, usa las actuales."""
    ventana.update_idletasks()
    
    if ancho is None:
        ancho = ventana.winfo_reqwidth()
    if alto is None:
        alto = ventana.winfo_reqheight()
        
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    
    x = (pantalla_ancho // 2) - (ancho // 2)
    y = (pantalla_alto // 2) - (alto // 2)
    
    # Aplicar geometría y forzar actualización
    ventana.geometry(f'{ancho}x{alto}+{x}+{y}')

class AboutDialog(Toplevel):
    def __init__(self, parent, image_manager):
        super().__init__(parent)
        self.image_manager = image_manager
        self.withdraw()
        self.title(_("title.info"))
        self.config(bg=COLOR_PRIMARY)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        try:
            if os.path.exists(LOGO_ICO):
                self.iconbitmap(LOGO_ICO)
        except Exception:
            pass
            
        self._create_widgets()
        center_window(self) # Ahora usa el tamaño calculado por los widgets
        self.deiconify()

    def _create_widgets(self):
        # Frame principal con padding para que no toque los bordes
        frame_info = tk.Frame(self, bg=COLOR_PRIMARY)
        frame_info.pack(pady=15, padx=15, fill="both", expand=True)

        # Usamos grid para el layout interno (Robot a la izquierda, Texto/Botón a la derecha)
        frame_info.grid_columnconfigure(0, weight=0)
        frame_info.grid_columnconfigure(1, weight=1)

        # Imagen del Robot
        robot_photo = self.image_manager.load(ROBOT_PNG, size=(120, 120), add_shadow_effect=False)
        if robot_photo:
            img_label = tk.Label(frame_info, image=robot_photo, bg=COLOR_PRIMARY)
            img_label.image = robot_photo
            img_label.grid(row=0, column=0, padx=(0, 15), pady=0, rowspan=2, sticky="nsew")

        # Mensaje de información
        message = tk.Label(
            frame_info, 
            text=_("info.developed_by"),
            justify="center", 
            bg=COLOR_PRIMARY, 
            fg=COLOR_TEXT_PRIMARY,
            font=("Segoe UI", 11, "bold"),
            wraplength=180
        )
        message.grid(row=0, column=1, sticky="nsew", pady=(5, 10))

        # Contenedor para el botón
        btn_holder = tk.Frame(frame_info, bg=COLOR_PRIMARY, width=120, height=45)
        btn_holder.pack_propagate(False)
        btn_holder.grid(row=1, column=1, sticky="n", pady=(5, 0))

        self.close_btn = create_image_button(
            btn_holder, _("button.close"), self.destroy, self.image_manager, 
            BOTON_PNG, (110, 35)
        )
        self.close_btn.place(relx=0.5, rely=0.5, anchor="center")

def show_error(root, title, message, image_manager):
    """Muestra una ventana de error profesional."""
    _show_custom_dialog(root, title, message, COLOR_PRIMARY, image_manager)

def show_success(root, title, message, image_manager):
    """Muestra una ventana de éxito profesional."""
    _show_custom_dialog(root, title, message, COLOR_PRIMARY, image_manager)

def show_confirm(root, title, message, image_manager):
    """Muestra una ventana de confirmación profesional y retorna True o False."""
    dialog = Toplevel(root)
    dialog.withdraw()
    dialog.title(title)
    dialog.config(bg=COLOR_PRIMARY)
    dialog.resizable(0, 0)
    dialog.transient(root)
    dialog.grab_set()

    result = [False]

    def on_confirm():
        result[0] = True
        dialog.destroy()

    try:
        if os.path.exists(LOGO_ICO):
            dialog.iconbitmap(LOGO_ICO)
    except Exception:
        pass
    
    frame = tk.Frame(dialog, bg=COLOR_PRIMARY)
    frame.pack(pady=15, padx=20, fill="both", expand=True)
    
    label = tk.Label(
        frame, text=message, bg=COLOR_PRIMARY, fg=COLOR_TEXT_PRIMARY, 
        font=("Segoe UI", 11, "bold"), wraplength=320, justify="center"
    )
    label.pack(expand=True, pady=(10, 15))
    
    btn_frame = tk.Frame(frame, bg=COLOR_PRIMARY)
    btn_frame.pack(pady=5)
    
    # Contenedores para botones
    btn_acc_cont = tk.Frame(btn_frame, bg=COLOR_PRIMARY, width=120, height=45)
    btn_acc_cont.pack_propagate(False)
    btn_acc_cont.grid(row=0, column=0, padx=10)
    
    btn_can_cont = tk.Frame(btn_frame, bg=COLOR_PRIMARY, width=120, height=45)
    btn_can_cont.pack_propagate(False)
    btn_can_cont.grid(row=0, column=1, padx=10)

    create_image_button(btn_acc_cont, _("button.accept"), on_confirm, image_manager, BOTON_PNG, (110, 35)).place(relx=0.5, rely=0.5, anchor="center")
    create_image_button(btn_can_cont, _("button.cancel"), dialog.destroy, image_manager, BOTON_PNG, (110, 35)).place(relx=0.5, rely=0.5, anchor="center")

    center_window(dialog) # Dinámico
    dialog.deiconify()

    root.wait_window(dialog)
    return result[0]

def _show_custom_dialog(root, title, message, bg_color, image_manager):
    """Función interna para crear diálogos consistentes y dinámicos."""
    dialog = Toplevel(root)
    dialog.withdraw()
    dialog.title(title)
    dialog.config(bg=bg_color)
    dialog.resizable(0, 0)
    dialog.transient(root)
    dialog.grab_set()

    try:
        if os.path.exists(LOGO_ICO):
            dialog.iconbitmap(LOGO_ICO)
    except Exception:
        pass
    
    frame = tk.Frame(dialog, bg=bg_color)
    frame.pack(pady=15, padx=20, fill="both", expand=True)
    
    label = tk.Label(
        frame, text=message, bg=bg_color, fg=COLOR_TEXT_PRIMARY, 
        font=("Segoe UI", 11, "bold"), wraplength=300, justify="center"
    )
    label.pack(expand=True, pady=(10, 15))
    
    btn_container = tk.Frame(frame, bg=bg_color, width=120, height=45)
    btn_container.pack_propagate(False)
    btn_container.pack(pady=(5, 0))
    
    close_btn = create_image_button(btn_container, _("button.accept"), dialog.destroy, image_manager, BOTON_PNG, (110, 35))
    close_btn.place(relx=0.5, rely=0.5, anchor="center")

    center_window(dialog) # Ahora se ajusta al contenido automáticamente
    dialog.deiconify()
