import tkinter as tk
from config.settings import COLOR_PRIMARY, COLOR_TEXT_PRIMARY, COLOR_GOLD, FONT_BUTTON

def create_image_button(parent, text, command, image_manager, filename, image_size=(120, 40), shadow_color=(0, 0, 0, 100)):
    """
    Crea un botón personalizado con imagen de fondo (HD + Sombra), 
    texto centrado y efecto hover profesional.
    """
    # Cargar imagen con el ImageManager (DPI + Sombra)
    photo = image_manager.load(
        filename, 
        size=image_size, 
        add_shadow_effect=True,
        shadow_offset=(2, 2),
        shadow_color=shadow_color,
        blur_radius=3,
        border=5
    )

    button = tk.Button(
        parent,
        text=text,
        image=photo,
        compound="center",
        command=command,
        relief="flat",
        bg=COLOR_PRIMARY,
        fg=COLOR_TEXT_PRIMARY,
        font=FONT_BUTTON,
        activebackground=COLOR_PRIMARY,
        activeforeground=COLOR_TEXT_PRIMARY,
        borderwidth=0,
        highlightthickness=0,
        cursor="hand2"
    )

    if photo:
        button.photo = photo

    # Efectos Hover (Cambio de color de texto)
    button.bind("<Enter>", lambda e: button.config(fg=COLOR_GOLD))
    button.bind("<Leave>", lambda e: button.config(fg=COLOR_TEXT_PRIMARY))

    # Efecto de presión (movimiento visual hacia abajo)
    button.bind("<Button-1>", lambda e: button.place_configure(rely=0.54) if button.winfo_manager() == "place" else None)
    button.bind("<ButtonRelease-1>", lambda e: button.place_configure(rely=0.5) if button.winfo_manager() == "place" else None)
    
    return button
