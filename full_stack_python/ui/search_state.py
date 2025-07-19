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
        if not self.search_term.strip():
            self.search_performed = False
            self.search_results = []

    @rx.event  # <--- AÑADE ESTE DECORADOR
    def perform_search(self, form_data: dict): # Acepta form_data del on_submit
        """
        Ejecuta la búsqueda en la base de datos y redirige a la página de resultados.
        """
        # Extraemos el valor del input del diccionario del formulario
        self.search_term = form_data.get("search_input", "").strip()

        if not self.search_term:
            return rx.toast.error("Por favor, introduce un término de búsqueda.")

        with rx.session() as session:
            statement = (
                select(BlogPostModel)
                .where(
                    BlogPostModel.publish_active == True,
                    BlogPostModel.publish_date < datetime.now(),
                    BlogPostModel.title.ilike(f"%{self.search_term}%")
                )
                .order_by(BlogPostModel.created_at.desc())
            )
            self.search_results = session.exec(statement).all()
        
        self.search_performed = True
        return rx.redirect("/search-results")