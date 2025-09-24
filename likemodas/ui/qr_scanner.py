# likemodas/ui/qr_scanner.py (VERSIÓN FINAL CON CÓDIGO JS INTEGRADO)
import reflex as rx

class JsQrScanner(rx.Component):
    """
    Un componente de Reflex que envuelve la librería 'jsqr' usando una
    implementación de React personalizada para un control total.
    """
    # La librería de bajo nivel que usará nuestro código JS.
    library = "jsqr"
    
    # El nombre del componente que definimos en el código JS de abajo.
    tag = "JsQrScannerComponent"
    
    # --- MANEJADORES DE EVENTOS ---
    # Evento para cuando un QR se decodifica con éxito.
    on_scan_success: rx.EventHandler[lambda decoded_text: [decoded_text]]
    
    # Evento para cuando la cámara no puede iniciarse.
    on_camera_error: rx.EventHandler[lambda error_message: [error_message]]

    # Esta función inyecta tu lógica de React directamente.
    def _get_custom_code(self) -> str:
        return """
import React, { useRef, useEffect } from 'react';
import jsQR from 'jsqr';

const JsQrScannerComponent = (props) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const requestRef = useRef(null);

  // Función para procesar los fotogramas del video
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

      // --- ¡ESTA ES LA CONEXIÓN CLAVE! ---
      if (code) {
        // Si se encuentra un código, se detiene el escaneo...
        stopWebcamScan();
        // ...y se llama al evento de Python con el resultado.
        if (props.on_scan_success) {
          props.on_scan_success(code.data);
        }
        return; // Salir del bucle
      }
    }
    // Si no se encuentra, seguir escaneando el siguiente fotograma.
    requestRef.current = requestAnimationFrame(scanVideoFrame);
  };

  // Función para iniciar la cámara
  const startWebcamScan = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
      streamRef.current = stream;
      videoRef.current.srcObject = stream;
      videoRef.current.play();
      requestRef.current = requestAnimationFrame(scanVideoFrame);
    } catch (error) {
      // Si hay un error, se llama al otro evento de Python.
      if (props.on_camera_error) {
        props.on_camera_error(`No se puede acceder a la cámara: ${error.message}`);
      }
    }
  };

  // Función para detener la cámara
  const stopWebcamScan = () => {
    if (requestRef.current) {
      cancelAnimationFrame(requestRef.current);
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  };

  // Efecto para iniciar y detener la cámara con el ciclo de vida del componente
  useEffect(() => {
    startWebcamScan();
    // Esto se ejecuta cuando el modal se cierra, deteniendo la cámara.
    return () => stopWebcamScan();
  }, []);

  // El HTML que se renderiza: un video y un canvas oculto.
  return (
    <div>
      <video ref={videoRef} style={{ width: '100%' }} playsInline muted />
      <canvas ref={canvasRef} style={{ display: 'none' }} />
    </div>
  );
};
"""

# Alias para facilitar la creación del componente
qr_scanner_component = JsQrScanner.create