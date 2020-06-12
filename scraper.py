import logging
import scrapy
import galaxus_scraper

from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess

import env_file


def main():
    env_file.load()
    process = CrawlerProcess(get_project_settings())
    process.crawl(galaxus_scraper.OffersSpider)
    process.start()


if __name__ == '__main__':
    try:
        galaxus_scraper.InitLogging()
        logger = logging.getLogger(__name__)

        main()
    except Exception as e:
        print(e)