# likemodas/ui/qr_scanner.py (VERSIÓN DEFINITIVA con html5-qrcode)
import reflex as rx

class Html5QrCodeScanner(rx.Component):
    """
    Un componente robusto que envuelve la librería 'html5-qrcode' para un escaneo
    de QR simple y efectivo, manejando la cámara internamente.
    """
    # 1. Cambiamos la librería a la nueva que instalamos.
    library = "html5-qrcode"
    
    # 2. El tag ahora es un simple div que la librería usará.
    tag = "div"
    
    # 3. Mantenemos los mismos EventHandlers para no tener que cambiar el backend.
    on_scan_success: rx.EventHandler[lambda decoded_text: [decoded_text]]
    on_camera_error: rx.EventHandler[lambda error_message: [error_message]]
    
    # Le damos un ID único al div para que el script lo encuentre.
    def get_custom_attrs(self) -> dict:
        return {"id": "qr-reader"}

    # 4. Inyectamos un script mucho más simple usando _get_hooks.
    def _get_hooks(self) -> str | None:
        return """
        React.useEffect(() => {
            const qrScanner = new Html5Qrcode("qr-reader");
            let isScanning = true;

            const qrCodeSuccessCallback = (decodedText, decodedResult) => {
                if (isScanning) {
                    isScanning = false; // Evita escanear múltiples veces
                    qrScanner.stop().then(() => {
                        // Enviamos el resultado a Python
                        if (props.on_scan_success) {
                            props.on_scan_success(decodedText);
                        }
                    }).catch(err => console.error("Error al detener la cámara:", err));
                }
            };

            const config = { fps: 10, qrbox: { width: 250, height: 250 } };

            // Iniciar la cámara
            qrScanner.start({ facingMode: "environment" }, config, qrCodeSuccessCallback)
                .catch(err => {
                    // Si hay un error, lo enviamos a Python
                    if (props.on_camera_error) {
                        props.on_camera_error(`No se pudo iniciar la cámara: ${err}`);
                    }
                });

            // Función de limpieza para cuando el componente se cierra
            return () => {
                if (qrScanner.isScanning) {
                    qrScanner.stop().catch(err => console.error("Error al limpiar:", err));
                }
            };
        }, []);
        """

# Alias para facilitar la creación del componente.
qr_scanner_component = Html5QrCodeScanner.create