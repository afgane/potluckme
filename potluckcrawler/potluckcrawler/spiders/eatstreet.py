import scrapy
import json
import os


class EatStreetSpider(scrapy.Spider):
    name = 'eatstreet'
    API_KEY = os.environ.get('EATSTREET_API_KEY')
    AUTH_HEADERS = { 'X-Access-Token' : API_KEY }

    def start_requests(self):
        urls = [
            'https://api.eatstreet.com/publicapi/v1/restaurant/search?method=both&pickup-radius=50&street-address=Baltimore,+MD',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=EatStreetSpider.AUTH_HEADERS)

    def parse(self, response):
        json_restaurants = json.loads(response.body_as_unicode())
        
        for restaurant in  json_restaurants['restaurants']:
            restaurant_id = restaurant['apiKey']
            url = f'https://api.eatstreet.com/publicapi/v1/restaurant/{restaurant_id}/menu'
            yield scrapy.Request(url=url, callback=self.parse_menu, headers=EatStreetSpider.AUTH_HEADERS)
        
    def parse_menu(self, response):
        json_menus = json.loads(response.body_as_unicode())
        
        for menu in  json_menus:
            print(menu['name'])
            print("---------------------------")