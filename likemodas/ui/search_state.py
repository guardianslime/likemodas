# likemodas/ui/search_state.py (VERSIÓN CORREGIDA)

import reflex as rx
from typing import List
from ..models import BlogPostModel
from sqlmodel import select
from datetime import datetime
from .. import navigation
from sqlalchemy.orm import joinedload # <<< 1. AÑADE ESTA IMPORTACIÓN

class SearchState(rx.State):
    """El único y definitivo estado para la búsqueda."""
    search_term: str = ""
    search_results: List[BlogPostModel] = []
    search_performed: bool = False

    @rx.event
    def perform_search(self):
        """Ejecuta la búsqueda y redirige."""
        term = self.search_term.strip()
        if not term:
            return rx.redirect(navigation.routes.BLOG_PUBLIC_PAGE_ROUTE) 

        with rx.session() as session:
            statement = (
                select(BlogPostModel)
                # <<< 2. AÑADE ESTA LÍNEA >>>
                .options(joinedload(BlogPostModel.comments))
                .where(
                    BlogPostModel.publish_active == True,
                    BlogPostModel.publish_date < datetime.now(),
                    BlogPostModel.title.ilike(f"%{term}%")
                )
                .order_by(BlogPostModel.created_at.desc())
            )
            self.search_results = session.exec(statement).unique().all()

        self.search_performed = True 
        return rx.redirect("/search-results") 