# likemodas/ui/qr_scanner.py (VERSIÓN CANÓNICA Y FINAL)
import reflex as rx

class Html5QrCodeScanner(rx.Component):
    """
    Un componente robusto que envuelve la librería 'html5-qrcode' para un escaneo
    de QR simple y efectivo, manejando la cámara internamente.
    """
    # 1. El tag es un 'div' normal de HTML. No se importa de ninguna librería.
    tag = "div"
    
    # 2. ELIMINAMOS la propiedad `library`. Esto evita que Reflex intente
    #    importar el 'div' desde 'html5-qrcode'.
    
    # 3. Mantenemos los mismos EventHandlers.
    on_scan_success: rx.EventHandler[lambda decoded_text: [decoded_text]]
    on_camera_error: rx.EventHandler[lambda error_message: [error_message]]
    
    # Le damos un ID único al div para que el script lo encuentre.
    def get_custom_attrs(self) -> dict:
        return {"id": "qr-reader"}

    # 4. Usamos _get_imports para importar la CLASE que necesitamos en nuestro script.
    def _get_imports(self) -> dict[str, str | list[str]]:
        return {"html5-qrcode": ["Html5Qrcode"]}

    # 5. El script en _get_hooks ahora tendrá acceso a la clase Html5Qrcode.
    def _get_hooks(self) -> str | None:
        return """
        React.useEffect(() => {
            // Esta variable ahora está definida gracias a _get_imports.
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
                // Verificamos si qrScanner se inicializó y si está escaneando antes de detener.
                if (qrScanner && qrScanner.isScanning) {
                    qrScanner.stop().catch(err => console.error("Error al limpiar:", err));
                }
            };
        }, []);
        """

# Alias para facilitar la creación del componente.
qr_scanner_component = Html5QrCodeScanner.create