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
        [VERSIÓN FINAL DEFINITIVA]
        Genera el código JS/React necesario para inicializar el escáner.
        Soluciona la condición de carrera (race condition) añadiendo un
        pequeño retraso antes de limpiar el escáner, asegurando que el
        evento se envíe correctamente al backend.
        """
        return """
import { Html5QrcodeScanner } from 'html5-qrcode';

// No se importa React ni useEffect, ya que Reflex los provee.

const Html5QrcodeScannerComponent = (props) => {
  const qrcodeRegionId = "html5qr-code-full-region";

  useEffect(() => {
    const config = {
      fps: props.fps || 10,
      qrbox: { width: 250, height: 250 },
      rememberLastUsedCamera: true,
    };

    const html5QrcodeScanner = new Html5QrcodeScanner(
      qrcodeRegionId,
      config,
      props.verbose || false
    );

    const successCallback = (decodedText, decodedResult) => {
      if (props.on_scan_success) {
        // 1. Envía el dato a Python.
        props.on_scan_success(decodedText);

        // 2. SOLUCIÓN DEFINITIVA: Espera 100ms antes de limpiar.
        // Esto le da tiempo al WebSocket de Reflex para procesar el evento
        // antes de que el componente se desmonte.
        setTimeout(() => {
          html5QrcodeScanner.clear().catch(error => {
            console.error("Fallo al limpiar el escáner tras el éxito.", error);
          });
        }, 100);
      }
    };

    const errorCallback = (errorMessage) => {
      // No hacer nada en caso de error para que el escáner siga activo.
    };

    html5QrcodeScanner.render(successCallback, errorCallback);

    // Función de limpieza que se ejecuta cuando el componente se desmonta (cierra)
    return () => {
      if (html5QrcodeScanner && html5QrcodeScanner.getState() !== 2) { // 2 = NOT_STARTED
          html5QrcodeScanner.clear().catch(error => {
            console.error("Fallo al limpiar el escáner al cerrar.", error);
          });
      }
    };
  }, []); // El array vacío asegura que useEffect se ejecute solo una vez

  return <div id={qrcodeRegionId} style={{ width: '100%' }} />;
};

export default Html5QrcodeScannerComponent;
"""

# Alias para facilitar la creación del componente en otras partes de tu app.
qr_scanner_component = QRScannerComponent.create