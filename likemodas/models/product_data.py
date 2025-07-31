import reflex as rx
from ..utils.formatting import format_to_cop

class ProductCardData(rx.Base):
    """Un modelo de datos simple para mostrar información de productos en la UI."""
    id: int
    title: str
    price: float = 0.0
    image_urls: list[str] = []
    average_rating: float = 0.0
    rating_count: int = 0

    @property
    def price_cop(self) -> str:
        """Propiedad para el precio ya formateado en COP."""
        return format_to_cop(self.price)
