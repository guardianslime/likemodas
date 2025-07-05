from datetime import datetime
from typing import Optional, List
import reflex as rx
import sqlalchemy
from sqlmodel import select
from .. import navigation
from ..auth.state import SessionState
from ..models import BlogPostModel, UserInfo, PostImageModel
import os

class BlogPostState(SessionState):
    post: Optional[BlogPostModel] = None
    posts: List[BlogPostModel] = []
    
    post_content: str = ""
    post_publish_active: bool = False
    uploaded_images: list[str] = []
    publish_date_str: str = ""
    publish_time_str: str = ""

    @rx.var
    def preview_image_urls(self) -> list[str]:
        urls = []
        if self.post and self.post.images:
            for img in self.post.images:
                urls.append(f"/_upload/{img.filename}")
        for filename in self.uploaded_images:
            if f"/_upload/{filename}" not in urls:
                urls.append(f"/_upload/{filename}")
        return urls

    @rx.var
    def blog_post_id(self) -> int:
        try:
            return int(self.router.page.params.get("blog_id", 0))
        except:
            return 0

    async def handle_upload(self, files: list[rx.UploadFile]):
        for file in files:
            data = await file.read()
            path = rx.get_upload_dir() / file.name
            with path.open("wb") as f: f.write(data)
            if file.name not in self.uploaded_images:
                self.uploaded_images.append(file.name)

    def delete_preview_image(self, url: str):
        filename_to_delete = os.path.basename(url)
        self.uploaded_images = [f for f in self.uploaded_images if f != filename_to_delete]
        if self.post:
            with rx.session() as session:
                img_to_delete = session.exec(
                    select(PostImageModel).where(
                        PostImageModel.blog_post_id == self.post.id,
                        PostImageModel.filename == filename_to_delete
                    )
                ).one_or_none()
                if img_to_delete:
                    session.delete(img_to_delete)
                    session.commit()
            return self.get_post_detail

    def get_post_detail(self):
        self.uploaded_images = []
        if not self.blog_post_id: self.post = None; return
        with rx.session() as session:
            self.post = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.selectinload(BlogPostModel.images)
                ).where(BlogPostModel.id == self.blog_post_id)
            ).one_or_none()
        if self.post:
            self.post_content = self.post.content
            self.post_publish_active = self.post.publish_active
            if self.post.publish_date:
                self.publish_date_str = self.post.publish_date.strftime("%Y-%m-%d")
                self.publish_time_str = self.post.publish_date.strftime("%H:%M:%S")
            else:
                self.publish_date_str = ""; self.publish_time_str = ""
        else:
            return rx.redirect("/blog")

    def load_posts(self):
        with rx.session() as session:
            self.posts = session.exec(
                select(BlogPostModel).options(
                    sqlalchemy.orm.selectinload(BlogPostModel.images)
                ).where(BlogPostModel.userinfo_id == self.my_userinfo_id).order_by(BlogPostModel.id.desc())
            ).all()

    def handle_submit(self, form_data: dict):
        post_id = self.blog_post_id if self.blog_post_id > 0 else None
        
        with rx.session() as session:
            db_post = session.get(BlogPostModel, post_id) if post_id else BlogPostModel(userinfo_id=self.my_userinfo_id)
            db_post.title = form_data.get("title"); db_post.content = self.post_content
            db_post.publish_active = self.post_publish_active
            
            if self.publish_date_str and self.publish_time_str:
                try:
                    db_post.publish_date = datetime.strptime(f"{self.publish_date_str} {self.publish_time_str}", "%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    db_post.publish_date = None
            else:
                db_post.publish_date = None
            
            session.add(db_post); session.commit(); session.refresh(db_post)
            post_id = db_post.id

            # Sincronizar imágenes nuevas
            if self.uploaded_images:
                existing_filenames = {img.filename for img in db_post.images}
                for filename in self.uploaded_images:
                    if filename not in existing_filenames:
                        session.add(PostImageModel(filename=filename, blog_post_id=post_id))
                session.commit()

        # Recargar la página de edición para mostrar el estado final
        return rx.redirect(f"/blog/{post_id}/edit")