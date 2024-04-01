from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = 6371 * c  # Radius of Earth in kilometers
    return distance


def find_nearest_point(target_lat, target_lon, points):
    """
    Find the nearest point to the target latitude and longitude
    from a list of points, where each point is represented as
    a tuple (lat, lon).
    """
    nearest_point = None
    min_distance = float('inf')

    for point in points:
        distance = haversine(target_lat, target_lon, point[0], point[1])
        if distance < min_distance:
            min_distance = distance
            nearest_point = point

    return nearest_point, min_distance


# Example usage:
target_lat = 43.1851576373  # Target latitude
target_lon = 76.7896189818  # Target longitude
points = [(43.210341, 76.907959), (40.7128, -74.0060)]  # List of points
nearest_point, min_distance = find_nearest_point(target_lat, target_lon, points)
print("Nearest point/unit:", nearest_point)
print("Distance to geofence:", min_distance, "km")
poi_lat = 43.230334161749184
poi_lon = 76.86763391908673
path = haversine(target_lat, target_lon, poi_lat, poi_lon)
print("Distance from geofence to POI:", path)
print("Total distance for unit :", min_distance + path)
