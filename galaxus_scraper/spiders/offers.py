import scrapy
import logging


class OffersSpider(scrapy.Spider):
    name = 'offers'

    def __init__(self, settings, *args, **kwargs):
        super(OffersSpider, self).__init__(*args, **kwargs)
        self.settings = settings

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        return cls(
            settings=crawler.settings,
            crawler=crawler
        )

    # the 'take=' needs to be set dynamically to the amount of articles currently on offer.
    start_urls = [
        f'https://www.galaxus.de/de/secondhand?so=16&take=1000',
    ]

    def parse(self, response):
        return {'response': response, }
