"Create web-map with locations of films"


import argparse
import os
import sys
import math
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

parser = argparse.ArgumentParser(description='get location and path to dataset')
parser.add_argument('year', type=int, help='film year')
parser.add_argument('latitude', type=float, help='your latitude')
parser.add_argument('longtitude', type=float, help='your longtitude')
parser.add_argument('path_to_dataset', type=str, help='paht to dataset')

args = parser.parse_args()
year = args.year
lat = args.latitude
lon = args.longtitude
path = args.path_to_dataset

if not os.path.exists(path) or not os.path.isfile(path):
    print('Error: The file specified does not exist')
    sys.exit()


def hover_form(lat1, lon1, lat2, lon2):
    """
    Return distance.
    (float) -> float
    >>> print(hover_form(33.3697, -106.3477, -4.1122, -63.9844))
    5928.850286041364
    """
    sinus = (math.sin(math.radians(lat2)-math.radians(lat1))/2)**2
    cosinus = math.cos(math.radians(lat1))*math.cos(math.radians(lat2))
    sinus2 = (math.sin((math.radians(lon2)-math.radians(lon1))/2))**2
    summa = (sinus+cosinus*sinus2)**(1/2)
    dist = 2*6371*math.asin(summa)
    return dist


def get_info(path, lat, lon, year):
    """
    (str, float, float) -> list
    Return list of films with coordinates with
    appropriate distance from specific place.
    """
    with open(path, 'r') as file:
        lst = []
        for line in file:
            if str(year) in line and '(' in line:
                if '{' in line:
                    line = line[:line.index('{')] + line[line.index('}')-1:]
                line = line.replace(')', '(').strip().split('(')
                line[0], line[2] = line[0].strip(), line[2].strip()
                line = line[:3]
                geolocator = Nominatim(user_agent="main.py")
                geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.000014)
                location = geolocator.geocode(line[2])
                if location != None:
                    lt = location.latitude
                    lng = location.longitude

                    dist = hover_form(lt, lng, lat, lon)
                    if dist <= 1000:
                        lst.append(line+[lt, lng])
                    if len(lst) == 10:
                        break
    return lst


def layers_add(lst):
    """
    Add layers to map and save it as html-file.
    """
    map =  folium.Map(location=[lat, lon], zoom_start = 10)
    fg1 = folium.FeatureGroup(name="Films")
    for info in lst:
        fg1.add_child(folium.Marker(location=[info[3], info[4]],
                                    radius=10,
                                    popup='<b>'+info[0]+'</b>'+"\n" + info[1],
                                    fill_opacity=0.5,
                                    icon=folium.Icon(color="darkred", icon="film")))

    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>\
              contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        name='darkmatter',
        control=False,
        opacity=0.3,
        max_zoom=15
    ).add_to(map)

    map.add_child(fg1)
    map.add_child(folium.LatLngPopup())
    map.save('film_map.html')


layers_add(get_info(path, lat, lon, year))
