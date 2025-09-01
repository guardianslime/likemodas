# likemodas/data/geography_data.py (VERSIÓN FINAL)

"""
Contiene los datos geográficos de Popayán, incluyendo comunas, barrios,
y un grafo de adyacencia de las comunas para el cálculo de rutas de envío.
"""

# --- NUEVO: Grafo de adyacencia de comunas basado en el mapa ---
# Define qué comunas son vecinas directas de otras.
COMUNA_ADJACENCY = {
    1: [9, 3],
    2: [3],
    3: [1, 2, 4, 9],
    4: [3, 5, 8],
    5: [4, 6, 7, 8],
    6: [5, 7],
    7: [5, 6, 8],
    8: [4, 5, 7, 9],
    9: [1, 3, 8],
}

BARRIOS_POR_COMUNA = {
    1: [
        "Alcalá", "Antonio Nariño", "Belalcázar", "Bloques de Pubenza", "Campamento", 
        "Campo Bello", "Casas Fiscales", "Catay (Pubenza)", "Ciudad Capri", "El Recuerdo", 
        "El Recuerdo I", "Fancal", "La Cabaña", "La Playa", "La Villa", "Loma Linda", 
        "Los Laureles", "Los Rosales", "Machangara", "Modelo", "Monte Rosales", "Navarra", 
        "Nueva Granada (Champagnat)", "Prados del Norte", "Puerta de Hierro", 
        "Puerta del Sol", "Santa Clara", "Villa Paola"
    ],
    2: [
        "Álamos del Norte", "Alcázares de Pino Pardo", "Atardeceres de la Pradera", 
        "Balcón Norte", "Bella Vista", "Bello Horizonte", "Bosques del Pinar", 
        "Bosques de Morinda", "Canterbury", "Capri", "Capri del Norte", "Chamizal", 
        "Cordillera", "Cruz Roja", "Destechados del Norte", "Divino Niño", "El Bambú", 
        "El Encanto", "El Placer", "El Pinar", "El Tablazo", "El Uvo", "Galilea", 
        "Gran Bretaña", "Guayacanes del Río", "La Aldea", "La Arboleda", "La Esperanza", 
        "La Florida", "La Primavera", "Los Ángeles", "Los Cámbulos", "Luna Blanca", 
        "María Paz", "Matamoros", "Minuto de Dios", "Morinda", "Nueva Alianza", 
        "Nuevo Tequendama", "Pinares Canal de Brujas", "Pinares del Río", "Pino Pardo", 
        "Pinos Llano", "Quintas de José Miguel", "Renacer", "Rincón de Comfacauca", 
        "Rincón de la Aldea", "Rinconcito Primaveral", "Río Vista", "San Fernando", 
        "San Gerardo", "San Ignacio", "Santiago de Cali", "Santiago de Cali II", "Tóez", 
        "Trece de Octubre", "Vereda González", "Villa Claudia", "Villa del Norte", 
        "Villa del Viento", "Villa Diana", "Villa Melisa", "Zuldemaida"
    ],
    3: [
        "Acacias", "Aida Lucía", "Alicante", "Altos del Río", "Arcos de Yanaconas", 
        "Bolívar", "Chicalá", "Ciudad Jardín", "Deportistas", "Galicia", "Guayacanes", 
        "José Antonio Galán", "La Estancia", "La Floresta", "La Virginia", "La Ximena", 
        "Los Hoyos", "Molinos de la Estancia", "Moravia", "Nuevo Yambitará", "Palacé", 
        "Periodistas", "Poblado de San Esteban", "Poblados de San Miguel", 
        "Portal de la Vega", "Portales del Norte", "Portón de Palacé", "Pueblillo", 
        "Recodo del Río", "Rincón de la Estancia", "Rincón de la Ximena", 
        "Rincón del Río", "Rincón de Yambitará", "Sotará", "Torres del Río", "Ucrania", 
        "Urbanización Yanaconas", "Vega de Prieto", "Villa Alicia", "Villa Mercedes", 
        "Yambitará", "Yanaconas"
    ],
    4: [
        "Achiral", "Alameda", "Argentina", "Belén", "Berlín", "Bosques de Pomona", 
        "Cadillal", "Caldas", "Centro", "Colombia I Etapa", "El Empedrado", "El Prado", 
        "El Refugio", "Fucha", "Fundecur", "Hernando Lora", "La Pamba", "Las Américas", 
        "Las Ferias", "Liceo", "Loma de Cartagena", "Los Álamos", "Moscopán", "Obrero", 
        "Pomona", "Portal de Pomona", "Provitec II Etapa", "San Camilo", "San Rafael", 
        "Santa Catalina", "Santa Inés", "Santa Teresita", "Siglo XX", "Valencia", 
        "Vásquez Cobo"
    ],
    5: [
        "Alfonso López", "Calicanto", "Camino Real", "Colina", "Colinas de Calicanto", 
        "El Boquerón", "El Deán", "El Limonar", "El Recuerdo", "Gabriel García Márquez", 
        "Jorge Eliécer Gaitán", "José Hilario López", "La Gran Victoria", "La Ladera", 
        "La Paz Sur", "Loma de la Virgen", "Los Comuneros", "Nueva Frontera", 
        "Nueva Granada", "Nuevo Deán", "Nuevo Japón", "Nuevo País", "Pajonal", 
        "Palermo", "Primero de Mayo", "Samuel Silverio", "San José de los Tejares", 
        "San Rafael", "Santa Fe", "Santa Rita", "Sindical II", "Tejares de Otón", 
        "Valparaíso", "Veraneras", "Versalles II", "Villa del Carmen", "Villa del Sur", 
        "Villa Hermosa", "Villareal"
    ],
    6: [
        "Alfonso López", "Calicanto", "Campos", "Chapinero", "Colombia II Etapa", "Corsocial", 
        "El Mirador", "Independencia", "La Campiña", "La Conquista", "La Heroica", 
        "La Libertad", "La Unión", "Las Brisas", "Las Palmas I y II", "Las Vegas", 
        "Los Álamos de Occidente", "Múnich", "Nazaret", "Nuevo Hogar", "Nuevo Milenio", 
        "Nuevo Popayán", "Panamericano", "Retiro Alto", "Santa Librada", 
        "Santo Domingo Sabio I y II", "Solidaridad", "Tomas Cipriano de Mosquera", 
        "Treinta y Uno de Marzo", "Villa del Carmen", "Villa España", "Villa Occidente", 
        "Villas del Palmar"
    ],
    7: [
        "Chapinero", "Colombia II Etapa", "Corsocial", "El Mirador", "Independencia", 
        "La Conquista", "La Heroica", "La Libertad", "La Unión", "Las Brisas", 
        "Las Palmas I y II", "Las Vegas", "Nazaret", "Nuevo Hogar", "Nuevo Popayán", 
        "Retiro Alto", "Santa Librada", "Solidaridad", "Tomas Cipriano de Mosquera", 
        "Treinta y Uno de Marzo", "Villa del Carmen"
    ],
    8: [
        "Camilo Torres", "Canadá", "El Triunfo", "Esperanza Sur", "Esmeralda", 
        "Guayabal", "Isla", "Isla II", "José María Obando", "Junín", "Junín II Etapa", 
        "La Isla", "Libertador", "Llano Largo", "Minuto de Dios", "Pandiguando", 
        "Perpetuo Socorro", "Popular", "Santa Elena"
    ],
    9: [
        "Carlos Primero", "Cinco de Abril", "Kennedy", "La Capitana", "Lomas de Granada", 
        "Los Naranjos", "María Occidente", "Mis Ranchitos", "Nuevo Hogar", 
        "San Antonio de Padua", "San José", "La Sombrilla"
    ]
}

LISTA_DE_BARRIOS = sorted(list(set(barrio for comuna_barrios in BARRIOS_POR_COMUNA.values() for barrio in comuna_barrios)))

BARRIO_A_COMUNA = {
    barrio: comuna 
    for comuna, barrios in BARRIOS_POR_COMUNA.items() 
    for barrio in barrios
}