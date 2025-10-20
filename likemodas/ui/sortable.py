# likemodas/ui/sortable.py (VERSIÓN FINAL CON EL PATRÓN CORRECTO)

import reflex as rx

class Sortable(rx.Component):
    """
    Un componente de Reflex que envuelve la biblioteca 'SortableJS' para permitir
    listas reordenables mediante drag-and-drop.
    """
    # 1. RESTAURAMOS el atributo 'library'. Esto es crucial.
    # Le dice a Reflex que nuestro componente depende de la librería 'sortablejs'.
    library = "sortablejs"

    # 2. El 'tag' sigue siendo el nombre de nuestro componente React personalizado.
    tag = "SortableProvider"

    # La propiedad para el manejador de eventos se mantiene igual.
    on_end: rx.EventHandler[lambda old_index, new_index: [old_index, new_index]]

    # Las importaciones para nuestro código JS personalizado.
    def get_imports(self) -> dict:
        return {
            "react": {"useEffect", "useRef"},
            # Importamos la clase 'Sortable' desde la librería 'sortablejs'
            "sortablejs": "Sortable",
        }
    
    # El código de nuestro componente React personalizado. No usamos 'window' aquí.
    def get_custom_code(self) -> str:
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