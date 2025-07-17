import reflex as rx
import sqlalchemy
from sqlmodel import select
from datetime import datetime
from typing import Optional
import os
import pathlib

from .. import navigation
from ..auth.state import SessionState
from ..models import BlogPostModel, UserInfo

BLOG_POSTS_ROUTE = navigation.routes.BLOG_POSTS_ROUTE.rstrip("/")

# ... (Las clases BlogPostState y BlogPublicState no necesitan cambios) ...
class BlogPostState(SessionState):
    posts: list[BlogPostModel] = []
    post: Optional[BlogPostModel] = None

    @rx.var
    def formatted_price(self) -> str:
        if self.post and self.post.price is not None:
            return f"${self.post.price:,.2f}"
        return "$0.00"

    @rx.var
    def post_image_urls(self) -> list[str]:
        if self.post and self.post.images:
            return [rx.get_upload_url(img) for img in self.post.images]
        return ["/no_image.png"]

    @rx.event
    def delete_post(self, post_id: int):
        if self.my_userinfo_id is None:
            return rx.window_alert("No estás autenticado.")
        with rx.session() as session:
            post_to_delete = session.get(BlogPostModel, post_id)
            if post_to_delete and post_to_delete.userinfo_id == int(self.my_userinfo_id):
                if post_to_delete.images:
                    upload_dir = rx.get_upload_dir()
                    for image_name in post_to_delete.images:
                        try:
                            file_path = pathlib.Path(upload_dir) / image_name
                            if file_path.is_file():
                                os.remove(file_path)
                        except Exception as e:
                            print(f"Error al eliminar el archivo {image_name}: {e}")
                session.delete(post_to_delete)
                session.commit()
                return rx.redirect(BLOG_POSTS_ROUTE)
            else:
                return rx.window_alert("No tienes permiso para eliminar esta publicación.")

    def handle_delete_confirm(self):
        if self.post:
            return self.delete_post(self.post.id)

    @rx.event
    def load_posts(self):
        if self.my_userinfo_id is None:
            self.posts = []
            return
        with rx.session() as session:
            self.posts = session.exec(
                select(BlogPostModel).options(sqlalchemy.orm.joinedload(BlogPostModel.userinfo)).where(BlogPostModel.userinfo_id == int(self.my_userinfo_id)).order_by(BlogPostModel.created_at.desc())
            ).all()

    @rx.var
    def blog_post_id(self) -> str:
        return self.router.page.params.get("blog_id", "")

    @rx.var
    def blog_post_edit_url(self) -> str:
        if self.post and self.post.id is not None:
            return f"{BLOG_POSTS_ROUTE}/{self.post.id}/edit"
        return BLOG_POSTS_ROUTE

    def get_post_detail(self):
        if self.my_userinfo_id is None:
            self.post = None
            return
        try:
            post_id_int = int(self.blog_post_id)
        except (ValueError, TypeError):
            self.post = None
            return
        with rx.session() as session:
            self.post = session.exec(
                select(BlogPostModel).options(sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user)).where((BlogPostModel.userinfo_id == int(self.my_userinfo_id)) & (BlogPostModel.id == post_id_int))
            ).one_or_none()

class BlogPublicState(SessionState):
    posts: list[BlogPostModel] = []
    def on_load(self):
        with rx.session() as session:
            self.posts = session.exec(select(BlogPostModel).where(BlogPostModel.publish_active == True).order_by(BlogPostModel.created_at.desc())).all()

class BlogAddFormState(SessionState):
    title: str = ""
    content: str = ""
    price: str = ""
    temp_images: list[str] = []
    async def handle_upload(self, files: list[rx.UploadFile]):
        for file in files:
            data = await file.read()
            path = rx.get_upload_dir() / file.name
            with path.open("wb") as f: f.write(data)
            if file.name not in self.temp_images:
                self.temp_images.append(file.name)
    def remove_image(self, name: str):
        if name in self.temp_images:
            self.temp_images.remove(name)
    def set_price(self, value: str): self.price = value
    def submit(self):
        if self.my_userinfo_id is None: return rx.window_alert("Inicia sesión.")
        try: parsed_price = float(self.price)
        except (ValueError, TypeError): return rx.window_alert("Precio inválido.")
        with rx.session() as session:
            post = BlogPostModel(
                title=self.title.strip(), content=self.content.strip(), price=parsed_price,
                images=self.temp_images.copy(), userinfo_id=int(self.my_userinfo_id),
                publish_active=True, publish_date=datetime.now()
            )
            session.add(post)
            session.commit()
        return rx.redirect("/blog")
    def set_price_from_input(self, value: str):
        try: self.price = float(value)
        except ValueError: self.price = 0.0

# --- ✨ CORRECCIONES PRINCIPALES EN ESTA CLASE ✨ ---
class BlogEditFormState(BlogPostState):
    # Variables de estado separadas para cada campo del formulario
    form_title: str = ""
    form_content: str = ""
    form_price_str: str = "0.0"
    form_publish_active: bool = False
    form_publish_date_str: str = ""
    form_publish_time_str: str = ""

    def on_load_edit(self):
        """Carga los datos del post y los prepara para el formulario."""
        self.get_post_detail()
        if self.post:
            # Llena las variables del formulario con los datos del post cargado
            self.form_title = self.post.title or ""
            self.form_content = self.post.content or ""
            self.form_price_str = str(self.post.price or "0.0")
            self.form_publish_active = self.post.publish_active
            
            if self.post.publish_date:
                self.form_publish_date_str = self.post.publish_date.strftime("%Y-%m-%d")
                self.form_publish_time_str = self.post.publish_date.strftime("%H:%M:%S")
            else:
                now = datetime.now()
                self.form_publish_date_str = now.strftime("%Y-%m-%d")
                self.form_publish_time_str = now.strftime("%H:%M:%S")

    # Setters para que los componentes del formulario sean "controlados"
    def set_form_title(self, value: str): self.form_title = value
    def set_form_content(self, value: str): self.form_content = value
    def set_form_price_str(self, value: str): self.form_price_str = value
    def set_form_publish_active(self, value: bool): self.form_publish_active = value
    def set_form_publish_date_str(self, value: str): self.form_publish_date_str = value
    def set_form_publish_time_str(self, value: str): self.form_publish_time_str = value

    def handle_submit(self):
        """Maneja el envío del formulario usando las variables de estado."""
        if not self.post:
            return rx.window_alert("No se ha cargado ningún post para editar.")

        post_id = self.post.id
        final_publish_date = None
        
        if self.form_publish_active and self.form_publish_date_str and self.form_publish_time_str:
            try:
                dt_str = f"{self.form_publish_date_str} {self.form_publish_time_str}"
                final_publish_date = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            except ValueError: pass

        try:
            price_val = float(self.form_price_str)
        except ValueError:
            return rx.window_alert("Precio inválido.")
            
        with rx.session() as session:
            post_to_update = session.get(BlogPostModel, post_id)
            if post_to_update:
                post_to_update.title = self.form_title
                post_to_update.content = self.form_content
                post_to_update.price = price_val
                post_to_update.publish_active = self.form_publish_active
                post_to_update.publish_date = final_publish_date
                session.add(post_to_update)
                session.commit()
        
        return rx.redirect(self.blog_post_url)

class BlogViewState(SessionState):
    post: Optional[BlogPostModel] = None
    @rx.var
    def post_id(self) -> str:
        return self.router.page.params.get("blog_public_id", "")
    @rx.var
    def post_image_urls(self) -> list[str]:
        if self.post and self.post.images:
            return [rx.get_upload_url(img) for img in self.post.images]
        return ["/no_image.png"]
    @rx.var
    def formatted_price(self) -> str:
        if self.post and self.post.price is not None:
            return f"${self.post.price:,.2f}"
        return "$0.00"
    @rx.var
    def content(self) -> str:
        if self.post and self.post.content:
            return self.post.content
        return ""
    @rx.var
    def has_post(self) -> bool:
        return self.post is not None
    def on_load(self):
        try:
            pid = int(self.post_id)
        except (ValueError, TypeError):
            self.post = None
            return
        with rx.session() as session:
            self.post = session.get(BlogPostModel, pid)