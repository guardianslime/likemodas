import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List

class Sortable(NoSSRComponent):
    """
    Un componente de Reflex que envuelve la biblioteca 'SortableJS' para permitir
    listas reordenables mediante drag-and-drop.
    """
    # El nombre exacto del paquete en npm.
    library = "sortablejs"
    # El tag que usaremos, aunque en este caso la lógica está en el código custom.
    tag = "div"

    # Evento que se disparará cuando el usuario termine de arrastrar un elemento.
    # Nos devolverá el índice antiguo y el nuevo del elemento movido.
    on_end: rx.EventHandler[lambda old_index, new_index: [old_index, new_index]]

    def _get_custom_code(self) -> str:
        # Este código JavaScript se encarga de inicializar SortableJS en el
        # contenedor del componente y de conectar su evento 'onEnd' con nuestro
        # EventHandler de Reflex.
        return """
import React, { useEffect, useRef } from "react";
import Sortable from "sortablejs";

export const SortableWrapper = (props) => {
    const ref = useRef(null);

    useEffect(() => {
        if (ref.current) {
            new Sortable(ref.current, {
                animation: 150, // Duración de la animación al soltar
                ghostClass: 'sortable-ghost', // Clase CSS para el 'fantasma'
                chosenClass: 'sortable-chosen', // Clase CSS para el elemento elegido
                dragClass: 'sortable-drag', // Clase CSS para el elemento que se arrastra
                onEnd: (evt) => {
                    // Cuando el usuario suelta el elemento, llamamos al evento de Reflex
                    // con los índices de la posición original y la nueva.
                    const { on_end } = props;
                    if (on_end) {
                        on_end(evt.oldIndex, evt.newIndex);
                    }
                }
            });
        }
    }, []);

    // Pasamos todas las props, incluyendo 'children' y 'style', al div.
    const { children, ...rest } = props;
    return (
        <div {...rest} ref={ref}>
            {children}
        </div>
    );
};
"""
    def _render(self):
        # Usamos _render para poder usar nuestro componente JS personalizado.
        return rx.fragment(
            rx.chakra.html(f"<SortableWrapper {...self.get_props()}>{self.children}</SortableWrapper>")
        )

# Creamos una instancia para usarla más fácilmente
sortable_js = Sortable.create