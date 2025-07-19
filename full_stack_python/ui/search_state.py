# full_stack_python/ui/search_state.py

import reflex as rx
from typing import List
from ..models import BlogPostModel
from sqlmodel import select
from datetime import datetime

class SearchState(rx.State):
    search_term: str = ""
    search_results: List[BlogPostModel] = []
    search_performed: bool = False

    # Este es el setter por defecto, lo usaremos en el on_change del input
    def set_search_term(self, value: str):
        self.search_term = value
        if not self.search_term.strip():
            self.search_performed = False
            self.search_results = []

    @rx.event  # <--- ESTE DECORADOR ES LA CLAVE
    def perform_search(self, form_data: dict):
        """
        Ejecuta la búsqueda desde el formulario y redirige.
        """
        term = form_data.get("search_input", "").strip()
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
        self.search_term = term  # Actualizamos el estado para mostrarlo en la página de resultados
        return rx.redirect("/search-results")