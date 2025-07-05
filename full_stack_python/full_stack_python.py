import reflex as rx
import os

class State(rx.State):
    uploaded_files: list[str] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializar la lista con los archivos ya guardados en el volumen
        upload_dir = rx.get_upload_dir()
        if upload_dir.exists():
            self.uploaded_files = [
                f.name for f in upload_dir.iterdir() if f.is_file()
            ]

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        for file in files:
            data = await file.read()
            path = rx.get_upload_dir() / file.name
            with path.open("wb") as f:
                f.write(data)
            if file.name not in self.uploaded_files:
                self.uploaded_files.append(file.name)

def index():
    return rx.vstack(
        rx.upload(
            rx.text("Arrastra imágenes aquí o haz clic para seleccionarlas"),
            id="image_upload",
            accept={
                "image/png": [".png"],
                "image/jpeg": [".jpg", ".jpeg"],
                "image/gif": [".gif"],
                "image/webp": [".webp"],
            },
            max_files=10,
            multiple=True,
            border="2px dashed #60a5fa",
            padding="2em",
        ),
        rx.button(
            "Subir imagen",
            on_click=State.handle_upload(rx.upload_files(upload_id="image_upload")),
        ),
        rx.foreach(
            State.uploaded_files,
            lambda filename: rx.image(src=rx.get_upload_url(filename), width="300px"),
        ),
        padding="2em"
    )

<<<<<<< HEAD
app = rx.App()
app.add_page(index, route="/")
=======
app = rx.App(
    theme=rx.theme(
        appearance="dark", 
        has_background=True, 
        panel_background="solid",
        scaling="90%",
        radius="medium",
        accent_color="sky"
    )
)

# --- Registro de Páginas ---

app.add_page(index, on_load=ArticlePublicState.load_posts)
app.add_page(my_login_page, route=reflex_local_auth.routes.LOGIN_ROUTE)
app.add_page(my_register_page, route=reflex_local_auth.routes.REGISTER_ROUTE)
app.add_page(my_logout_page, route=navigation.routes.LOGOUT_ROUTE)
app.add_page(pages.about_page, route=navigation.routes.ABOUT_US_ROUTE)
app.add_page(pages.protected_page, route="/protected/", on_load=SessionState.on_load)
app.add_page(pages.pricing_page, route=navigation.routes.PRICING_ROUTE)

# Páginas de Artículos
app.add_page(
    article_public_list_page,
    route=navigation.routes.ARTICLE_LIST_ROUTE,
    on_load=ArticlePublicState.load_posts,
)
app.add_page(
    article_detail_page,
    route=f"{navigation.routes.ARTICLE_LIST_ROUTE}/[article_id]",
    on_load=ArticlePublicState.get_post_detail,
)

# Páginas de Blog
app.add_page(
    blog.blog_post_list_page,
    route=navigation.routes.BLOG_POSTS_ROUTE,
    on_load=blog.BlogPostState.load_posts
)
app.add_page(blog.blog_post_add_page, route=navigation.routes.BLOG_POST_ADD_ROUTE)
app.add_page(
    blog.blog_post_detail_page,
    route="/blog/[blog_id]",
    on_load=blog.BlogPostState.get_post_detail
)
app.add_page(
    blog.blog_post_edit_page,
    route="/blog/[blog_id]/edit",
    on_load=blog.BlogPostState.get_post_detail
)

# --- INICIO DE LA CORRECCIÓN ---
# Páginas de Contacto
app.add_page(contact.contact_page, route=navigation.routes.CONTACT_US_ROUTE)
app.add_page(
    contact.contact_entries_list_page,
    route=navigation.routes.CONTACT_ENTRIES_ROUTE,
    on_load=contact.ContactState.load_entries
)
# --- FIN DE LA CORRECCIÓN ---
>>>>>>> beb53a0e4ed77ef43ba9c6e06e281de46a7ae37f
