# Ruta: likemodas/ui/qr_scanner.py
import reflex as rx
from reflex.vars import Var

class QRScannerComponent(rx.Component):
    tag = "Html5QrcodeScannerComponent"
    fps: Var[int]
    qrbox: Var[int]
    verbose: Var[bool]
    on_scan_success: rx.EventHandler[lambda decoded_text: [decoded_text]]

    def _get_custom_code(self) -> str:
        return """
import { Html5QrcodeScanner } from 'html5-qrcode';

const Html5QrcodeScannerComponent = (props) => {
  const qrcodeRegionId = "html5qr-code-full-region";

  useEffect(() => {
    const config = {
      fps: props.fps || 10,
      qrbox: { width: 250, height: 250 },
      rememberLastUsedCamera: true,
    };

    const html5QrcodeScanner = new Html5QrcodeScanner(
      qrcodeRegionId, config, props.verbose || false
    );

    const successCallback = (decodedText, decodedResult) => {
      if (props.on_scan_success) {
        // --- MENSAJE DE DEPURACIÓN EN EL NAVEGADOR ---
        console.log(`[DEBUG] Escaneo exitoso en frontend. Enviando VUID: ${decodedText}`);
        
        props.on_scan_success(decodedText);

        setTimeout(() => {
          html5QrcodeScanner.clear().catch(error => {
            console.error("Fallo al limpiar el escáner tras el éxito.", error);
          });
        }, 100);
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

qr_scanner_component = QRScannerComponent.create