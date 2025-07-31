import reflex as rx
from typing import List
# Se elimina la importación de BlogPostModel de la parte superior.
# from ..models import BlogPostModel 
from sqlmodel import select
from datetime import datetime
from ..cart.state import ProductCardData
from sqlalchemy.orm import joinedload

class SearchState(rx.State):
    """El único y definitivo estado para la búsqueda."""
    search_term: str = ""
    search_results: List[ProductCardData] = []
    search_performed: bool = False

    @rx.event
    def perform_search(self):
        """Ejecuta la búsqueda, transforma los datos y redirige."""
        # --- CAMBIO CLAVE ---
        # Se importa BlogPostModel DENTRO de la función.
        # Esto rompe el ciclo de importación, ya que el modelo solo se carga
        # cuando la búsqueda se ejecuta, no durante el inicio de la app.
        from ..models import BlogPostModel

        term = self.search_term.strip()
        if not term:
            return

        with rx.session() as session:
            statement = (
                select(BlogPostModel)
                .options(joinedload(BlogPostModel.comments))
                .where(
                    BlogPostModel.publish_active == True,
                    BlogPostModel.publish_date < datetime.now(),
                    BlogPostModel.title.ilike(f"%{term}%")
                )
                .order_by(BlogPostModel.created_at.desc())
            )
            results = session.exec(statement).unique().all()
            self.search_results = [
                ProductCardData(
                    id=post.id,
                    title=post.title,
                    price=post.price,
                    image_urls=post.image_urls,
                    average_rating=post.average_rating,
                    rating_count=post.rating_count
                )
                for post in results
            ]

        self.search_performed = True 
        return rx.redirect("/search-results")
