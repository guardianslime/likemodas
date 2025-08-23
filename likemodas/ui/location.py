# likemodas/ui/location.py
import reflex as rx

class LocationButton(rx.Component):
    library = "./LocationButton.js" # ✅ Ruta correcta y relativa
    tag = "LocationButton"
    on_location_update: rx.EventHandler[lambda data: [data]]