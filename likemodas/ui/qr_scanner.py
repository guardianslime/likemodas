# likemodas/ui/qr_scanner.py (VERSIÓN CON DEPURACIÓN)
import reflex as rx

class JsQrScanner(rx.Component):
    """
    Un componente de Reflex que envuelve la librería 'jsqr' usando una
    implementación de React personalizada para un control total.
    """
    library = "jsqr"
    tag = "JsQrScannerComponent"
    
    on_scan_success: rx.EventHandler[lambda decoded_text: [decoded_text]]
    on_camera_error: rx.EventHandler[lambda error_message: [error_message]]

    def _get_imports(self) -> dict[str, str | list[str]]:
        return {
            "react": ["default as React"],
            "jsqr": ["default as jsQR"]
        }

    def _get_custom_code(self) -> str:
        return """
const JsQrScannerComponent = (props) => {
    const videoRef = React.useRef(null);
    const canvasRef = React.useRef(null);
    const streamRef = React.useRef(null);
    const requestRef = React.useRef(null);

    const stopWebcamScan = () => {
        if (requestRef.current) {
            cancelAnimationFrame(requestRef.current);
            requestRef.current = null;
        }
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
    };

    const scanVideoFrame = () => {
        if (videoRef.current && videoRef.current.readyState === videoRef.current.HAVE_ENOUGH_DATA) {
            const canvas = canvasRef.current;
            const video = videoRef.current;
            const ctx = canvas.getContext('2d', { willReadFrequently: true });
            
            canvas.height = video.videoHeight;
            canvas.width = video.videoWidth;
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const code = jsQR(imageData.data, imageData.width, imageData.height);

            if (code) {
                // --- INICIO DE LA LÍNEA DE DEPURACIÓN ---
                // Mostramos en la consola del navegador la URL que hemos encontrado.
                console.log("QR Code detected:", code.data);
                // --- FIN DE LA LÍNEA DE DEPURACIÓN ---

                if (props.on_scan_success) {
                    props.on_scan_success(code.data);
                }
                stopWebcamScan();
                return;
            }
        }
        requestRef.current = requestAnimationFrame(scanVideoFrame);
    };

    const startWebcamScan = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
            streamRef.current = stream;
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                videoRef.current.play();
                requestRef.current = requestAnimationFrame(scanVideoFrame);
            }
        } catch (error) {
            if (props.on_camera_error) {
                props.on_camera_error(`No se puede acceder a la cámara: ${error.message}`);
            }
        }
    };

    React.useEffect(() => {
        startWebcamScan();
        return () => {
            stopWebcamScan();
        };
    }, []);

    return (
        React.createElement("div", null,
            React.createElement("video", { ref: videoRef, style: { width: '100%' }, playsInline: true, muted: true }),
            React.createElement("canvas", { ref: canvasRef, style: { display: 'none' } })
        )
    );
};
"""

qr_scanner_component = JsQrScanner.create