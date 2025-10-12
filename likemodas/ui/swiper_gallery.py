import reflex as rx
from reflex.components.component import NoSSRComponent
from typing import Any, List, Dict, Union

# El único paquete que se necesita instalar desde npm.
LIBRARY = "swiper"

class SwiperGallery(NoSSRComponent):
    """Wrapper para el componente principal de Swiper, ahora autoconfigurable."""
    library = LIBRARY
    tag = "CustomSwiper" # Mantenemos el nombre único para evitar colisiones.

    # Las props no cambian.
    navigation: rx.Var[bool]
    pagination: rx.Var[Dict[str, bool]]
    loop: rx.Var[bool]
    space_between: rx.Var[int]
    slides_per_view: rx.Var[Union[int, str]]
    initial_slide: rx.Var[int]
    class_name: rx.Var[str]

    # Los handlers no cambian.
    on_slide_change: rx.EventHandler[lambda swiper: [swiper.activeIndex]]
    on_click: rx.EventHandler[lambda swiper, event: [swiper.clickedIndex]]

    def add_imports(self) -> dict:
        # Se movió la importación de CSS al código JS para mayor robustez.
        return {}

    def _get_custom_code(self) -> str | None:
        """
        Inyecta código JS que importa todo lo necesario y crea un componente
        wrapper que maneja los módulos automáticamente.
        """
        return """
import React from 'react';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination } from 'swiper/modules';

// Importamos el CSS directamente en el JavaScript.
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';

// Creamos nuestro componente único que envuelve al Swiper real.
export const CustomSwiper = (props) => {
  const { children, ...rest } = props;
  
  // LÓGICA CLAVE: Construimos la lista de módulos a usar
  // basándonos en las props que llegan desde Python.
  const modules_to_use = [];
  if (props.navigation) {
    modules_to_use.push(Navigation);
  }
  if (props.pagination) {
    modules_to_use.push(Pagination);
  }

  return (
    <Swiper modules={modules_to_use} {...rest}>
      {children}
    </Swiper>
  );
};

// También exportamos SwiperSlide con un nombre único.
export { SwiperSlide as CustomSwiperSlide };
"""

class SwiperSlide(NoSSRComponent):
    """Wrapper para el componente SwiperSlide."""
    library = LIBRARY
    tag = "CustomSwiperSlide"

# Solo necesitamos exportar los componentes que se renderizan.
swiper_gallery = SwiperGallery.create
swiper_slide = SwiperSlide.create