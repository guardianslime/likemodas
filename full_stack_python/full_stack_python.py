# full_stack_python/full_stack_python.py

import reflex as rx
import reflex_local_auth
from rxconfig import config

# --- CORRECCIÓN: Importar paquetes completos para evitar errores de importación ---
from . import articles, auth, blog, contact, navigation, pages, ui

def index() -> rx.Component:
    """La página principal que redirige al dashboard si el usuario está autenticado."""
    # Se usan las referencias completas desde los paquetes importados.
    return ui.base.base_page(
        rx.cond(
            auth.state.SessionState.is_authenticated,
            pages.dashboard_component(),
            pages.landing_component(),
        )
    )

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

# --- CORRECCIÓN: Registro de páginas usando la notación de punto ---

# Página principal
app.add_page(index, on_load=articles.state.ArticlePublicState.load_posts)

# Páginas de autenticación
app.add_page(auth.pages.my_login_page, route=reflex_local_auth.routes.LOGIN_ROUTE)
app.add_page(auth.pages.my_register_page, route=reflex_local_auth.routes.REGISTER_ROUTE)
app.add_page(auth.pages.my_logout_page, route=navigation.routes.LOGOUT_ROUTE)

# Páginas generales
app.add_page(pages.about_page, route=navigation.routes.ABOUT_US_ROUTE)
app.add_page(pages.protected_page, route="/protected/", on_load=auth.state.SessionState.on_load)
app.add_page(pages.pricing_page, route=navigation.routes.PRICING_ROUTE)

# Páginas de Artículos (públicas)
app.add_page(
    articles.list.article_public_list_page,
    route=navigation.routes.ARTICLE_LIST_ROUTE,
    on_load=articles.state.ArticlePublicState.load_posts,
)
app.add_page(
    articles.detail.article_detail_page,
    route=f"{navigation.routes.ARTICLE_LIST_ROUTE}/[article_id]",
    on_load=articles.state.ArticlePublicState.get_post_detail,
)

# Páginas de Blog (privadas)
app.add_page(
    blog.list.blog_post_list_page,
    route=navigation.routes.BLOG_POSTS_ROUTE,
    on_load=blog.state.BlogPostState.load_posts
)
app.add_page(blog.add.blog_post_add_page, route=navigation.routes.BLOG_POST_ADD_ROUTE)
app.add_page(
    blog.detail.blog_post_detail_page,
    route="/blog/[blog_id]",
    on_load=blog.state.BlogPostState.get_post_detail
)
app.add_page(
    blog.edit.blog_post_edit_page,
    route="/blog/[blog_id]/edit",
    on_load=blog.state.BlogPostState.get_post_detail
)

# Páginas de Contacto
app.add_page(contact.page.contact_page, route=navigation.routes.CONTACT_US_ROUTE)
app.add_page(
    contact.page.contact_entries_list_page,
    route=navigation.routes.CONTACT_ENTRIES_ROUTE,
    on_load=contact.state.ContactState.load_entries
)