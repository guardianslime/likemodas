# likemodas/ui/sortable.py (VERSIÓN FINAL CON ARCHIVO EXTERNO)

import reflex as rx

class Sortable(rx.Component):
    """
    Componente de Reflex que carga el componente React 'SortableProvider'
    desde un archivo externo en la carpeta assets.
    """
    # 1. La 'library' ahora apunta a nuestro archivo JS, relativo a la carpeta 'assets'.
    library = "/js/SortableComponent.js"

    # 2. El 'tag' es el nombre del componente que estamos exportando en el archivo JS.
    tag = "SortableProvider"
    
    # 3. Indicamos que estamos usando `export default` en nuestro archivo JS.
    is_default = True

    # 4. La definición del evento que nuestro componente puede emitir se mantiene igual.
    on_end: rx.EventHandler[lambda old_index, new_index: [old_index, new_index]]

# La función para crear el componente no cambia.
sortable_js = Sortable.create