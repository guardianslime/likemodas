# likemodas/ui/search_state.py (VERSIÓN FINAL Y CORREGIDA)

import reflex as rx
from typing import List
from ..models import BlogPostModel
from sqlmodel import select
from datetime import datetime
from .. import navigation
from sqlalchemy.orm import joinedload

# --- CAMBIO 1: Importamos el modelo de datos seguro ---
from ..cart.state import ProductCardData

class SearchState(rx.State):
    """El único y definitivo estado para la búsqueda."""
    search_term: str = ""
    
    # --- CAMBIO 2: Los resultados ahora serán del tipo seguro ---
    search_results: List[ProductCardData] = []
    
    search_performed: bool = False

    @rx.event
    def perform_search(self):
        """Ejecuta la búsqueda, transforma los datos y redirige."""
        term = self.search_term.strip()
        
        # --- ✨ CAMBIO CLAVE ---
        # Si la búsqueda está vacía, simplemente no hacemos nada.
        if not term:
            return
        # --- FIN DEL CAMBIO ---

        with rx.session() as session:
            # ... (el resto de la función sigue igual)
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