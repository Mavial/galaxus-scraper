import scrapy
import logging
from pprint import pprint

from galaxus_scraper.data_handler import DataHandler


class OffersSpider(scrapy.Spider):
    name = 'offers'

    def __init__(self, settings, *args, **kwargs):
        super(OffersSpider, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        # self.logger.basicConfig(level=logging.INFO)
        self.settings = settings

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        return cls(
            settings = crawler.settings,
            crawler = crawler
        )

    start_urls = [
        f'https://www.galaxus.de/de/secondhand?so=16&take=2000',
    ]

    def parse(self, response):

        data_handler = DataHandler(response, self.settings)

        product_list = data_handler.get_products()

        # pprint(product_list)
        # pprint(len(product_list))
        return product_list