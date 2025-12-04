import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia Haversine (en kilómetros) entre dos puntos
    dados por su latitud y longitud.
    """
    R = 6371  # Radio de la Tierra en kilómetros

    # Convertir grados a radianes
    lat1_rad = math.radians(float(lat1))
    lon1_rad = math.radians(float(lon1))
    lat2_rad = math.radians(float(lat2))
    lon2_rad = math.radians(float(lon2))

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # Aplicar la fórmula de Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return round(distance, 1) # Retorna la distancia en KM (redondeada a 1 decimal)