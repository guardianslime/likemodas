# full_stack_python/blog/state.py

from datetime import datetime
from typing import Optional, List
import reflex as rx
import sqlalchemy
from sqlmodel import select
from .. import navigation
from ..auth.state import SessionState
from ..models import BlogPostModel, UserInfo
import asyncio
import reflex.moment as moment # <--- ¡AÑADE ESTA IMPORTACIÓN!

# ... (El resto del archivo hasta BlogEditFormState no cambia)
# ... (Las clases BlogPostState y BlogAddPostFormState no cambian)


class BlogEditFormState(BlogPostState):
    form_data: dict = {}

    @rx.var
    def publish_display_date(self) -> str:
        """Usa rx.moment para formatear la fecha de forma segura."""
        now_str = moment.Moment.now().format("YYYY-MM-DD")
        if not self.post:
            return now_str
        if not self.post.publish_date:
            return now_str
        # Convierte el datetime de Python a un Moment y lo formatea
        return moment.moment(self.post.publish_date).format("YYYY-MM-DD")

    @rx.var
    def publish_display_time(self) -> str:
        """Usa rx.moment para formatear la hora de forma segura."""
        now_str = moment.Moment.now().format("HH:mm:ss")
        if not self.post:
            return now_str
        if not self.post.publish_date:
            return now_str
        # Convierte el datetime de Python a un Moment y lo formatea
        return moment.moment(self.post.publish_date).format("HH:mm:ss")

    def handle_submit(self, form_data):
        self.form_data = form_data
        post_id = form_data.pop('post_id')
        publish_date_str = form_data.pop('publish_date', None)
        publish_time_str = form_data.pop('publish_time', None)
        
        final_publish_date = None
        if publish_date_str and publish_time_str:
            try:
                # El formato del input es 'YYYY-MM-DD' y 'HH:MM:SS'
                publish_input_string = f"{publish_date_str} {publish_time_str}"
                final_publish_date = datetime.strptime(publish_input_string, "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                final_publish_date = None

        publish_active = form_data.pop('publish_active', False) == "on"
        
        updated_data = {**form_data}
        if self.uploaded_image:
            updated_data['image_filename'] = self.uploaded_image
            
        updated_data['publish_active'] = publish_active
        updated_data['publish_date'] = final_publish_date
        self.save_post_edits(post_id, updated_data)
        return self.to_blog_post()