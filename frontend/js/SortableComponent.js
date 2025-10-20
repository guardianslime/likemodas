// En: assets/js/SortableComponent.js

import React, { useEffect, useRef } from "react";
import Sortable from "sortablejs";

// Definimos nuestro componente de React.
function SortableProvider(props) {
    const ref = useRef(null);
    useEffect(() => {
        if (!ref.current) {
            return;
        }
        // Inicializamos la librería SortableJS en nuestro div.
        new Sortable(ref.current, {
            animation: 150,
            onEnd: (evt) => {
                const { on_end } = props;
                if (on_end) {
                    // Cuando el usuario termina de arrastrar, llamamos al evento de Reflex.
                    on_end(evt.oldIndex, evt.newIndex);
                }
            }
        });
    }, [ref]);

    // Renderizamos un div simple que contendrá los elementos que Reflex le pase.
    const { children, ...rest } = props;
    return (
        <div {...rest} ref={ref}>
            {children}
        </div>
    );
}

// Exportamos nuestro componente como el export por defecto. Esto es importante.
export default SortableProvider;