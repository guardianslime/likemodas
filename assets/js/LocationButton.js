import React from 'react';
import { Button } from '@radix-ui/themes';
import { TargetIcon } from '@radix-ui/react-icons';

export const LocationButton = (props) => {
  const handleClick = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          if (props.on_location_update) {
            props.on_location_update({
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
            });
          }
        },
        (error) => {
          if (props.on_location_update) {
            props.on_location_update({ error: error.message });
          }
        }
      );
    } else {
      if (props.on_location_update) {
        props.on_location_update({ error: "Geolocation not supported." });
      }
    }
  };

  return (
    <Button onClick={handleClick} variant="outline" width="100%">
      <TargetIcon /> Añadir mi ubicación con mapa
    </Button>
  );
};