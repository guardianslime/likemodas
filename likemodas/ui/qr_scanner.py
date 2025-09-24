# likemodas/ui/qr_scanner.py (VERSIÓN FINAL CON TODAS LAS IMPORTACIONES)
import reflex as rx

class Html5QrCodeScanner(rx.Component):
    """
    Un componente robusto que envuelve la librería 'html5-qrcode' para un escaneo
    de QR simple y efectivo, manejando la cámara internamente.
    """
    tag = "div"
    
    on_scan_success: rx.EventHandler[lambda decoded_text: [decoded_text]]
    on_camera_error: rx.EventHandler[lambda error_message: [error_message]]
    
    def get_custom_attrs(self) -> dict:
        return {"id": "qr-reader"}

    # --- INICIO DE LA CORRECCIÓN ---
    # Añadimos de nuevo la importación de React que se había perdido.
    def _get_imports(self) -> dict[str, str | list[str]]:
        return {
            "react": ["default as React"],  # <-- ¡ESTA LÍNEA ES LA QUE FALTABA!
            "html5-qrcode": ["Html5Qrcode"]
        }
    # --- FIN DE LA CORRECCIÓN ---

    def _get_hooks(self) -> str | None:
        return """
        React.useEffect(() => {
            const qrScanner = new Html5Qrcode("qr-reader");
            let isScanning = true;

            const qrCodeSuccessCallback = (decodedText, decodedResult) => {
                if (isScanning) {
                    isScanning = false;
                    qrScanner.stop().then(() => {
                        if (props.on_scan_success) {
                            props.on_scan_success(decodedText);
                        }
                    }).catch(err => console.error("Error al detener la cámara:", err));
                }
            };

            const config = { fps: 10, qrbox: { width: 250, height: 250 } };

            qrScanner.start({ facingMode: "environment" }, config, qrCodeSuccessCallback)
                .catch(err => {
                    if (props.on_camera_error) {
                        props.on_camera_error(`No se pudo iniciar la cámara: ${err}`);
                    }
                });

            return () => {
                if (qrScanner && qrScanner.isScanning) {
                    qrScanner.stop().catch(err => console.error("Error al limpiar:", err));
                }
            };
        }, []);
        """

qr_scanner_component = Html5QrCodeScanner.create