# likemodas/ui/sortable.py (VERSIÓN CON RUTA SIMPLIFICADA)

import reflex as rx

class Sortable(rx.Component):
    """
    Componente de Reflex que carga el componente React 'SortableProvider'
    desde un archivo externo en la carpeta assets.
    """
    # --- ✨ INICIO DE LA CORRECCIÓN CLAVE ✨ ---
    # La 'library' ahora apunta directamente al archivo en la raíz de 'assets'.
    library = "/SortableComponent.js"
    # --- ✨ FIN DE LA CORRECCIÓN CLAVE ✨ ---

    tag = "SortableProvider"
    is_default = True
    on_end: rx.EventHandler[lambda old_index, new_index: [old_index, new_index]]

    def get_imports(self) -> dict:
        return {
            "react": {"useEffect", "useRef"},
            "sortablejs": "Sortable",
        }
    
    def get_custom_code(self) -> str:
        # El código JS no cambia, pero se debe dejar aquí para que Reflex lo encuentre.
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