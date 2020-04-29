import scrapy
from pprint import pprint

from galaxus_scraper.data_handler import DataHandler


class OffersSpider(scrapy.Spider):
    name = 'offers'

    # TODO Get product count and set value to 'take' before scraping
    product_count = 768

    start_urls = [
        f'https://www.galaxus.de/de/secondhand?so=16&take={product_count}',
    ]

    def parse(self, response):

        data_handler = DataHandler(response, self.settings)

        product_list = data_handler.get_products()

        pprint(product_list)
