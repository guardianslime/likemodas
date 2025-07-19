# full_stack_python/ui/search_state.py

import reflex as rx
from typing import List
from ..models import BlogPostModel
from sqlmodel import select
from datetime import datetime

class SearchState(rx.State):
    """El único y definitivo estado para la búsqueda."""
    search_term: str = ""
    search_results: List[BlogPostModel] = []
    search_performed: bool = False

    @rx.event
    def perform_search(self):
        """
        Ejecuta la búsqueda usando el valor actual de search_term y redirige.
        """
        term = self.search_term.strip()
        if not term:
            return rx.toast.error("Por favor, introduce un término de búsqueda.")

        with rx.session() as session:
            statement = (
                select(BlogPostModel)
                .where(
                    BlogPostModel.publish_active == True,
                    BlogPostModel.publish_date < datetime.now(),
                    BlogPostModel.title.ilike(f"%{term}%")
                )
                .order_by(BlogPostModel.created_at.desc())
            )
            self.search_results = session.exec(statement).all()

        self.search_performed = True
        return rx.redirect("/search-results")