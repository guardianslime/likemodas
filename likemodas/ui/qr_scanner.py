import reflex as rx
from reflex.vars import Var

class QRScannerComponent(rx.Component):
    """
    Un componente de Reflex que envuelve la biblioteca 'html5-qrcode'
    para proporcionar un escáner de QR funcional.
    """
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
        """
        return """
import { Html5QrcodeScanner } from 'html5-qrcode';

const Html5QrcodeScannerComponent = (props) => {
  const qrcodeRegionId = "html5qr-code-full-region";

  useEffect(() => {
    const html5QrcodeScanner = new Html5QrcodeScanner(
      qrcodeRegionId,
      {
        fps: props.fps || 10,
        qrbox: props.qrbox || 250,
      },
      props.verbose || false
    );

    const successCallback = (decodedText, decodedResult) => {
      if (props.on_scan_success) {
        props.on_scan_success(decodedText);
      }
    };

    const errorCallback = (errorMessage) => {
      // Manejo de errores (opcional)
    };

    html5QrcodeScanner.render(successCallback, errorCallback);

    return () => {
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