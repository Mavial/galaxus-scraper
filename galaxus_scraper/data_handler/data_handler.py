# galaxus_scraper/data_handler/data_handler.py

import scrapy
from bs4 import BeautifulSoup

from urllib.parse import urlparse
import yaml

class DataHandler(object):
    def __init__(self, response, settings):
        self.response = response
        self.settings = settings

    def get_products(self):
        soup = BeautifulSoup(self.response.text, 'lxml')
        article_list = soup.find_all('article', class_='panel product')

        product_list = []
        for article in article_list:
            product_yaml = self._get_product_yaml(article)

            product = {
                'name': product_yaml['name'],
                'img_url': self._get_image(article),
                'discount_price': self._get_discount_price(article),
                'regular_price': float(product_yaml['price']),
                'tags': self._get_tag(article),
                'type': self._get_type(article),
                'url': self._get_url(article),
            }

            try:
                product['brand'] = product_yaml['brand']
            except KeyError:
                product['brand'] = "N/A"

            product['discount'] = str(round((1-(product['discount_price']/product['regular_price']))*100, 2)) + ' %'
            product_list.append(product)
        return product_list

    def _get_product_yaml(self, article):
        product_str = article.find('a', class_='product-overlay')['onclick'].replace('dataLayer.push(', '')[:-2].replace('\n', '').replace('\r', '')
        try:
            product_yaml = yaml.load(product_str, Loader=yaml.FullLoader)['ecommerce']['click']['products'][0]
            return product_yaml
        except yaml.parser.ParserError as e:
            get_num = 0
            for word in str(e).split():
                if get_num == 2:
                    word = word[:-1]
                    char_index = int(word)
                    break
                elif  word == 'column':
                    get_num += 1

            product_str_list = list(product_str)
            product_str_list[char_index-2] = ''
            product_str = ''.join(product_str_list)

            product_yaml = yaml.load(product_str, Loader=yaml.FullLoader)['ecommerce']['click']['products'][0]
            return product_yaml

    # def _get_name(self, article):
    #     return article.find('h5', class_='product-name').text.replace('\n', ' ').replace('\r', '')

    def _get_image(self, article):
        return article.find('img')['data-src']

    def _get_discount_price(self, article):
        parent_tag = article.find('div', class_='product-price')
        for child in parent_tag.find_all():
            child.decompose()
        try:
            return float(parent_tag.text.replace('\n', '').replace('\r', '').replace(',', '.').replace('–', '0'))
        except ValueError:
            return 0.0

    def _get_tag(self, article):
        try:
            return article.find('div', class_='tag').text.replace('\n', '').replace('\r', '')
        except AttributeError:
            return None

    def _get_type(self, article):
        type_tag = article.find('span', class_='product-type').find('a')
        type_url = urlparse(self.response.url).netloc + type_tag['href']
        product_type = type_tag.text.replace('\n', '').replace('\r', '')
        return [product_type, type_url]

    def _get_url(self, article):
        return urlparse(self.response.url).netloc + article.find('a', class_='product-overlay')['href']
