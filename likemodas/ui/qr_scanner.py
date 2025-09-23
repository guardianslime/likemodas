# likemodas/ui/qr_scanner.py (NUEVA VERSIÓN)
import reflex as rx
from reflex.vars import Var

class QrReader(rx.Component):
    """
    Un componente de Reflex que envuelve la librería 'react-qr-reader',
    optimizada para una integración sencilla y un rendimiento superior.
    """
    # El nombre del paquete instalado vía npm
    library = "react-qr-reader"
    
    # El nombre del componente exportado por la librería
    tag = "QrReader"
    
    # El manejador de eventos que se llamará en AppState con el resultado
    on_result: rx.EventHandler[lambda result, error: [result.text if result else ""]]
    
    # Propiedades para configurar el comportamiento de la cámara
    constraints: Var[dict]
    scan_delay: Var[int]

# Alias para facilitar la creación del componente
qr_scanner_component = QrReader.create