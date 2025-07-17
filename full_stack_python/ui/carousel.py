# full_stack_python/ui/carousel.py (VERSIÓN FINAL)

import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import List, Set

class SwiperContainer(NoSSRComponent):
    """
    Wrapper de Reflex para el componente de React Swiper.
    Proporciona un carrusel de imágenes deslizable.
    """
    # El componente principal viene de 'swiper/react'
    library = "swiper/react"
    tag = "Swiper"
    is_default = True

    # La dependencia de npm es el paquete 'swiper'
    lib_dependencies: List[str] = ["swiper"]

    # Propiedades de Swiper expuestas como Vars de Reflex.
    pagination: rx.Var[bool] = True
    navigation: rx.Var[bool] = False
    allow_touch_move: rx.Var[bool] = True
    loop: rx.Var[bool] = True

    def _get_custom_triggers(self) -> Set[str]:
        """Registra los eventos que Swiper puede emitir para evitar errores de 'ValueError'."""
        return super()._get_custom_triggers() | {
            "on_slide_change",
            "on_init",
            "on_touch_start",
            "on_touch_end",
        }
    
    def _get_imports(self):
        """Define las importaciones de JS y CSS necesarias."""
        imports = super()._get_imports()

        # ✨ CORRECCIÓN: Se asegura de manejar un conjunto (set) para los imports de CSS.
        css_imports = imports.get("", set())
        css_imports.update([
            "swiper/css",
            "swiper/css/pagination",
            "swiper/css/navigation",
        ])
        imports[""] = css_imports

        # ✨ CORRECCIÓN: Se importan los módulos 'Pagination' y 'Navigation' desde la librería 'swiper'.
        # Esto se hace de forma segura, modificando el diccionario de componentes.
        swiper_modules = imports.setdefault("swiper", {})
        components = swiper_modules.setdefault("components", set())
        components.update(["Pagination", "Navigation"])
        
        return imports

    def _get_props(self) -> dict:
        """Pasa las props al componente de React, incluyendo los módulos activados."""
        props = super()._get_props()
        
        modules = []
        if self.pagination:
            # Crea una referencia a la variable JS del módulo 'Pagination'
            modules.append(rx.vars.Var.create_safe("Pagination", _var_is_local=False))
        if self.navigation:
            # Crea una referencia a la variable JS del módulo 'Navigation'
            modules.append(rx.vars.Var.create_safe("Navigation", _var_is_local=False))
        
        if modules:
            props["modules"] = modules
        return props


class SwiperSlide(NoSSRComponent):
    """Wrapper de Reflex para el componente React SwiperSlide."""
    library = "swiper/react"
    tag = "SwiperSlide"
    is_default = False

# Creación de instancias simplificadas para facilitar su uso.
swiper_container = SwiperContainer.create
swiper_slide = SwiperSlide.create