# likemodas/blog/state.py (COMPLETO Y CORREGIDO)

import reflex as rx
from sqlmodel import select
from ..models import BlogPostModel
from ..state import AppState

class BlogAdminState(AppState):
    """
    Estado para la página de administración de publicaciones.
    """

    # Variable para el formulario de "Crear Publicación", necesaria para la previsualización.
    post_form_data: dict = {
        "title": "",
        "content": "",
        "main_image": "",
    }

    @rx.var
    def my_blog_posts(self) -> list[BlogPostModel]:
        """
        Una variable computada que devuelve solo las publicaciones del usuario actual.
        Ahora maneja de forma segura el caso en que no hay un usuario logueado.
        """
        # --- MODIFICACIÓN CLAVE Y FINAL ---
        # Ahora verificamos no solo si el usuario está autenticado,
        # sino también que la información del usuario (user_info) ya se haya cargado.
        if not self.is_authenticated or self.user_info is None:
            return []
        # --- FIN DE LA MODIFICACIÓN ---
        
        # Si ambas condiciones son verdaderas, podemos acceder a self.user_info de forma segura.
        with rx.session() as session:
            posts = session.exec(
                select(BlogPostModel)
                .where(BlogPostModel.userinfo_id == self.user_info.id)
                .order_by(BlogPostModel.created_at.desc())
            ).all()
            return posts

    async def delete_post(self, post_id: int):
        """
        Manejador de evento para eliminar una publicación de forma segura.
        """
        # Usamos la misma lógica segura aquí.
        if not self.is_authenticated or self.user_info is None:
            return

        with rx.session() as session:
            post_to_delete = session.get(BlogPostModel, post_id)
            
            if post_to_delete and post_to_delete.userinfo_id == self.user_info.id:
                session.delete(post_to_delete)
                session.commit()