# likemodas/blog/state.py

import reflex as rx
from sqlmodel import select
from ..models import BlogPostModel  # Importamos tu modelo BlogPostModel
from ..state import AppState         # Importamos tu estado principal

class BlogAdminState(AppState):
    """
    Estado para la página de administración de publicaciones ("Mis Publicaciones").
    Hereda de AppState para tener acceso al usuario logueado.
    """

    @rx.var
    def my_blog_posts(self) -> list[BlogPostModel]:
        """
        Una variable computada que devuelve solo las publicaciones del usuario actual.
        ¡Esta es la clave de la solución!
        """
        # Primero, nos aseguramos de que haya un user_info cargado.
        if not self.user_info:
            return []
        
        # Conectamos con la BD y filtramos los posts donde el 'userinfo_id'
        # coincide con el id del user_info del usuario en sesión.
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
            return  # No hacer nada si no hay usuario

        with rx.session() as session:
            # Obtenemos el post de la base de datos
            post_to_delete = session.get(BlogPostModel, post_id)
            
            # Verificación de seguridad: solo el dueño puede borrar su post
            if post_to_delete and post_to_delete.userinfo_id == self.user_info.id:
                session.delete(post_to_delete)
                session.commit()

        # Reflex detectará el cambio en la BD y `my_blog_posts` se recalculará,
        # actualizando la UI automáticamente.

