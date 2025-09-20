# likemodas/ui/qr_display.py (COMPLETO Y CORREGIDO)
import reflex as rx

class QRCodeDisplay(rx.Component):
    """Un componente que envuelve la librería de React 'qrcode.react'."""

    library = "qrcode.react"
    tag = "QRCode"  # El nombre que le daremos después de importar

    # Props que acepta el componente.
    value: rx.Var[str]
    size: rx.Var[int] = 128
    bgColor: rx.Var[str] = "#FFFFFF"
    fgColor: rx.Var[str] = "#000000"
    level: rx.Var[str] = "L"

    # --- 👇 MÉTODO AÑADIDO PARA CORREGIR LA IMPORTACIÓN 👇 ---
    def _get_imports(self) -> dict[str, str]:
        # Le decimos a Reflex: "De 'qrcode.react', importa la exportación
        # por defecto (default) y llámala 'QRCode'".
        return {"qrcode.react": ["default as QRCode"]}
    # --- 👆 FIN DE LA CORRECCIÓN 👆 ---

# Creamos un alias para que sea más fácil de usar.
qr_code_display = QRCodeDisplay.create