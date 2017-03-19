"""
Interact with Zomato API to retrieve available info about restaurants.

Before using, export env car ZOMATO_API_KEY with your API key for the service.

Simplest usage is to just call `fetch_and_store_restaurant_info` method,
which will fetch info about restaurants for the supplied city and store it in
a file.
"""
import json
import os
from urllib import parse

import requests

API_KEY = os.environ.get('ZOMATO_API_KEY')
URL_BASE = "https://developers.zomato.com/api/v2.1/"


def _get_request(endpoint, payload):
    """
    Issue a GET request for the specified endpoint using the supplied payload.

    The request header will be amended with the API_KEY using `user-key` key.
    """
    headers = {'user-key': API_KEY}
    return requests.get(endpoint, headers=headers, params=payload)


def get_city_id(city_name=None, lat=None, lon=None):
    """
    Try to get the Zomato city ID given it's name and/or location.

    TODO: This call is likely to return multiple results.

    Baltimore ID: 787
    """
    payload = {'query': city_name, 'lat': lat, 'lon': lon}
    endpoint = parse.urljoin(URL_BASE, 'locations')
    r = _get_request(endpoint, payload)
    return r.json().get('location_suggestions')[0]['city_id']


def get_restaurants(city_id):
    """
    Query the API and retrieve restaurant info for the given city.

    The API does not return any results after the first 100 restaurants!
    http://stackoverflow.com/questions/42013020/zomato-api-always-returning-only-20-restaurants-in-search-by-location-response
    """
    # category IDs: 1-Delivery; 2-Dine-out; 3-Nightlife
    payload = {'entity_id': city_id, 'entity_type': 'city', 'category': 2}
    endpoint = parse.urljoin(URL_BASE, 'search')
    # Send off the first request to fetch the number of results
    r = _get_request(endpoint, payload)
    results = [r]
    restaurants = r.json().get('restaurants')
    results_shown = r.json().get('results_shown', 0)
    # results_found = r.json().get('results_found', 0)
    # for i in range(results_shown, results_found, 20):  # Rate limit is 20
    for i in range(results_shown, 100, 20):  # API limited to 100 results
        print("Starting at %s" % i)
        payload['start'] = i
        r = _get_request(endpoint, payload)
        restaurants.append(r.json().get('restaurants'))
        results.append(r)
    return restaurants, results


def fetch_and_store_restaurant_info(
        city_name='Baltimore', filename='restaurants.json'):
    """Fetch info about the restaurants in a city and save it to a file."""
    city_id = get_city_id(city_name)
    restaurants, _ = get_restaurants(city_id)
    for r in restaurants:
        if isinstance(r, list):
            for rp in r:
                with open(filename, 'a') as f:
                    json.dump(rp['restaurant'], f, indent=4, sort_keys=True)
        elif r:
            with open(filename, 'a') as f:
                json.dump(r['restaurant'], f, indent=4, sort_keys=True)


def get_daily_menu(res_id):
    """
    Get the daily menu for given restaurant.

    Note that not all restaurants have a daily menu.
    """
    payload = {'res_id': res_id}
    endpoint = parse.urljoin(URL_BASE, 'dailymenu')
    r = _get_request(endpoint, payload)
    if r.ok:
        return r.json().get('daily_menu')
    return None


def check_for_daily_menus(city_name='Baltimore'):
    # def check_for_daily_menus(info_file='restaurants.json'):
    # JSONDecodeError: Extra data: line 42 column 2 (char 1847)??
    # with open(info_file, 'r') as f:
    #     restaurants_info = json.load(f)

    daily_menus = []
    city_id = get_city_id(city_name)
    restaurants, _ = get_restaurants(city_id)
    for r in restaurants:
        if isinstance(r, list):
            for rp in r:
                print("Getting daily menu for restaurant {0}".format(
                      rp['restaurant']['name']))
                dm = get_daily_menu(rp['restaurant']['R']['res_id'])
                if dm:
                    daily_menus.append(dm)
        elif r:
            print("Getting daily menu for restaurant {0}".format(
                  r['restaurant']['name']))
            dm = get_daily_menu(r['restaurant']['R']['res_id'])
            if dm:
                daily_menus.append(dm)

    return daily_menus
