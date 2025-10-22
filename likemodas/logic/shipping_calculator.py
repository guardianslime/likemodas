# likemodas/logic/shipping_calculator.py (LÓGICA ADAPTATIVA)

from collections import deque
# AHORA IMPORTAMOS EL DICCIONARIO MAESTRO
from ..data.geography_data import CITY_SPECIFIC_DATA

def find_shortest_commune_path(start_commune: int, end_commune: int, adjacency_graph: dict) -> list[int]:
    """
    Encuentra la ruta más corta entre dos comunas usando un grafo de adyacencia específico.
    """
    if start_commune not in adjacency_graph or end_commune not in adjacency_graph:
        return []

    queue = deque([[start_commune]])
    visited = {start_commune}

    while queue:
        path = queue.popleft()
        node = path[-1]

        if node == end_commune:
            return path

        for neighbor in adjacency_graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)
    
    return []

def calculate_dynamic_shipping(
    base_cost: float, 
    seller_barrio: str | None, 
    buyer_barrio: str | None,
    seller_city: str | None,
    buyer_city: str | None
) -> float:
    """
    [VERSIÓN FINAL CORREGIDA] Calcula el costo de envío final, siempre partiendo
    del costo base y sumando los costos de distancia.
    """
    # Si las ciudades son diferentes, el costo es fijo y alto.
    if seller_city and buyer_city and seller_city != buyer_city:
        return 15000.0

    # Si no hay datos suficientes o los barrios son iguales, el costo es simplemente el base.
    if not seller_city or not seller_barrio or not buyer_barrio or seller_barrio == buyer_barrio:
        return base_cost
    
    # Obtenemos los datos geográficos de la ciudad del vendedor
    city_data = CITY_SPECIFIC_DATA.get(seller_city)
    if not city_data:
        return base_cost

    barrio_a_comuna_map = city_data["barrio_map"]
    comuna_adjacency_graph = city_data["adjacency"]
    
    seller_commune = barrio_a_comuna_map.get(seller_barrio)
    buyer_commune = barrio_a_comuna_map.get(buyer_barrio)

    if not seller_commune or not buyer_commune:
        return base_cost

    # --- ✨ LÓGICA DE CÁLCULO CORREGIDA Y SIMPLIFICADA ✨ ---
    
    costo_adicional = 0.0
    
    # Si los barrios son diferentes pero la comuna es la misma
    if seller_commune == buyer_commune:
        costo_adicional = 2000.0
    # Si las comunas son diferentes
    else:
        path = find_shortest_commune_path(seller_commune, buyer_commune, comuna_adjacency_graph)
        if not path:
            # Si no se encuentra una ruta (caso improbable), se usa un costo alto.
            return 12000.0
        else:
            # Se calcula el costo basado en el número de "saltos" entre comunas.
            num_jumps = len(path) - 1
            costo_adicional = num_jumps * 4000.0

    # El costo total es SIEMPRE el base + el adicional, con un tope máximo.
    total_shipping_cost = min(base_cost + costo_adicional, 12000.0)
    
    return total_shipping_cost