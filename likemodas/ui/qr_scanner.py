# likemodas/ui/qr_scanner.py (VERSIÓN FINAL Y COMPLETA)
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

    # --- INICIO DE LA CORRECCIÓN ---
    # Este método le dice a Reflex cómo importar la librería jsqr correctamente.
    def _get_imports(self) -> dict[str, str]:
        """
        Especifica que se debe importar la exportación 'default' de la librería 'jsqr'
        y asignarle el alias 'jsQR' para que el código personalizado pueda usarlo.
        """
        return {"jsqr": ["default as jsQR"]}
    # --- FIN DE LA CORRECCIÓN ---

    def _get_custom_code(self) -> str:
        # Tu código JavaScript personalizado se mantiene exactamente igual.
        # Ya no lo incluyo aquí por brevedad, pero no necesita cambios.
        return """
const JsQrScannerComponent = (props) => {
  const videoRef = React.useRef(null);
  const canvasRef = React.useRef(null);
  const streamRef = React.useRef(null);
  const requestRef = React.useRef(null);

  const scanVideoFrame = () => {
    if (videoRef.current && videoRef.current.readyState === videoRef.current.HAVE_ENOUGH_DATA) {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      const ctx = canvas.getContext('2d');
      canvas.height = video.videoHeight;
      canvas.width = video.videoWidth;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const code = jsQR(imageData.data, imageData.width, imageData.height);

      if (code) {
        stopWebcamScan();
        if (props.on_scan_success) {
          props.on_scan_success(code.data);
        }
        return;
      }
    }
    requestRef.current = requestAnimationFrame(scanVideoFrame);
  };

  const startWebcamScan = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
      streamRef.current = stream;
      videoRef.current.srcObject = stream;
      videoRef.current.play();
      requestRef.current = requestAnimationFrame(scanVideoFrame);
    } catch (error) {
      if (props.on_camera_error) {
        props.on_camera_error(`No se puede acceder a la cámara: ${error.message}`);
      }
    }
  };

  const stopWebcamScan = () => {
    if (requestRef.current) {
      cancelAnimationFrame(requestRef.current);
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  };

  React.useEffect(() => {
    startWebcamScan();
    return () => stopWebcamScan();
  }, []);

  return (
    React.createElement("div", null,
      React.createElement("video", { ref: videoRef, style: { width: '100%' }, playsInline: true, muted: true }),
      React.createElement("canvas", { ref: canvasRef, style: { display: 'none' } })
    )
  );
};
"""

# Alias para facilitar la creación del componente
qr_scanner_component = JsQrScanner.create