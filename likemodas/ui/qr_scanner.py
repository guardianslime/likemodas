# likemodas/ui/qr_scanner.py
import reflex as rx
from reflex.vars import Var

class QRScannerComponent(rx.Component):
    """
    Un componente de Reflex que envuelve la biblioteca 'html5-qrcode'
    para proporcionar un escáner de QR funcional.
    """
    # El nombre del paquete en npm
    library = "html5-qrcode"
    
    # El nombre del componente que crearemos en el código JS personalizado.
    tag = "Html5QrcodeScannerComponent"

    # Props configurables que se pasan a la biblioteca JS
    fps: Var[int]
    qrbox: Var[int]
    verbose: Var[bool]

    # El manejador de eventos que servirá como puente hacia Python.
    # Recibe un string (el texto decodificado del QR).
    on_scan_success: rx.EventHandler[lambda decoded_text: [decoded_text]]

    def _get_custom_code(self) -> str:
        """
        Genera el código JS/React necesario para inicializar el escáner.
        """
        return """
import React, { useEffect } from 'react';
import { Html5QrcodeScanner } from 'html5-qrcode';

const Html5QrcodeScannerComponent = (props) => {
  const qrcodeRegionId = "html5qr-code-full-region";

  useEffect(() => {
    const html5QrcodeScanner = new Html5QrcodeScanner(
      qrcodeRegionId,
      {
        fps: props.fps || 10,
        qrbox: props.qrbox || 250,
      },
      props.verbose || false
    );

    const successCallback = (decodedText, decodedResult) => {
      // Llama al event handler de Reflex cuando el escaneo es exitoso
      if (props.on_scan_success) {
        props.on_scan_success(decodedText);
      }
    };

    const errorCallback = (errorMessage) => {
      // Se puede manejar el error si es necesario
    };

    html5QrcodeScanner.render(successCallback, errorCallback);

    // Función de limpieza para detener la cámara cuando el componente se desmonte
    return () => {
      html5QrcodeScanner.clear().catch(error => {
        console.error("Failed to clear html5QrcodeScanner.", error);
      });
    };
  }, []);

  return <div id={qrcodeRegionId} style={{ width: '100%' }} />;
};

export default Html5QrcodeScannerComponent;
"""

# Alias para facilitar la creación del componente
qr_scanner_component = QRScannerComponent.create