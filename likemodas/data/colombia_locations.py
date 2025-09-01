# likemodas/data/colombia_locations.py

# Diccionario de ciudades y sus barrios. 
# Debes completar esta lista según tus necesidades.
LOCATIONS = {
    "Bogotá D.C.": [
        "Usaquén", "Chapinero", "Santa Fe", "San Cristóbal", 
        "Usme", "Tunjuelito", "Bosa", "Kennedy", "Fontibón", 
        "Engativá", "Suba", "Barrios Unidos", "Teusaquillo", 
        "Los Mártires", "Antonio Nariño", "Puente Aranda", 
        "La Candelaria", "Rafael Uribe Uribe", "Ciudad Bolívar", "Sumapaz"
    ],
    "Medellín": [
        "Popular", "Santa Cruz", "Manrique", "Aranjuez", 
        "Castilla", "Doce de Octubre", "Robledo", "Villa Hermosa",
        "Buenos Aires", "La Candelaria", "Laureles-Estadio", "La América",
        "San Javier", "El Poblado", "Guayabal", "Belén"
    ],
    "Cali": [
        "Comuna 1", "Comuna 2", "Comuna 3", "Comuna 4", "Comuna 5",
        "Comuna 6", "Comuna 7", "Comuna 8", "Comuna 9", "Comuna 10",
        "Comuna 11", "Comuna 12", "Comuna 13", "Comuna 14", "Comuna 15",
        "Comuna 16", "Comuna 17", "Comuna 18", "Comuna 19", "Comuna 20",
        "Comuna 21", "Comuna 22"
    ],
    "Popayán": [
        "Centro Histórico", "El Cadillal", "La Pamba", "El Empedrado",
        "La Esmeralda", "Modelo", "Bolívar", "José María Obando"
    ]
}

def load_colombia_data():
    return LOCATIONS