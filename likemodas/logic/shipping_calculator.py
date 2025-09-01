# likemodas/logic/shipping_calculator.py (NUEVO ARCHIVO)

from collections import deque
from ..data.geography_data import BARRIO_A_COMUNA, COMUNA_ADJACENCY

def find_shortest_commune_path(start_commune: int, end_commune: int) -> list[int]:
    """
    Encuentra la ruta más corta entre dos comunas usando el algoritmo Breadth-First Search (BFS).
    Devuelve una lista de comunas que representan la ruta.
    """
    if start_commune not in COMUNA_ADJACENCY or end_commune not in COMUNA_ADJACENCY:
        return []

    queue = deque([[start_commune]])
    visited = {start_commune}

    while queue:
        path = queue.popleft()
        node = path[-1]

        if node == end_commune:
            return path

        for neighbor in COMUNA_ADJACENCY.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)
    
    return [] # No se encontró ruta

def calculate_dynamic_shipping(
    base_cost: float, 
    seller_barrio: str | None, 
    buyer_barrio: str | None
) -> float:
    """
    Calcula el costo de envío final basado en la ruta de comunas.
    """
    # Si falta información clave, solo se cobra el costo base.
    if not seller_barrio or not buyer_barrio:
        return base_cost

    # Nivel 1: Mismo Barrio (costo de distancia es 0)
    if seller_barrio == buyer_barrio:
        return base_cost

    seller_commune = BARRIO_A_COMUNA.get(seller_barrio)
    buyer_commune = BARRIO_A_COMUNA.get(buyer_barrio)

    # Si algún barrio no está en el mapa, devolvemos el costo base.
    if not seller_commune or not buyer_commune:
        return base_cost
        
    # Nivel 2: Mismo Comuna, diferente barrio
    if seller_commune == buyer_commune:
        distance_cost = 2000.0
    else:
        # Nivel 3: Diferente Comuna, se calcula la ruta
        path = find_shortest_commune_path(seller_commune, buyer_commune)
        if not path:
            # Si no hay ruta (improbable), usamos un costo alto por defecto.
            distance_cost = 12000.0
        else:
            # El costo aumenta por cada "salto" de comuna.
            # Un multiplicador de 4000 por salto da un buen escalado.
            num_jumps = len(path) - 1
            distance_cost = num_jumps * 4000.0

    # Sumamos el costo base al de la distancia y aplicamos el tope máximo.
    total_shipping_cost = min(base_cost + distance_cost, 12000.0)
    
    return total_shipping_cost