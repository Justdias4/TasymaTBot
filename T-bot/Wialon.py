import requests

host = "hst-api.wialon.com"
url = "https://"+host+"/wialon/ajax.html?"
token = "268dc682b3aa5ad7699e7ccd3662596d201930970B8213BE6642200EE9722725BB3EE7F8"
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}
global sid
sid = None

def login():
    data = {
        'svc': 'token/login',
        "params": {
            "token": token
        }
    }
    params = "svc=token/login&params={\"token\":\""+token+"\"}"
    # encoded_data = encode(data)
    res = requests.post(url, params=params, headers=headers)
    data = res.json()
    if 'eid' in data:
        global sid
        sid = data['eid']
        print(sid)
    print("logged )")




def get_active_units():
    params = "sid="+sid+"&svc=core/search_items&params={\"spec\":{\"itemsType\":\"avl_unit\",\"propName\":\"*\",\"propValueMask\":\"*\",\"sortType\":\"sys_name\"},\"force\":1,\"flags\":1025,\"from\":0,\"to\":0}"
    # para = `"sid"=`
    res = requests.post(url, params=params, headers=headers)
    # print(res.json()['items'])
    print(res.json())
    active_transports = []

    for item in res.json()['items']:
        # print("name", item['nm'])
        # print("lat:", item['pos']['y'])
        # print("lon:", item['pos']['x'])
        if item.get("pos") and item.get('lmsg') and item['lmsg'].get('p') and item['lmsg']['p'].get('status') == "available":
            # Extract required information
            item_name = item['nm']
            if item.get('pos'):
                lat = item['pos']['y']
                lon = item['pos']['x']
            # Append to selected items list
            status = item['lmsg']['p'].get('status')
            # tracker = item['lmsg']['p'].get('s_on')
            active_transports.append({'name': item_name, 'status':status, 'lat': lat, 'lon': lon})

    return active_transports


def avl_resources():
    params = "sid="+sid+"&svc=core/search_items&params={\"spec\":{\"itemsType\":\"avl_resource\",\"propName\":\"*\",\"propValueMask\":\"*\",\"sortType\":\"sys_name\"},\"force\":1,\"flags\":4096,\"from\":0,\"to\":0}"
    res = requests.post(url, params=params, headers=headers)
    # print(res.json())
    coordinates = []
    for item in res.json()['items']:
        geo = item['zl']['1']
        # print("name:", geo['n'])
        # print("geoid:", geo['id'])
        lon = geo['b']['cen_x'] if geo['t'] == 2 else 0
        lat = geo['b']['cen_y'] if geo['t'] == 2 else 0
        coor = {"name": geo['n'], "geoid": geo['id'], "lon" : lon, "lat" : lat }
        coordinates.append(coor)

    return coordinates

login()
# avl_resources()
#
# print(sid)
#
# print("Active transports: ", get_active_units())
print("Post : ", avl_resources())
# providers = avl_resources()# key:value   name, geoid, lon, lat
# provider_name = ""
# for provider in providers:
#     provider_name = provider.get("name")
# print(provider_name)
    #kak to tekseru kerek osy marka barma



