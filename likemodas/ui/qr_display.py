# En: likemodas/ui/qr_display.py (SOLUCIÓN DEFINITIVA)

import reflex as rx

# Si tu archivo tiene el código del QrCodeComponent, elimínalo o reemplázalo
# completamente por la función de abajo.

def qr_code_display(value: rx.Var[str], size: rx.Var[int] = 180, id: rx.Var[str] = "") -> rx.Component:
    """
    [VERSIÓN FINAL CON rx.image ESTÁNDAR]
    Muestra una imagen QR desde una URL o un Data URI.
    Asegura la etiqueta <img> para que el JavaScript pueda dibujarla en Canvas.
    Se ha ELIMINADO cross_origin="anonymous" ya que suele ser innecesario
    para Data URIs y puede causar fallos de carga.
    """
    return rx.box(
        rx.image(
            src=value,
            width=f"{size}px",
            height=f"{size}px",
            object_fit="contain",
            id=id, # Pasa el id al tag <img>
            # --- ✨ IMPORTANTE: ELIMINA o COMENTA la línea cross_origin ---
            # cross_origin="anonymous", # <<-- ¡QUITA ESTO!
            # -----------------------------------------------------------
        ),
        padding="1em",
        border="1px solid #EAEAEA",
        border_radius="md",
        bg="white", # Fondo blanco necesario para el Canvas
    )