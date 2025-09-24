# likemodas/ui/qr_scanner.py (VERSIÓN FINAL CON rx.Box)
import reflex as rx

# --- INICIO DE LA CORRECCIÓN DEFINITIVA ---
# Heredamos de rx.Box, que es el componente de Reflex para crear contenedores <div>.
# Esta es la clase correcta y existente.
class Html5QrCodeScanner(rx.Box):
# --- FIN DE LA CORRECCIÓN DEFINITIVA ---
    """
    Un componente robusto que envuelve la librería 'html5-qrcode' para un escaneo
    de QR simple y efectivo, manejando la cámara internamente.
    """
    
    # La propiedad 'tag' se elimina, ya que rx.Box es un <div> por defecto.
    
    # Los EventHandlers se mantienen igual.
    on_scan_success: rx.EventHandler[lambda decoded_text: [decoded_text]]
    on_camera_error: rx.EventHandler[lambda error_message: [error_message]]
    
    # El ID para que el script encuentre el elemento se mantiene.
    def get_custom_attrs(self) -> dict:
        return {"id": "qr-reader"}

    # Las importaciones de JS siguen siendo necesarias.
    def _get_imports(self) -> dict[str, str | list[str]]:
        return {
            "react": ["default as React"],
            "html5-qrcode": ["Html5Qrcode"]
        }

    # El script que se ejecuta en el navegador se mantiene igual.
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

# El alias se mantiene igual.
qr_scanner_component = Html5QrCodeScanner.create