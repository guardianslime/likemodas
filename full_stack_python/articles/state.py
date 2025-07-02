from datetime import datetime
from typing import Optional, List
import reflex as rx
import sqlalchemy
from sqlmodel import select

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

    # --- INICIO: CÓDIGO AÑADIDO ---
    async def handle_upload(self, files: list[rx.UploadFile]):
        """
        Maneja la subida de la imagen para el artículo actual.
        """
        # 1. Validar que hay un artículo seleccionado y un archivo para subir
        if not self.post or not files:
            return

        file = files[0]
        upload_data = await file.read()
        
        # 2. Crear un nombre de archivo único para evitar conflictos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outfile_path = f".web/public/{timestamp}_{file.filename}"

        # 3. Guardar el archivo en el directorio público del servidor
        with open(outfile_path, "wb") as f:
            f.write(upload_data)
        
        # 4. Crear la URL pública para acceder a la imagen
        image_url = f"/{timestamp}_{file.filename}"
        
        # 5. Actualizar la base de datos con la nueva URL
        with rx.session() as session:
            db_post = session.get(BlogPostModel, self.post.id)
            if db_post:
                db_post.image_url = image_url
                session.add(db_post)
                session.commit()
                session.refresh(db_post)
                # Actualizar el estado local para que la UI reaccione instantáneamente
                self.post = db_post
        
        # 6. Limpiar el componente de subida en el frontend
        return rx.clear_upload_files("upload_image")
    # --- FIN: CÓDIGO AÑADIDO ---

    # En full_stack_python/articles/state.py

    def get_post_detail(self):
        # --- INICIO DE LA MODIFICACIÓN ---
        try:
            # Intenta convertir el post_id de la URL a un número entero.
            post_id_num = int(self.post_id)
        except (ValueError, TypeError):
            # Si no es un número válido (ej. "detial"), no hagas nada.
            self.post = None
            return
        # --- FIN DE LA MODIFICACIÓN ---

        lookups = (
            (BlogPostModel.publish_active == True) &
            (BlogPostModel.publish_date < datetime.now()) &
            # Usa la variable numérica en la consulta
            (BlogPostModel.id == post_id_num)
        )
        with rx.session() as session:
            # El chequeo de self.post_id == "" ya no es tan necesario, pero lo mantenemos por si acaso
            if self.post_id == "":
                self.post = None
                return
            sql_statement = select(BlogPostModel).options(
                sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user)
            ).where(lookups)
            result = session.exec(sql_statement).one_or_none()
            self.post = result
            if result is None:
                self.post_content = ""
                return
            self.post_content = self.post.content
            self.post_publish_active = self.post.publish_active

    def set_limit_and_reload(self, new_limit: int = 5):
        self.limit = new_limit
        self.load_posts
        yield

    def load_posts(self, *args, **kwargs):
        lookup_args = (
            (BlogPostModel.publish_active == True) &
            (BlogPostModel.publish_date < datetime.now())
        )
        with rx.session() as session:
            result = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo)
                ).where(lookup_args).limit(self.limit)
            ).all()
            self.posts = result

    def to_post(self):
        if not self.post:
            return rx.redirect(ARTICLE_LIST_ROUTE)
        return rx.redirect(f"{self.post_url}")