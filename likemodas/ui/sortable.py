# likemodas/ui/sortable.py (VERSIÓN FINAL Y CORRECTA)

import reflex as rx

# Heredamos de rx.Component, la clase base para componentes personalizados
class Sortable(rx.Component):
    """
    Un componente de Reflex que envuelve la biblioteca 'SortableJS' para permitir
    listas reordenables mediante drag-and-drop.
    """
    # La biblioteca de JavaScript que necesitamos que se importe en el frontend.
    library = "sortablejs"

    # El 'tag' es el NOMBRE del componente de React que definiremos en nuestro código JS.
    tag = "SortableProvider"

    # La única propiedad que necesitamos es el manejador de eventos que se
    # disparará cuando el usuario termine de arrastrar un elemento.
    on_end: rx.EventHandler[lambda old_index, new_index: [old_index, new_index]]

    # Importaciones necesarias para nuestro código JavaScript.
    def get_imports(self) -> dict:
        return {
            "react": {"useEffect", "useRef"},
            "sortablejs": "Sortable",
        }
    
    # El código JavaScript personalizado.
    def get_custom_code(self) -> str:
        return """
// El nombre de esta función, 'SortableProvider', debe coincidir con el `tag` de arriba.
function SortableProvider(props) {
    const ref = useRef(null);
    useEffect(() => {
        if (!ref.current) {
            return;
        }
        // Inicializamos SortableJS en el div que renderizamos.
        new Sortable(ref.current, {
            animation: 150, // Animación suave al soltar
            onEnd: (evt) => {
                // Cuando el evento 'onEnd' de SortableJS se dispara...
                const { on_end } = props;
                if (on_end) {
                    // ...llamamos a nuestro EventHandler de Reflex con los índices.
                    on_end(evt.oldIndex, evt.newIndex);
                }
            }
        });
    }, [ref]);

    // Simplemente renderizamos un div y le pasamos todas las propiedades que Reflex
    // nos da, incluyendo los `children` (que pueden ser el resultado de un rx.foreach).
    const { children, ...rest } = props;
    return (
        <div {...rest} ref={ref}>
            {children}
        </div>
    );
}
"""

# Creamos la función "fábrica" para poder usar nuestro componente fácilmente.
sortable_js = Sortable.create