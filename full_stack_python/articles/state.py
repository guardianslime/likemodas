# state.py

from datetime import datetime
from typing import Optional, List
import reflex as rx
import sqlalchemy
from sqlmodel import select
import shutil # Importa shutil para mover archivos

from .. import navigation
from ..auth.state import SessionState
from ..models import BlogPostModel, UserInfo

ARTICLE_LIST_ROUTE = navigation.routes.ARTICLE_LIST_ROUTE
if ARTICLE_LIST_ROUTE.endswith("/"):
    ARTICLE_LIST_ROUTE = ARTICLE_LIST_ROUTE[:-1]

class ArticlePublicState(SessionState):
    posts: List["BlogPostModel"] = []
    post: Optional["BlogPostModel"] = None
    post_content: str = ""
    post_publish_active: bool = False
    limit: int = 20

    @rx.var
    def post_id(self) -> str:
        return self.router.page.params.get("article_id", "")

    @rx.var
    def post_url(self) -> str:
        if not self.post:
            return f"{ARTICLE_LIST_ROUTE}"
        return f"{ARTICLE_LIST_ROUTE}/{self.post.id}"

    # --- INICIO DE CAMBIOS ---

    # 1. Handler para la subida de la imagen
async def handle_upload(self, files: list[rx.UploadFile]):
    """Maneja la subida de la imagen del post."""
    if not self.post or not files:
        return

    file = files[0]
    upload_data = await file.read()
    # Asegura un nombre de archivo único para evitar sobreescrituras
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outfile_path = f".web/public/{timestamp}_{file.filename}"
    
    # Guardar el archivo en el directorio público
    with open(outfile_path, "wb") as f:
        f.write(upload_data)
    
    # La URL pública no incluye ".web/public"
    image_url = f"/{timestamp}_{file.filename}"
    
    # Actualizar la URL de la imagen en la base de datos
    with rx.session() as session:
        # Volvemos a cargar el post desde la BD para asegurarnos de que trabajamos con el objeto correcto
        db_post = session.get(BlogPostModel, self.post.id)
        if db_post:
            db_post.image_url = image_url
            session.add(db_post)
            session.commit()
            session.refresh(db_post)
            # Actualizar el estado local para que la UI reaccione
            self.post = db_post
    
    # Limpia los archivos del componente de subida para permitir subir otro
            return rx.clear_upload_files("upload_image")

