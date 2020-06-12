import logging
import scrapy
import galaxus_scraper

from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess

import env_file


def main(settings):
    process = CrawlerProcess(settings)
    process.crawl(galaxus_scraper.OffersSpider)
    process.start()


if __name__ == '__main__':
    try:
        env_file.load()
        settings = get_project_settings()
        galaxus_scraper.InitLogging(settings['PYTHON_LOG_LEVEL'])
        logger = logging.getLogger(__name__)

        main(settings)
    except Exception as e:
        print(e)