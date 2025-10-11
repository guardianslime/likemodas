# En: likemodas/utils/formatting.py

from typing import Optional

def format_to_cop(price: Optional[float]) -> str:
    """
    Formatea un número a moneda COP ($ 55.000) de forma segura.
    """
    if price is None or price < 1:
        return "$ 0"
    
    formatted_number = f"{price:,.0f}"
    colombian_format = formatted_number.replace(',', '.')
    return f"$ {colombian_format}"