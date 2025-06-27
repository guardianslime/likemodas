# full_stack_python/contact/__init__.py

# Exporta las páginas del módulo
from .page import contact_page, contact_entries_list_page

# Exporta los NUEVOS estados refactorizados
from .state import ContactHistoryState, ContactAddFormState

# Define lo que es "público" para este paquete
__all__ = [
    "contact_page",
    "contact_entries_list_page",
    "ContactHistoryState",
    "ContactAddFormState",
]