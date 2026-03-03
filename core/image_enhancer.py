from PIL import Image, ImageFilter

def add_shadow(image: Image.Image, offset=(2, 2), shadow_color=(0, 0, 0, 128), blur_radius=3, border=5):
    """
    Añade una sombra paralela a una imagen PIL transparente en un lienzo simétrico.
    Esto asegura que el centro del botón sea el centro del lienzo.
    """
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # Margen simétrico para centrado perfecto
    pad = max(abs(offset[0]), abs(offset[1])) + border
    
    total_width = image.width + 2 * pad
    total_height = image.height + 2 * pad
    
    # Crear fondo transparente
    shadow_image = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
    
    # Capa de sombra (silueta de la imagen original)
    shadow_layer = Image.new('RGBA', image.size, shadow_color)
    
    # Pegar la sombra con el desplazamiento (offset)
    shadow_image.paste(shadow_layer, (pad + offset[0], pad + offset[1]), image.getchannel('A'))
    
    # Aplicar desenfoque (blur)
    if blur_radius > 0:
        shadow_image = shadow_image.filter(ImageFilter.GaussianBlur(blur_radius))
    
    # Pegar la imagen original en el centro exacto (pad, pad)
    shadow_image.paste(image, (pad, pad), image)
    
    return shadow_image
