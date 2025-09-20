import reflex as rx
from reflex.vars import Var

class QRScannerComponent(rx.Component):
    """
    Un componente de Reflex que envuelve la biblioteca 'html5-qrcode'
    para proporcionar un escáner de QR funcional.
    """
    tag = "Html5QrcodeScannerComponent"

    # Props que pasamos desde Python a la biblioteca JS
    fps: Var[int]
    qrbox: Var[int]
    verbose: Var[bool]

    # El manejador de eventos que envía los datos escaneados de vuelta a Python
    on_scan_success: rx.EventHandler[lambda decoded_text: [decoded_text]]

    def _get_custom_code(self) -> str:
        """
        Genera el código JS/React necesario para inicializar el escáner.
        Esta es la versión corregida que soluciona la condición de carrera
        y restaura la funcionalidad de subir archivos de imagen.
        """
        return """
import { Html5QrcodeScanner } from 'html5-qrcode';
import React, { useEffect } from 'react';

const Html5QrcodeScannerComponent = (props) => {
  const qrcodeRegionId = "html5qr-code-full-region";

  useEffect(() => {
    const config = {
      fps: props.fps || 10,
      qrbox: { width: 250, height: 250 },
      rememberLastUsedCamera: true,
    };

    const html5QrcodeScanner = new Html5QrcodeScanner(
      qrcodeRegionId,
      config,
      props.verbose || false
    );

    const successCallback = (decodedText, decodedResult) => {
      if (props.on_scan_success) {
        // 1. Enviar el dato a Python.
        props.on_scan_success(decodedText);
        // 2. Limpiar el escáner DESPUÉS de enviar el dato.
        // Esto da tiempo suficiente al WebSocket de Reflex para procesar el evento.
        html5QrcodeScanner.clear().catch(error => {
          console.error("Fallo al limpiar el escáner tras el éxito.", error);
        });
      }
    };

    const errorCallback = (errorMessage) => {
      // No hacer nada en caso de error para que el escáner siga activo.
    };

    html5QrcodeScanner.render(successCallback, errorCallback);

    // Función de limpieza que se ejecuta cuando el componente se desmonta (cierra)
    return () => {
      if (html5QrcodeScanner && html5QrcodeScanner.getState() !== 2) { // 2 = NOT_STARTED
          html5QrcodeScanner.clear().catch(error => {
            console.error("Fallo al limpiar el escáner al cerrar.", error);
          });
      }
    };
  }, []); // El array vacío asegura que useEffect se ejecute solo una vez

  return <div id={qrcodeRegionId} style={{ width: '100%' }} />;
};

export default Html5QrcodeScannerComponent;
"""

# Alias para facilitar la creación del componente en otras partes de tu app.
qr_scanner_component = QRScannerComponent.create