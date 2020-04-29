from bs4 import BeautifulSoup
import scrapy

class OffersSpider(scrapy.Spider):
    name='offers'

    def start_requests(self):
        urls = [
            'https://www.galaxus.de/de/secondhand?so=16',
            ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        soup = BeautifulSoup(response.text, 'lxml')
        products = soup.find_all('div', class_='products-wrapper')
        # print(type(products))

        filename = f'offers-{page}.html'
        with open(filename, 'wb') as f:
            f.write(str(products).encode('utf-8'))
        self.log(f'Saved file {filename}')