# likemodas/ui/sortable.py (VERSIÓN FINAL DEFINITIVA)

import reflex as rx

class Sortable(rx.Component):
    """
    Un componente de Reflex que envuelve la biblioteca 'SortableJS' para permitir
    listas reordenables mediante drag-and-drop.
    """
    # --- ✨ INICIO DE LA CORRECCIÓN CLAVE ✨ ---
    # Se elimina la línea: library = "sortablejs"
    # Esto le dice a Reflex que el componente del `tag` no viene de una librería externa,
    # sino que está definido en nuestro `get_custom_code`.
    # --- ✨ FIN DE LA CORRECCIÓN CLAVE ✨ ---

    tag = "SortableProvider"

    on_end: rx.EventHandler[lambda old_index, new_index: [old_index, new_index]]

    def get_imports(self) -> dict:
        # Aquí sí importamos la clase 'Sortable' de la librería para usarla en nuestro JS.
        return {
            "react": {"useEffect", "useRef"},
            "sortablejs": "Sortable",
        }
    
    def get_custom_code(self) -> str:
        # Nuestro código JS personalizado que define el componente 'SortableProvider'
        return """
function SortableProvider(props) {
    const ref = useRef(null);
    useEffect(() => {
        if (!ref.current) {
            return;
        }
        new Sortable(ref.current, {
            animation: 150,
            onEnd: (evt) => {
                const { on_end } = props;
                if (on_end) {
                    on_end(evt.oldIndex, evt.newIndex);
                }
            }
        });
    }, [ref]);

    const { children, ...rest } = props;
    return (
        <div {...rest} ref={ref}>
            {children}
        </div>
    );
}
"""

sortable_js = Sortable.create