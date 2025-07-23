# likemodas/ui/search_state.py (VERSIÓN FINAL Y CORREGIDA)

import reflex as rx
from typing import List
from ..models import BlogPostModel
from sqlmodel import select
from datetime import datetime
from .. import navigation
from sqlalchemy.orm import joinedload
from ..states.gallery_state import ProductGalleryState

# --- CAMBIO 1: Importamos el modelo de datos seguro ---
from ..cart.state import ProductCardData

class SearchState(ProductGalleryState):
    """El único y definitivo estado para la búsqueda."""
    search_term: str = ""
    
    # --- CAMBIO 2: Los resultados ahora serán del tipo seguro ---
    search_results: List[ProductCardData] = []
    search_performed: bool = False

    @rx.event
    def perform_search(self):
        """Ejecuta la búsqueda y puebla la lista de posts para ser filtrada."""
        term = self.search_term.strip()
        if not term:
            self.all_posts = []
            return rx.redirect(navigation.routes.BLOG_PUBLIC_PAGE_ROUTE) 

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
            
            # --- PASO 2: Guarda los resultados en 'all_posts' para los filtros ---
            self.all_posts = [
                ProductCardData(
                    id=post.id, title=post.title, price=post.price,
                    images=post.images, average_rating=post.average_rating,
                    rating_count=post.rating_count
                ) for post in results
            ]

        return rx.redirect("/search-results")