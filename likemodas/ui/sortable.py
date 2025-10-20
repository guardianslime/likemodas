# likemodas/ui/sortable.py (VERSIÓN FINAL CON CORRECCIÓN DE SCOPE)

import reflex as rx

class Sortable(rx.Component):
    """
    Un componente de Reflex que envuelve la biblioteca 'SortableJS' para permitir
    listas reordenables mediante drag-and-drop.
    """
    tag = "SortableProvider"

    on_end: rx.EventHandler[lambda old_index, new_index: [old_index, new_index]]

    def get_imports(self) -> dict:
        return {
            "react": {"useEffect", "useRef"},
            "sortablejs": "Sortable",
        }
    
    def get_custom_code(self) -> str:
        return """
// --- ✨ INICIO DE LA CORRECCIÓN CLAVE ✨ ---
// Adjuntamos el componente al objeto global 'window' para garantizar que esté definido.
window.SortableProvider = function(props) {
// --- ✨ FIN DE LA CORRECCIÓN CLAVE ✨ ---
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