// assets/js/LocationButton.js
import React from 'react';
import { Button } from '@radix-ui/themes';
import { TargetIcon } from '@radix-ui/react-icons'

export const LocationButton = (props) => {
  const handleClick = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        // --- Función si el usuario acepta ---
        (position) => {
          // Llama al manejador de eventos de Python con las coordenadas
          if (props.on_location_update) {
            props.on_location_update({
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
            });
          }
        },
        // --- Función si el usuario niega o hay un error ---
        (error) => {
          if (props.on_location_update) {
            props.on_location_update({ error: error.message });
          }
        }
      );
    } else {
      // El navegador no soporta geolocalización
      if (props.on_location_update) {
        props.on_location_update({ error: "La geolocalización no es soportada." });
      }
    }
  };

  return (
    <Button onClick={handleClick} size="3" variant="soft">
      <TargetIcon /> Usar mi Ubicación Actual
    </Button>
  );
};