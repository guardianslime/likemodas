# likemodas/ui/sortable.py (VERSIÓN FINAL Y ROBUSTA)

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

    # --- ✨ INICIO DE LA CORRECCIÓN FINAL ✨ ---
    def _render(self):
        """
        Renderiza el componente, manejando correctamente tanto un hijo único como
        una lista de hijos (generada por rx.foreach).
        """
        props_dict = {
            prop_name: getattr(self, prop_name)
            for prop_name in self.get_props()
        }
        props_dict.pop("children", None)
        prop_str = " ".join(f"{key}={{{value}}}" for key, value in props_dict.items())
        
        children_str = ""
        if self.children:
            # Si self.children es una lista (generada por rx.foreach)...
            if isinstance(self.children, list):
                # ...construimos una cadena que representa un array de JS.
                child_vars = ", ".join(c._var_full_name_unwrapped for c in self.children)
                children_str = f"{{ [{child_vars}] }}"
            else:
                # Si es un solo hijo, lo manejamos como antes.
                children_str = f"{{ {self.children._var_full_name_unwrapped} }}"

        return rx.fragment(
            rx.chakra.html(
                f"<SortableWrapper {prop_str}>{children_str}</SortableWrapper>"
            )
        )
    # --- ✨ FIN DE LA CORRECCIÓN FINAL ✨ ---

# Creamos una instancia para usarla más fácilmente
sortable_js = Sortable.create