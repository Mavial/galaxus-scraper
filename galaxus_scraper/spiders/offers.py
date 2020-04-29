import scrapy
from pprint import pprint

from galaxus_scraper.data_handler import DataHandler


class OffersSpider(scrapy.Spider):
    name = 'offers'

    start_urls = [
        f'https://www.galaxus.de/de/secondhand?so=16&take=20000',
    ]

    def parse(self, response):

        data_handler = DataHandler(response, self.settings)

        product_list = data_handler.get_products()

        pprint(product_list)
        pprint(len(product_list))