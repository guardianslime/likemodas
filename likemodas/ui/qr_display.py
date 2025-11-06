# En: likemodas/ui/qr_display.py (SOLUCIÓN CORS)

import reflex as rx

def qr_code_display(value: rx.Var[str], size: rx.Var[int] = 180, id: rx.Var[str] = "") -> rx.Component:
    """
    [VERSIÓN FINAL CON CORS]
    Muestra una imagen QR y añade cross_origin="anonymous" para permitir
    el copiado de la imagen a través de Canvas (prevención de CORS/Tainting).
    """
    return rx.box(
        rx.image(
            src=value,
            width=f"{size}px",
            height=f"{size}px",
            object_fit="contain",
            id=id, 
            # --- ✨ CORRECCIÓN CRÍTICA: AÑADIR cross_origin="anonymous" para Canvas API ✨ ---
            cross_origin="anonymous",
            # --- ✨ FIN CORRECCIÓN CRÍTICA ✨ ---
        ),
        padding="1em",
        border="1px solid #EAEAEA",
        border_radius="md",
        bg="white", 
    )