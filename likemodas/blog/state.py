# likemodas/blog/state.py (COMPLETO Y CORREGIDO)

import reflex as rx
from sqlmodel import select
from ..models import BlogPostModel
from ..state import AppState

class BlogAdminState(AppState):
    """
    Estado para la página de administración de publicaciones.
    """

    # --- MODIFICACIÓN CLAVE: AÑADIR LA VARIABLE DEL FORMULARIO ---
    # Esta variable almacenará los datos del formulario de "Crear Publicación"
    # para que la previsualización funcione.
    post_form_data: dict = {
        "title": "",
        "content": "",
        "main_image": "",
        # Añade aquí otros campos si tu formulario los tiene
    }
    # --- FIN DE LA MODIFICACIÓN ---

    @rx.var
    def my_blog_posts(self) -> list[BlogPostModel]:
        """
        Devuelve solo las publicaciones del usuario actual.
        """
        if not self.user_info:
            return []
        
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
        if not self.user_info:
            return

        with rx.session() as session:
            post_to_delete = session.get(BlogPostModel, post_id)
            
            if post_to_delete and post_to_delete.userinfo_id == self.user_info.id:
                session.delete(post_to_delete)
                session.commit()