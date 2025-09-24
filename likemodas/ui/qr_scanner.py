# likemodas/ui/qr_scanner.py (VERSIÓN FINAL, CORRECTA Y CANÓNICA)
import reflex as rx

# 1. Volvemos a heredar de rx.Component. Esta es la base correcta para TODOS los componentes personalizados.
class Html5QrCodeScanner(rx.Component):
    """
    Un componente robusto que envuelve la librería 'html5-qrcode' para un escaneo
    de QR simple y efectivo, manejando la cámara internamente.
    """
    
    # 2. Especificamos que este componente debe renderizar una etiqueta <div> de HTML.
    tag = "div"
    
    # Los EventHandlers se mantienen igual.
    on_scan_success: rx.EventHandler[lambda decoded_text: [decoded_text]]
    on_camera_error: rx.EventHandler[lambda error_message: [error_message]]
    
    # El ID para que el script encuentre el elemento se mantiene.
    def get_custom_attrs(self) -> dict:
        return {"id": "qr-reader"}

    # 3. Mantenemos las importaciones que resuelven los errores de JavaScript.
    def _get_imports(self) -> dict[str, str | list[str]]:
        return {
            "react": ["default as React"],
            "html5-qrcode": ["Html5Qrcode"]
        }

    # 4. El script que se ejecuta en el navegador se mantiene igual.
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