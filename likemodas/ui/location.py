# likemodas/ui/location.py
import reflex as rx

class LocationButton(rx.Component):
    library = "/js/LocationButton.js"
    tag = "LocationButton"
    on_location_update: rx.EventHandler[lambda data: [data]]