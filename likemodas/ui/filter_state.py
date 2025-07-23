# likemodas/ui/filter_state.py

import reflex as rx

class FilterState(rx.State):
    """Gestiona el estado del panel de filtros flotante."""
    min_price: str = ""
    max_price: str = ""
    show_filters: bool = False

    def toggle_filters(self):
        """Muestra u oculta el panel de filtros."""
        self.show_filters = not self.show_filters

    def set_min_price(self, price: str):
        """Actualiza el valor del precio mínimo."""
        self.min_price = price.strip()

    def set_max_price(self, price: str):
        """Actualiza el valor del precio máximo."""
        self.max_price = price.strip()

