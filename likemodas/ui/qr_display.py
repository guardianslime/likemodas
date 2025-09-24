# likemodas/ui/qr_display.py
import reflex as rx

class QrCodeComponent(rx.Component):
    """
    Componente de Reflex que envuelve la librería 'react-qr-code'
    para mostrar códigos QR.
    """
    library = "react-qr-code"
    tag = "QRCode"

    # El valor (la URL) que se codificará en el QR.
    value: rx.Var[str]
    
    # El tamaño del QR en píxeles.
    size: rx.Var[int] = 256
    
    # Nivel de corrección de errores. 'H' (High) es el más robusto.
    # Esto hace que el QR sea mucho más fácil de leer para la cámara.
    level: rx.Var[str] = "H"
    
    # Color de fondo.
    bgColor: rx.Var[str] = "#FFFFFF"
    
    # Color de los módulos del QR.
    fgColor: rx.Var[str] = "#000000"

# Crea una instancia para un uso más sencillo
qr_code_component = QrCodeComponent.create

def qr_code_display(url: rx.Var[str]) -> rx.Component: # <--- NOMBRE CORREGIDO AQUÍ
    """
    Muestra un código QR para la URL dada con una configuración robusta.
    """
    return rx.box(
        qr_code_component(
            value=url,
            size=180,
            level="H", # Nivel de corrección de errores ALTO.
        ),
        padding="1em",
        border="1px solid #EAEAEA",
        border_radius="md",
        bg="white",
    )