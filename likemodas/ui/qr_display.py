# likemodas/ui/qr_display.py

import reflex as rx

class QRCodeDisplay(rx.Component):
    """Un componente que envuelve la librería de React 'qrcode.react'."""

    # El nombre del paquete en npm que se instalará en el frontend.
    library = "qrcode.react"

    # El nombre de la etiqueta del componente en React.
    tag = "QRCode"

    # Las propiedades que acepta el componente.
    # 'value' es el texto que se convertirá en QR (tu VUID).
    value: rx.Var[str]

    # Propiedades opcionales para personalizar el estilo.
    size: rx.Var[int] = 128
    bgColor: rx.Var[str] = "#FFFFFF"
    fgColor: rx.Var[str] = "#000000"
    level: rx.Var[str] = "L"

# Creamos un alias para que sea más fácil de usar en nuestras páginas.
qr_code_display = QRCodeDisplay.create