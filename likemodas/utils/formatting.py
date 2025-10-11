# En: likemodas/utils/formatting.py

from typing import Optional, Union
import reflex as rx

def format_to_cop(price: Union[rx.Var[Optional[float]], Optional[float]]) -> Union[rx.Var[str], str]:
    """
    [VERSIÓN DEFINITIVA] Formatea un valor a moneda COP, funcionando tanto
    para Vars de Reflex en la UI como para floats/ints normales en el backend.
    """
    # CASO 1: La variable es una Var de Reflex (usada en la UI).
    # Devuelve una estructura condicional de Reflex.
    if isinstance(price, rx.Var):
        return rx.cond(
            price > 0,
            rx.call_script(
                f"new Intl.NumberFormat('es-CO', {{ style: 'currency', currency: 'COP', maximumFractionDigits: 0 }}).format({price.to(str)})"
            ),
            "$ 0"
        )
    
    # CASO 2: El valor es un número normal de Python (usado en el backend/modelos).
    # Devuelve un string de Python normal.
    if isinstance(price, (int, float)):
        if price is None or price < 1:
            return "$ 0"
        
        # Lógica de formateo original que funciona en Python.
        formatted_number = f"{price:,.0f}"
        colombian_format = formatted_number.replace(',', '.')
        return f"$ {colombian_format}"

    # Caso por defecto si el tipo no es esperado.
    return "$ 0"