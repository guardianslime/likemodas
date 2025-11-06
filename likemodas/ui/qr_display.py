# En: likemodas/ui/qr_display.py (VERSIÓN FINAL Y COMPROBADA)

import reflex as rx

# --- IMPORTANTE: Elimina o comenta cualquier componente QrCodeComponent
# class QrCodeComponent(NoSSRComponent):
#    ... (código del componente de terceros) ...
# ---

def qr_code_display(value: rx.Var[str], size: rx.Var[int] = 180, id: rx.Var[str] = "") -> rx.Component:
    """
    [VERSIÓN FINAL CON rx.image ESTÁNDAR]
    Muestra una imagen QR desde un Data URI (generado en el backend de Python).
    El ID se pasa directamente a la etiqueta <img> para que el JavaScript lo encuentre.
    """
    return rx.box(
        rx.image(
            # src es el Data URI (ej: 'data:image/png;base64,...')
            src=value,
            width=f"{size}px",
            height=f"{size}px",
            object_fit="contain",
            # ✨ EL ID DEBE ESTAR AQUÍ, en el rx.image que se convierte en <img> ✨
            id=id, 
            # cross_origin no es necesario si es Data URI, y si está, puede romperlo.
        ),
        padding="1em",
        border="1px solid #EAEAEA",
        border_radius="md",
        bg="white", # Necesario para copiar con fondo blanco
    )