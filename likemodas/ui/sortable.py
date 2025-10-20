# likemodas/ui/sortable.py
import reflex as rx
from typing import Any

class Sortable(rx.Component):
    """
    Un componente wrapper que integra la librería SortableJS para crear
    listas reordenables mediante arrastrar y soltar.
    """
    # La librería de npm que Reflex debe instalar.
    library = "sortablejs"
    
    # El nombre del componente React que definiremos en get_custom_code.
    tag = "SortableProvider"

    # El manejador de eventos que se llamará desde JS cuando se suelte un elemento.
    # Enviará el índice antiguo y el nuevo al estado de Python.
    on_end: rx.EventHandler[lambda old_index, new_index: [old_index, new_index]]

    def get_imports(self) -> dict[str, Any]:
        """
        Importa las dependencias necesarias para el componente React personalizado.
        """
        return {
            "react": {"useEffect", "useRef"},
            "sortablejs": "Sortable",
        }

    def get_custom_code(self) -> str:
        """
        El código del componente React que inicializa SortableJS
        y conecta sus eventos con los de Reflex.
        """
        return """
function SortableProvider(props) {
    const ref = React.useRef(null);

    React.useEffect(() => {
        // Asegurarse de que el elemento DOM exista en el navegador.
        if (!ref.current) {
            return;
        }
        
        // Inicializar SortableJS en el contenedor.
        new Sortable(ref.current, {
            animation: 150, // Animación suave al arrastrar
            ghostClass: 'sortable-ghost', // Clase CSS para el elemento fantasma
            
            // Esta función se ejecuta cuando el usuario suelta el elemento.
            onEnd: (evt) => {
                const { on_end } = props;
                // Si el manejador de eventos on_end fue pasado desde Python, lo llamamos.
                if (on_end) {
                    // Enviamos los índices de vuelta al estado de AppState.
                    on_end(evt.oldIndex, evt.newIndex);
                }
            }
        });
    }, [ref]); // El efecto se ejecuta solo una vez cuando el ref está listo.

    // Extraemos las propiedades que no son estándar de un div.
    const { children, on_end, ...rest } = props;

    // Renderizamos un div que contendrá los elementos reordenables.
    return (
        <div {...rest} ref={ref}>
            {children}
        </div>
    );
}
"""

# Función de fábrica para usar el componente fácilmente en la UI.
sortable_js = Sortable.create