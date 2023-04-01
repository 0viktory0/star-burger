import requests

from django.conf import settings
from django.utils import timezone
from geoapp.models import Place


def fetch_coordinates(address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": settings.YANDEX_API_KEY,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def get_place_coordinates(places, address):
    place = [place for place in places if place.address == address]
    if not place:
        try:
            coords = fetch_coordinates(address)
            lat, lon = coords
            place = Place.objects.create(
                address=address,
                lat=lat,
                lon=lon,
                request_date=timezone.now(),
            )
        except (requests.exceptions.HTTPError, KeyError) as error:
            pass
    else:
        place = place[0]
    return place.lat, place.lon
