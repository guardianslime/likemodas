# full_stack_python/contact/__init__.py

from .page import contact_page, contact_entries_list_page
from .state import ContactState # Exporta el estado único

__all__ = [
    "contact_page",
    "contact_entries_list_page",
    "ContactState",
]