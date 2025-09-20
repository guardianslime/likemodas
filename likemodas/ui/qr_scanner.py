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
        Esta versión mejorada soluciona el error de redeclaración de 'useEffect'
        y añade una configuración más robusta para la cámara.
        """
        return """
import { Html5QrcodeScanner } from 'html5-qrcode';
// La importación de 'useEffect' se ha eliminado para evitar el conflicto con Reflex.

const Html5QrcodeScannerComponent = (props) => {
  // Un ID único para el elemento donde se renderizará el escáner.
  const qrcodeRegionId = "html5qr-code-full-region";

  useEffect(() => {
    // --- INICIO DE LA CORRECCIÓN DE LA CÁMARA ---
    // Una configuración más detallada para mayor compatibilidad con diversas cámaras.
    const config = {
      fps: props.fps || 10,
      // Define el cuadro de escaneo como un objeto para mayor claridad.
      qrbox: { width: 250, height: 250 },
      // Recuerda la última cámara utilizada para mejorar la experiencia.
      rememberLastUsedCamera: true,
      // Especifica que solo queremos usar la cámara.
      supportedScanTypes: [0] // 0 = Html5QrcodeScanType.SCAN_TYPE_CAMERA
    };
    // --- FIN DE LA CORRECCIÓN DE LA CÁMARA ---

    const html5QrcodeScanner = new Html5QrcodeScanner(
      qrcodeRegionId,
      config, // Usamos la nueva configuración mejorada
      props.verbose || false
    );

    const successCallback = (decodedText, decodedResult) => {
      if (props.on_scan_success) {
        // Detiene el escáner para liberar la cámara antes de enviar el resultado.
        html5QrcodeScanner.clear().catch(error => {
          console.error("Fallo al limpiar el escáner tras el éxito.", error);
        });
        props.on_scan_success(decodedText);
      }
    };

    const errorCallback = (errorMessage) => {
      // Manejo de errores (opcional).
    };

    html5QrcodeScanner.render(successCallback, errorCallback);

    // Función de limpieza para detener la cámara al cerrar el modal.
    return () => {
      if (html5QrcodeScanner && html5QrcodeScanner.getState() !== 2) { // 2 = NOT_STARTED
          html5QrcodeScanner.clear().catch(error => {
            console.error("Fallo al limpiar el escáner al cerrar.", error);
          });
      }
    };
  }, []); // El array vacío asegura que esto se ejecute solo una vez.

  return <div id={qrcodeRegionId} style={{ width: '100%' }} />;
};

export default Html5QrcodeScannerComponent;
"""

# Alias para facilitar la creación del componente en otras partes de tu app.
qr_scanner_component = QRScannerComponent.create