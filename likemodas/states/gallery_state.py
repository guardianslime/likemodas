# likemodas/states/gallery_state.py

import reflex as rx
from ..auth.state import SessionState
from ..data.schemas import ProductCardData

class ProductGalleryState(SessionState):
    """Un estado base para galerías de productos que incluye filtros."""

    # La lista completa de productos para la vista actual (sin filtrar)
    all_posts: list[ProductCardData] = []

    # Variables para controlar el sidebar de filtros
    show_filters: bool = False

    # Variables para los valores de los filtros
    min_price: str = ""
    max_price: str = ""

    @rx.event
    def toggle_filters(self):
        """Muestra u oculta la barra lateral de filtros."""
        self.show_filters = not self.show_filters

    @rx.var
    def filtered_posts(self) -> list[ProductCardData]:
        """
        Una propiedad computada que devuelve la lista de productos
        filtrada por precio.
        """
        posts = self.all_posts
        
        # Filtrar por precio mínimo
        if self.min_price.strip().isdigit():
            min_val = float(self.min_price)
            posts = [p for p in posts if p.price >= min_val]

        # Filtrar por precio máximo
        if self.max_price.strip().isdigit():
            max_val = float(self.max_price)
            posts = [p for p in posts if p.price <= max_val]
            
        return posts