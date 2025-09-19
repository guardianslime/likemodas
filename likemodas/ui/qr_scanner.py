# likemodas/ui/qr_scanner.py (CORREGIDO)
import reflex as rx
from reflex.vars import Var

class QRScannerComponent(rx.Component):
    """
    Un componente de Reflex que envuelve la biblioteca 'html5-qrcode'
    para proporcionar un escáner de QR funcional.
    """
    # Se elimina la línea 'library' para que Reflex no intente importar
    # el componente desde el paquete de node.
    
    # El tag debe coincidir con el nombre del componente que exportamos en el código JS.
    tag = "Html5QrcodeScannerComponent"

    # Props que pasamos a la biblioteca JS
    fps: Var[int]
    qrbox: Var[int]
    verbose: Var[bool]

    # El manejador de eventos que envía los datos de vuelta a Python
    on_scan_success: rx.EventHandler[lambda decoded_text: [decoded_text]]

    def _get_custom_code(self) -> str:
        """
        Genera el código JS/React necesario para inicializar el escáner.
        Este código es ahora la única fuente de definición del componente.
        """
        # --- CORRECCIÓN: Se ha eliminado la línea "import React, { useEffect } from 'react';" ---
        return """
import { Html5QrcodeScanner } from 'html5-qrcode';

const Html5QrcodeScannerComponent = (props) => {
  const qrcodeRegionId = "html5qr-code-full-region";

  useEffect(() => {
    // Esta sección solo se ejecuta una vez cuando el componente se monta
    const html5QrcodeScanner = new Html5QrcodeScanner(
      qrcodeRegionId,
      {
        fps: props.fps || 10,
        qrbox: props.qrbox || 250,
      },
      props.verbose || false
    );

    const successCallback = (decodedText, decodedResult) => {
      // Llama al event handler de Reflex cuando el escaneo es exitoso
      if (props.on_scan_success) {
        props.on_scan_success(decodedText);
      }
    };

    const errorCallback = (errorMessage) => {
      // Manejo de errores (opcional)
    };

    html5QrcodeScanner.render(successCallback, errorCallback);

    // Función de limpieza para detener la cámara cuando el componente se desmonte
    return () => {
      // Asegurarse de que el scanner todavía existe antes de llamar a clear
      if (html5QrcodeScanner && html5QrcodeScanner.getState() !== 2) { // 2 es NOT_STARTED
          html5QrcodeScanner.clear().catch(error => {
            console.error("Failed to clear html5QrcodeScanner.", error);
          });
      }
    };
  }, []);

  return <div id={qrcodeRegionId} style={{ width: '100%' }} />;
};

export default Html5QrcodeScannerComponent;
"""

# Alias para facilitar la creación del componente
qr_scanner_component = QRScannerComponent.create