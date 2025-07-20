# likemodas/blog/__init__.py (VERSIÓN CORREGIDA)

from .add import blog_post_add_page
from .detail import blog_post_detail_page
from .edit import blog_post_edit_page
from .list import blog_post_list_page
# --- 👇 CAMBIO: Se elimina 'BlogViewState' de esta línea ---
from .state import BlogPostState, BlogAddFormState, BlogEditFormState, CommentState

__all__ = [
    'blog_post_add_page',
    'blog_post_detail_page',
    'blog_post_edit_page',
    'blog_post_list_page',
    'BlogPostState',
    'BlogAddFormState',
    'BlogEditFormState',
    # --- 👇 CAMBIO: Se elimina 'BlogViewState' de esta lista ---
    'CommentState',
]