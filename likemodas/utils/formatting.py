# En: likemodas/utils/formatting.py (CORREGIDO)

from typing import Optional, Union
import reflex as rx

def format_to_cop(price: Union[rx.Var[Optional[float]], Optional[float]]) -> Union[rx.Var[str], str]:
    """
    [VERSIÓN DEFINITIVA] Formatea un valor a moneda COP, funcionando tanto
    para Vars de Reflex en la UI como para floats/ints normales en el backend.
    """
    # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
    # 1. Primero, se maneja el caso de los números normales de Python (backend).
    if isinstance(price, (int, float)):
        if price is None or price < 1:
            return "$ 0"
        
        # Lógica de formateo que funciona solo en Python.
        formatted_number = f"{price:,.0f}"
        colombian_format = formatted_number.replace(',', '.')
        return f"$ {colombian_format}"

    # 2. Si no es un número de Python, se asume que es un rx.Var (de cualquier tipo)
    #    y se usa la lógica del frontend con rx.call_script.
    return rx.cond(
        price > 0,
        # Se usa la función nativa del navegador para formatear la moneda.
        rx.call_script(
            f"new Intl.NumberFormat('es-CO', {{ style: 'currency', currency: 'COP', maximumFractionDigits: 0 }}).format({price.to(str)})"
        ),
        "$ 0"
    )
    # --- ✨ FIN DE LA CORRECCIÓN ✨ ---