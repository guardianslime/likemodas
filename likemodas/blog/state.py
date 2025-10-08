# likemodas/blog/state.py (COMPLETO Y CORREGIDO)

import reflex as rx
from sqlmodel import select
from ..models import BlogPostModel
from ..state import AppState

class BlogAdminState(AppState):
    """
    Estado para la página de administración de publicaciones.
    """

    post_form_data: dict = {
        "title": "",
        "content": "",
        "price_str": "", # <--- AÑADE ESTA LÍNEA
    }

    def set_post_form_field(self, field: str, value: str):
        """
        Un manejador genérico para actualizar cualquier campo del
        formulario.
        """
        self.post_form_data[field] = value

    async def delete_post(self, post_id: int):
        """
        Manejador de evento para eliminar una publicación de forma segura.
        """
        if not hasattr(self, "user_info") or self.user_info is None:
            return

        with rx.session() as session:
            post_to_delete = session.get(BlogPostModel, post_id)
            
            if post_to_delete and post_to_delete.userinfo_id == self.user_info.id:
                session.delete(post_to_delete)
                session.commit()