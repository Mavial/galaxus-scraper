import galaxus_scraper
import scrapy

from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def main():
    process = CrawlerProcess(get_project_settings())
    process.crawl(galaxus_scraper.OffersSpider)
    process.start()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)