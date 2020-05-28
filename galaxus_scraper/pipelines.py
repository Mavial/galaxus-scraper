# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from bs4 import BeautifulSoup
from urllib.parse import urlparse
import yaml

import sqlite3


class GalaxusScraperPipeline:
    # NOTE: The goal is to compress all important data from the products article page into a single json.
    #       Some of the data needs to be gathered from different tags, through different methods which are found in the functions below.
    #       Thankfully a lot of the data is stored in a yaml string probably used for ad-tracking and cookies.
    #       Finally the actual discount is calculated manually.

    def process_item(self, item, spider):
        soup = BeautifulSoup(item['response'].text, 'lxml')
        article_list = soup.find_all('article', class_='panel product')

        product_list = []
        for article in article_list:
            product_yaml = self._get_product_yaml(article)
            product = {
                'id': product_yaml['id'],
                'name': product_yaml['name'],
                'img_url': self._get_image(article),
                'discount_price': self._get_discount_price(article),
                'regular_price': float(product_yaml['price']),
                'type': self._get_tag(article),
                'category': self._get_type(article),
                'url': self._get_url(item['response'], article),
            }

            # these should be a function just for cleanliness
            try:
                product['brand'] = product_yaml['brand']
            except KeyError:
                product['brand'] = "N/A"

            product['discount'] = round(
                (1-(product['discount_price']/product['regular_price'])), 4)
            product_list.append(product)

        return product_list

    def _get_product_yaml(self, article):
        product_str = article.find('a', class_='product-overlay')['onclick'].replace(
            'dataLayer.push(', '')[:-2].replace('\n', '').replace('\r', '')
        try:
            product_yaml = yaml.load(product_str, Loader=yaml.FullLoader)[
                'ecommerce']['click']['products'][0]
            return product_yaml
        except yaml.parser.ParserError as e:
            if e.problem == "expected ',' or '}', but got '<scalar>'":
                # NOTE: A rogue asterisk has possibly made its way into the yaml file, breaking it.
                #       Seing as they are usually prefixed with a '//', so that's what I'm looking for to remove them.

                product_str = product_str.replace("\\'", "")
            else:
                # I have no fucking clue what this is supposed to fix but it seems to work so imma leave it here for the moment.
                get_num = 0
                for word in str(e).split():
                    if get_num == 2:
                        word = word[:-1]
                        char_index = int(word)
                        break
                    elif word == 'column':
                        get_num += 1

                product_str_list = list(product_str)
                product_str_list[char_index-2] = ''
                product_str = ''.join(product_str_list)

            product_yaml = yaml.load(product_str, Loader=yaml.FullLoader)[
                'ecommerce']['click']['products'][0]
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
        # type_url = urlparse(self.response.url).netloc + type_tag['href']
        product_type = type_tag.text.replace('\n', '').replace('\r', '')
        return product_type  # , type_url]

    def _get_url(self, response, article):
        return urlparse(response.url).netloc + article.find('a', class_='product-overlay')['href']


class SQLitePipeline(object):
    # NOTE: This pipeline takes the json list created by GalaxusScraperPipeline and commits them to articles.db
    # TODO:
    #   - delete rows containing articles that have been taken down from the site
    #   - update rows with articles that have been added contain changed data
    #   - a secondary tables to the database to track price changes
    def __init__(self):
        self.sqlite_db = 'articles.db'
        # self.sqlite_db = sqlite_db
        # self.sqlite_coll = sqlite_coll

    # @classmethod
    # def from_crawler(cls, crawler):
    #     return cls(

    #     )

    def open_spider(self, spider):
        try:
            self.conn = sqlite3.connect(self.sqlite_db)
            self.c = self.conn.cursor()
            self.c.execute(
                '''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='article_offers';''')
            if self.c.fetchone()[0] == 0:
                self.c.execute('''CREATE TABLE article_offers (id INTEGER NOT NULL PRIMARY KEY, name TEXT, brand TEXT, url TEXT, img_url TEXT, discount_price REAL, regular_price REAL, discount REAL, category TEXT, type TEXT)''')
        except Exception as e:
            print('There has been an exception while starting the SQLite Pipeline ' + e)

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()

    def process_item(self, item, spider):
        for product in item:
            try:
                sql_query = f'''INSERT INTO article_offers VALUES ('{product['id']}', '{product['name']}', '{product['brand']}', '{product['url']}', '{product['img_url']}', '{product['discount_price']}', '{product['regular_price']}', '{product['discount']}', '{product['category']}', '{product['type']}')'''
                self.c.execute(sql_query)
            except sqlite3.IntegrityError:
                print(
                    product['name'] + ' is already present in the database, adjusting values.')
                # Here is where I adjust the values. cba rn.
            except Exception as e:
                print('An SQLLite Pipeline has caused an exception: ' + e)
