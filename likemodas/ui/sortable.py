# likemodas/ui/sortable.py (CORREGIDO)

import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List

class Sortable(NoSSRComponent):
    """
    Un componente de Reflex que envuelve la biblioteca 'SortableJS' para permitir
    listas reordenables mediante drag-and-drop.
    """
    library = "sortablejs"
    tag = "div"

    on_end: rx.EventHandler[lambda old_index, new_index: [old_index, new_index]]

    def _get_custom_code(self) -> str:
        return """
import React, { useEffect, useRef } from "react";
import Sortable from "sortablejs";

export const SortableWrapper = (props) => {
    const ref = useRef(null);

    useEffect(() => {
        if (ref.current) {
            new Sortable(ref.current, {
                animation: 150,
                ghostClass: 'sortable-ghost',
                chosenClass: 'sortable-chosen',
                dragClass: 'sortable-drag',
                onEnd: (evt) => {
                    const { on_end } = props;
                    if (on_end) {
                        on_end(evt.oldIndex, evt.newIndex);
                    }
                }
            });
        }
    }, []);

    const { children, ...rest } = props;
    return (
        <div {...rest} ref={ref}>
            {children}
        </div>
    );
};
"""

    # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
    def _render(self):
        """
        Renderiza el componente, construyendo manualmente la cadena de propiedades
        para evitar el SyntaxError de Python.
        """
        # Obtenemos las propiedades como un diccionario
        props = self.get_props()
        # Los 'children' se manejan por separado
        props.pop("children", None)

        # Creamos una cadena de texto con las propiedades en formato JSX
        # Ej: on_end={_on_end_5c1b} style={{...}}
        prop_str = " ".join(f"{key}={{{value}}}" for key, value in props.items())
        
        # Obtenemos el nombre de la variable de los children para interpolarla
        children_str = f"{{ {self.children._var_full_name_unwrapped} }}" if self.children else ""

        # Construimos el HTML final
        return rx.fragment(
            rx.chakra.html(
                f"<SortableWrapper {prop_str}>{children_str}</SortableWrapper>"
            )
        )
    # --- ✨ FIN DE LA CORRECCIÓN ✨ ---

# Creamos una instancia para usarla más fácilmente
sortable_js = Sortable.create