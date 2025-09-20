# likemodas/ui/qr_display.py (NUEVA VERSIÓN COMPLETA)
import reflex as rx

class QRCodeDisplay(rx.Component):
    """Un componente que envuelve la librería 'react-qr-code'."""

    # 1. Cambiamos la librería a la nueva que instalamos
    library = "react-qr-code"
    tag = "QRCode"

    # 2. Las propiedades son las mismas, 'value' es la importante
    value: rx.Var[str]
    size: rx.Var[int] = 128
    bgColor: rx.Var[str] = "#FFFFFF"
    fgColor: rx.Var[str] = "#000000"
    
    # 3. Le decimos a Reflex que esta librería SÍ usa una importación por defecto
    def _get_imports(self) -> dict[str, str]:
        return {"react-qr-code": ["default as QRCode"]}

# Creamos un alias para que sea más fácil de usar.
qr_code_display = QRCodeDisplay.create