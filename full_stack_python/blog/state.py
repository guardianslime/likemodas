from datetime import datetime
from typing import Optional
import reflex as rx
import sqlalchemy
from sqlmodel import select

from .. import navigation
from ..auth.state import SessionState
from ..models import BlogPostModel, UserInfo

BLOG_POSTS_ROUTE = navigation.routes.BLOG_POSTS_ROUTE.rstrip("/")

# ───────────────────────────────
# Estado privado (mis publicaciones)
# ───────────────────────────────

class BlogPostState(SessionState):
    posts: list[BlogPostModel] = []
    post: Optional[BlogPostModel] = None
    img_idx: int = 0

    @rx.event
    def load_posts(self):
        if self.my_userinfo_id is None:
            self.posts = []
            return
        with rx.session() as session:
            self.posts = session.exec(
                select(BlogPostModel)
                .options(sqlalchemy.orm.joinedload(BlogPostModel.userinfo))
                .where(BlogPostModel.userinfo_id == self.my_userinfo_id)
                .order_by(BlogPostModel.created_at.desc())
            ).all()

    @rx.var
    def blog_post_id(self) -> str:
        return self.router.page.params.get("blog_id", "")

    @rx.var
    def blog_post_url(self) -> str:
        if self.post and self.post.id is not None:
            return f"{BLOG_POSTS_ROUTE}/{self.post.id}"
        return BLOG_POSTS_ROUTE

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
                select(BlogPostModel)
                .options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo)
                    .joinedload(UserInfo.user)
                )
                .where(
                    (BlogPostModel.userinfo_id == self.my_userinfo_id) &
                    (BlogPostModel.id == post_id_int)
                )
            ).one_or_none()

    def _add_post_to_db(self, form_data: dict):
        with rx.session() as session:
            post_data = form_data.copy()
            post_data["userinfo_id"] = self.my_userinfo_id
            post = BlogPostModel(**post_data)
            session.add(post)
            session.commit()
            session.refresh(post)
            self.post = post

    def _save_post_edits_to_db(self, post_id: int, updated_data: dict):
        with rx.session() as session:
            post = session.get(BlogPostModel, post_id)
            if post is None:
                return
            for key, value in updated_data.items():
                setattr(post, key, value)
            session.add(post)
            session.commit()
            session.refresh(post)
            self.post = post

# ───────────────────────────────
# Estado para vista pública
# ───────────────────────────────

class BlogPublicState(rx.State):
    posts: list[BlogPostModel] = []

    def on_load(self):
        with rx.session() as session:
            self.posts = session.exec(
                select(BlogPostModel)
                .where(BlogPostModel.publish_active == True)
                .order_by(BlogPostModel.created_at.desc())
            ).all()



# ───────────────────────────────
# Estado para añadir publicaciones
# ───────────────────────────────

class BlogAddFormState(SessionState):
    title: str = ""
    content: str = ""
    price: str = ""
    temp_images: list[str] = []

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        for file in files:
            data = await file.read()
            path = rx.get_upload_dir() / file.name
            with path.open("wb") as f:
                f.write(data)
            if file.name not in self.temp_images:
                self.temp_images.append(file.name)

    @rx.event
    def remove_image(self, name: str):
        if name in self.temp_images:
            self.temp_images.remove(name)

    @rx.event
    def set_price(self, value: str):
        self.price = value

    @rx.event
    def submit(self):
        if self.my_userinfo_id is None:
            return rx.window_alert("Inicia sesión.")

        try:
            parsed_price = float(self.price)
        except ValueError:
            return rx.window_alert("Precio inválido.")

        with rx.session() as session:
            post = BlogPostModel(
                title=self.title.strip(),
                content=self.content.strip(),
                price=parsed_price,
                images=self.temp_images.copy(),
                userinfo_id=self.my_userinfo_id,
                publish_active=True,
                publish_date=datetime.now()
            )
            session.add(post)
            session.commit()
            session.refresh(post)

        self.temp_images = []
        self.title = ""
        self.content = ""
        self.price = ""
        return rx.redirect("/blog/page")

    @rx.event
    def set_price_from_input(self, value: str):
        try:
            self.price = float(value)
        except ValueError:
            self.price = 0.0

class BlogEditFormState(BlogPostState):
    post_content: str = ""
    post_publish_active: bool = False

    def on_load_edit(self):
        self.get_post_detail()
        if self.post:
            self.post_content = self.post.content or ""
            self.post_publish_active = self.post.publish_active

    @rx.var
    def publish_display_date(self) -> str:
        if not self.post or not self.post.publish_date:
            return datetime.now().strftime("%Y-%m-%d")
        return self.post.publish_date.strftime("%Y-%m-%d")

    @rx.var
    def publish_display_time(self) -> str:
        if not self.post or not self.post.publish_date:
            return datetime.now().strftime("%H:%M:%S")
        return self.post.publish_date.strftime("%H:%M:%S")

    price_str: str = "0.0"

    @rx.event
    def set_price(self, value: str):
        self.price_str = value

    def handle_submit(self, form_data: dict):
        post_id = int(form_data.pop("post_id", 0))

        # Parsear fecha/hora
        final_publish_date = None
        if form_data.get("publish_date") and form_data.get("publish_time"):
            try:
                dt_str = f"{form_data['publish_date']} {form_data['publish_time']}"
                final_publish_date = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass

        # Validar precio
        try:
            form_data["price"] = float(self.price_str)
        except ValueError:
            return rx.window_alert("Precio inválido.")

        form_data["publish_active"] = form_data.get("publish_active") == "on"
        form_data["publish_date"] = final_publish_date
        form_data.pop("publish_time", None)

        self._save_post_edits_to_db(post_id, form_data)
        return rx.redirect(self.blog_post_url)

