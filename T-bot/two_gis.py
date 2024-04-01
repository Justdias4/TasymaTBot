import requests

url = "https://catalog.api.2gis.com/3.0/items/geocode?"
token = "d73c1925-eec6-4694-96c2-2bb2f54fcfc0"
url_routing = f"https://routing.api.2gis.com/get_dist_matrix?key={token}&version=2.0"
headers = {
    "Content-Type": "application/json"
}

def get_distances(points, sources, targets):
    data = {
        "points": points,
        "mode": "truck",
        "sources": sources,
        "targets": targets
    }
    res = requests.post(url_routing, headers=headers, json=data)
    print(res.json())





def get_point(address):
    params = {
        'q': address,
        'fields': 'items.point',
        'key': token
    }
    res = requests.get(url, headers=headers, params=params)
    data = res.json()
    if data['result']['total'] > 0:
        item = data['result']['items'][0]
        return item['point']['lat'], item['point']['lon']
    else:
        return None
        # for item in items:
        #     item['address_name']
        #     print("Latitude:", item['point']['lat'])
        #     print("Longitude:", item['point']['lon'])

# print(get_point("Алматы, Килыбай Медеубекова улица, 11")) # lat  43.185079, lon 76.789317
# print()
# get_distances([{"lat": 43.2922251, "lon": 76.8497949},{"lat": 43.2103373, "lon": 76.9079463}, {"lat": 43.185079, "lon": 76.789317}], [0,1], [2])