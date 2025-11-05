# En: likemodas/ui/qr_display.py (Archivo COMPLETO y CORREGIDO)

import reflex as rx
from reflex.components.component import NoSSRComponent

class QrCodeComponent(NoSSRComponent):
    """
    Componente de Reflex que envuelve la librería 'react-qr-code'
    para mostrar códigos QR.
    """
    library = "react-qr-code"
    tag = "QRCode"

    # Parámetros que el componente de React espera.
    value: rx.Var[str]
    size: rx.Var[int]
    level: rx.Var[str]
    bgColor: rx.Var[str]
    fgColor: rx.Var[str]
    
    # --- ✨ INICIO: AÑADIR EL PROP 'id' ✨ ---
    id: rx.Var[str]
    # --- ✨ FIN: AÑADIR EL PROP 'id' ✨ ---

# Crea una instancia para un uso más sencillo
qr_code_component = QrCodeComponent.create

def qr_code_display(value: rx.Var[str], size: rx.Var[int] = 180, id: rx.Var[str] = "") -> rx.Component:
    """
    Muestra un código QR para el valor (URL) dado con una configuración robusta.
    Ahora acepta un 'id' para ser referenciado por JavaScript.
    """
    return rx.box(
        qr_code_component(
            value=value,
            size=size,
            level="H",  # Nivel de corrección de errores ALTO.
            bgColor="#FFFFFF",
            fgColor="#000000",
            id=id, # <-- Pasa el id al componente de React
        ),
        padding="1em",
        border="1px solid #EAEAEA",
        border_radius="md",
        bg="white",
    )