import reflex as rx

class LocationButton(rx.Component):
    # ✅ Ruta explícita desde la raíz del paquete
    library = "likemodas/ui/location_button/LocationButton.js" 
    tag = "LocationButton"
    on_location_update: rx.EventHandler[lambda data: [data]]