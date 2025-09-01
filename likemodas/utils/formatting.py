# likemodas/utils/formatting.py

from typing import Optional

def format_to_cop(price: Optional[float]) -> str:
    """
    Formatea un número a moneda COP ($ 55.000) sin depender del locale del sistema.
    """
    if price is None or price < 1:
        return "$ 0"
    
    # 1. Formatea el número con comas como separador de miles y sin decimales.
    #    Ejemplo: 55000 -> "55,000"
    formatted_number = f"{price:,.0f}"
    
    # 2. Reemplaza la coma por un punto para el estándar colombiano.
    #    Ejemplo: "55,000" -> "55.000"
    colombian_format = formatted_number.replace(',', '.')
    
    # 3. Añade el símbolo de peso y un espacio.
    #    Ejemplo: "55.000" -> "$ 55.000"
    return f"$ {colombian_format}"

