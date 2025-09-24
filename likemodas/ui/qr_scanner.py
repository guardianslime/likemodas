# likemodas/ui/qr_scanner.py (VERSIÓN FINAL Y ROBUSTA)
import reflex as rx

class JsQrScanner(rx.Component):
    """
    Un componente de Reflex que envuelve la librería 'jsqr' usando una
    implementación de React personalizada para un control total.
    """
    # Carga la librería jsqr desde una CDN. Es ligera y no requiere instalación.
    library = "jsqr"
    # El nombre de la etiqueta del componente React que definiremos en el código JS.
    tag = "JsQrScannerComponent"
    
    # Evento que se dispara cuando se escanea un código QR con éxito.
    # Pasa el texto decodificado (la URL) como argumento.
    on_scan_success: rx.EventHandler[lambda decoded_text: [decoded_text]]
    
    # Evento que se dispara si hay un error al acceder a la cámara.
    on_camera_error: rx.EventHandler[lambda error_message: [error_message]]

    def _get_imports(self) -> dict[str, str | list[str]]:
        """
        Define las importaciones necesarias para el componente de React.
        """
        return {
            "react": ["default as React"],
            "jsqr": ["default as jsQR"]
        }

    def _get_custom_code(self) -> str:
        """
        Aquí reside toda la lógica del frontend en JavaScript (React).
        Este código gestiona el acceso a la cámara, el bucle de escaneo y la
        comunicación de vuelta a Python.
        """
        return """
const JsQrScannerComponent = (props) => {
    const videoRef = React.useRef(null);
    const canvasRef = React.useRef(null);
    const streamRef = React.useRef(null);
    const requestRef = React.useRef(null);

    // Función para detener la cámara y el bucle de escaneo.
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

    // Bucle de escaneo que se ejecuta en cada frame de animación.
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

            // --- INICIO DE LA CORRECCIÓN DE LÓGICA ---
            if (code) {
                // 1. Enviamos el evento PRIMERO, usando las props directamente.
                if (props.on_scan_success) {
                    props.on_scan_success(code.data);
                }
                // 2. DESPUÉS, detenemos la cámara.
                stopWebcamScan();
                return; // Detenemos el bucle de escaneo.
            }
            // --- FIN DE LA CORRECCIÓN DE LÓGICA ---
        }
        // Si no se encuentra un código, se continúa con el siguiente frame.
        requestRef.current = requestAnimationFrame(scanVideoFrame);
    };

    // Función para iniciar el acceso a la cámara.
    const startWebcamScan = async () => {
        try {
            // Pide acceso a la cámara trasera preferentemente.
            const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
            streamRef.current = stream;
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                videoRef.current.play();
                // Inicia el bucle de escaneo.
                requestRef.current = requestAnimationFrame(scanVideoFrame);
            }
        } catch (error) {
            // Si hay un error (ej. el usuario deniega el permiso), se emite el evento de error.
            if (props.on_camera_error) {
                props.on_camera_error(`No se puede acceder a la cámara: ${error.message}`);
            }
        }
    };

    // Hook de React que se ejecuta cuando el componente se monta y se desmonta.
    React.useEffect(() => {
        startWebcamScan();
        // Función de limpieza: se asegura de que la cámara se apague si el componente se desmonta.
        return () => {
            stopWebcamScan();
        };
    }, []);

    // Renderiza los elementos de video (visible) y canvas (oculto).
    return (
        React.createElement("div", null,
            React.createElement("video", { ref: videoRef, style: { width: '100%' }, playsInline: true, muted: true }),
            React.createElement("canvas", { ref: canvasRef, style: { display: 'none' } })
        )
    );
};
"""

# Crea una "fábrica" para poder usar el componente fácilmente en otras partes del código.
qr_scanner_component = JsQrScanner.create