from datetime import datetime, timezone
import sqlalchemy
from sqlalchemy.sql import func
from ..models import BlogPostModel

def calculate_review_impact(
    current_score: float, 
    old_rating: int, 
    new_rating: int, 
    is_first_review: bool = False
) -> float:
    """
    Calcula el nuevo puntaje de calidad basado en las reglas de negocio:
    - Castiga fuerte si bajan la nota.
    - Premia si suben la nota.
    - Premia extra si es la primera opinión y es buena.
    """
    delta = new_rating - old_rating
    
    # 1. Si es una opinión nueva (old_rating es 0)
    if old_rating == 0:
        impact = float(new_rating)
        # Regla: Si es la primera review de este usuario y da buena nota (>=4), vale x1.5
        if is_first_review and new_rating >= 4:
            impact *= 1.5 
        return current_score + impact

    # 2. Si es una actualización (El usuario cambió su nota)
    if delta > 0:
        # Regla: Mejorar calificación (delta positivo) bonifica x1.5
        # Ejemplo: Subir de 3 a 5 (delta 2) suma 3 puntos.
        impact = delta * 1.5 
        return current_score + impact
        
    elif delta < 0:
        # Regla: Bajar calificación (delta negativo) castiga x2.0
        # Ejemplo: Bajar de 5 a 3 (delta -2) resta 4 puntos.
        impact = delta * 2.0 
        return current_score + impact
        
    # Si la nota es igual, el score se mantiene
    return current_score

def get_ranking_query_sort(model):
    """
    Devuelve la expresión SQL para ordenar por gravedad.
    Fórmula: (Calidad + (Ventas * PesoVenta)) / (HorasDesdeInteracción + 2)^Gravedad
    """
    # Peso de las ventas: Cada venta equivale a 5 puntos de "calidad"
    SALES_WEIGHT = 5.0
    # Gravedad: Qué tan rápido caen los posts viejos (1.8 es un estándar fuerte)
    GRAVITY = 1.8 
    
    # Calculamos horas desde la última interacción relevante (Venta o Review)
    # Usamos last_interaction_at para mantener vivos a los productos que se mueven
    age_in_hours = func.extract('epoch', func.now() - model.last_interaction_at) / 3600
    
    # El numerador: La popularidad bruta
    score = (model.quality_score + (model.total_units_sold * SALES_WEIGHT))
    
    # El denominador: El paso del tiempo
    time_decay = func.power(age_in_hours + 2, GRAVITY)
    
    return score / time_decay