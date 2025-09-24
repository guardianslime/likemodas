# likemodas/ui/qr_display.py
import reflex as rx

class QrCodeComponent(rx.Component):
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

# Crea una instancia para un uso más sencillo
qr_code_component = QrCodeComponent.create

def qr_code_display(value: rx.Var[str], size: rx.Var[int] = 180) -> rx.Component:
    """
    Muestra un código QR para el valor (URL) dado con una configuración robusta.
    
    Args:
        value: La URL o texto a codificar en el QR.
        size: El tamaño en píxeles del QR.
    """
    return rx.box(
        qr_code_component(
            value=value,
            size=size,
            level="H",  # Nivel de corrección de errores ALTO.
            bgColor="#FFFFFF",
            fgColor="#000000",
        ),
        padding="1em",
        border="1px solid #EAEAEA",
        border_radius="md",
        bg="white",
    )