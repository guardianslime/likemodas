# full_stack_python/blog/__init__.py

from .add import blog_post_add_page
from .detail import blog_post_detail_page
from .edit import blog_post_edit_page
from .list import blog_post_list_page
# --- ✨ CAMBIO AQUÍ ✨ ---
# Se han eliminado los estados de este archivo de inicialización.
# from .state import BlogPostState, BlogAddFormState, BlogPublicState, BlogViewState

__all__ = [
    'blog_post_add_page',
    'blog_post_detail_page',
    'blog_post_edit_page',
    'blog_post_list_page',
    # --- ✨ Y TAMBIÉN SE ELIMINAN DE AQUÍ ✨ ---
    # 'BlogPostState',
    # 'BlogAddFormState',
    # 'BlogPublicState',
    # 'BlogViewState',
]