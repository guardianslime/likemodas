# En: likemodas/ui/qr_display.py (Archivo COMPLETO y CORREGIDO)

import reflex as rx

def qr_code_display(value: rx.Var[str], size: rx.Var[int] = 180, id: rx.Var[str] = "") -> rx.Component:
    """
    [VERSIÓN CORREGIDA]
    Muestra una imagen QR desde una URL o un Data URI.
    Usa un rx.image estándar, pero mantiene el padding y fondo blanco
    para que se vea bien y se pueda guardar con fondo.
    """
    return rx.box(
        rx.image(
            src=value,
            width=f"{size}px",
            height=f"{size}px",
            object_fit="contain",
            id=id, # Pasa el id al tag <img>
        ),
        padding="1em",
        border="1px solid #EAEAEA",
        border_radius="md",
        bg="white", # Fondo blanco para que "Guardar Imagen" funcione bien
    )