# likemodas/ui/qr_scanner.py (ARCHIVO COMPLETO Y CORREGIDO)

import reflex as rx
from reflex.vars import Var

class QRScannerComponent(rx.Component):
    """
    Un componente de Reflex que envuelve la biblioteca 'html5-qrcode'
    para proporcionar un escáner de QR funcional.
    """
    tag = "Html5QrcodeScannerComponent"

    # Props que pasamos desde Python a la biblioteca JS
    fps: Var[int]
    qrbox: Var[int]
    verbose: Var[bool]

    # El manejador de eventos que envía los datos escaneados de vuelta a Python
    on_scan_success: rx.EventHandler[lambda decoded_text: [decoded_text]]

    def _get_custom_code(self) -> str:
        """
        Genera el código JS/React necesario para inicializar el escáner.
        Esta versión restaura la opción de subir archivos.
        """
        return """
import { Html5QrcodeScanner } from 'html5-qrcode';

const Html5QrcodeScannerComponent = (props) => {
  const qrcodeRegionId = "html5qr-code-full-region";

  useEffect(() => {
    const config = {
      fps: props.fps || 10,
      qrbox: { width: 250, height: 250 },
      rememberLastUsedCamera: true,
      
      // --- CORRECCIÓN AQUÍ ---
      // Se ha eliminado la línea "supportedScanTypes: [0]".
      // Al no especificarlo, la librería mostrará por defecto tanto la cámara
      // como la opción para escanear una imagen desde un archivo.
    };

    const html5QrcodeScanner = new Html5QrcodeScanner(
      qrcodeRegionId,
      config,
      props.verbose || false
    );

    const successCallback = (decodedText, decodedResult) => {
      if (props.on_scan_success) {
        props.on_scan_success(decodedText);
        html5QrcodeScanner.clear().catch(error => {
          console.error("Fallo al limpiar el escáner tras el éxito.", error);
        });
      }
    };

    const errorCallback = (errorMessage) => {};

    html5QrcodeScanner.render(successCallback, errorCallback);

    return () => {
      if (html5QrcodeScanner && html5QrcodeScanner.getState() !== 2) {
          html5QrcodeScanner.clear().catch(error => {
            console.error("Fallo al limpiar el escáner al cerrar.", error);
          });
      }
    };
  }, []);

  return <div id={qrcodeRegionId} style={{ width: '100%' }} />;
};

export default Html5QrcodeScannerComponent;
"""

# Alias para facilitar la creación del componente en otras partes de tu app.
qr_scanner_component = QRScannerComponent.create