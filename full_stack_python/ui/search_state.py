# full_stack_python/ui/search_state.py

import reflex as rx
from typing import List
from ..models import BlogPostModel # Importamos el modelo de las publicaciones
from sqlmodel import select
from datetime import datetime

class SearchState(rx.State):
    search_term: str = ""
    # Variable para guardar los resultados de la búsqueda
    search_results: List[BlogPostModel] = []
    # Variable para saber si ya se realizó una búsqueda
    search_performed: bool = False

    def update_search(self, value: str):
        self.search_term = value
        # Si el usuario borra el campo, reseteamos el estado
        if not self.search_term.strip():
            self.search_performed = False
            self.search_results = []

    @rx.event
    def perform_search(self):
        """
        Ejecuta la búsqueda en la base de datos y redirige a la página de resultados.
        """
        if not self.search_term.strip():
            # No buscar si el campo está vacío
            return rx.toast.error("Por favor, introduce un término de búsqueda.")

        with rx.session() as session:
            # Construimos la consulta
            statement = (
                select(BlogPostModel)
                .where(
                    # Buscamos solo en publicaciones activas
                    BlogPostModel.publish_active == True,
                    BlogPostModel.publish_date < datetime.now(),
                    # Usamos ilike para una búsqueda case-insensitive que contenga el término
                    BlogPostModel.title.ilike(f"%{self.search_term}%")
                )
                .order_by(BlogPostModel.created_at.desc())
            )
            self.search_results = session.exec(statement).all()
        
        self.search_performed = True
        # Redirigimos a la nueva página de resultados
        return rx.redirect("/search-results")