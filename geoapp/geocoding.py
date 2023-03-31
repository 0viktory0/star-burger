from django.utils import timezone
from geoapp.models import Place

from restaurateur.views import fetch_coordinates


def get_place_coordinates(places, address):
    place = [place for place in places if place.address == address]
    if not place:
        coords = fetch_coordinates(address)
        if not coords:
            return None
        lat, lon = coords
        place = Place.objects.create(
            address=address,
            lat=lat,
            lon=lon,
            request_date=timezone.now(),
        )
    else:
        place = place[0]
    return place.lat, place.lon
