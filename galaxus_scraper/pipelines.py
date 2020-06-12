# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime
import yaml
import logging

import MySQLdb
import sqlite3


class GalaxusScraperPipeline:
    # TMFS: The goal is to compress all important data from the products article page into a single json.
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


class SQLPipeline(object):
    # TMFS: This pipeline takes the json list created by GalaxusScraperPipeline and commits them to articles.db
    # TODO:
    #   - delete rows containing articles that have been taken down from the site
    #   - update rows with articles that have been added contain changed data
    #   - add secondary tables to the database to track price changes
    def __init__(self, settings):
        self.logger = logging.getLogger(__name__)
        self.DB_TYPE = settings.get('DB_TYPE')
        self.SQLITE_FILE = settings.get('SQLITE_FILE')
        self.MYSQL_URL = settings.get('MYSQL_URL')
        self.MYSQL_DB = settings.get('MYSQL_DB')
        self.MYSQL_USER = settings.get('MYSQL_USER')
        self.MYSQL_PASSWORD = settings.get('MYSQL_PASSWORD')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            settings=crawler.settings,
        )

    def open_spider(self, spider):

        # TMFS: I'm trying to allow different SQL db types because I'm a nice guy. Thus below there are different connection methods.
        #       The end result is a cursor at self.c that should work the same for all databases.
        #       Currently its just SQLite and MySQL but maybe if I feel like it, just because im that cool of a person I'll add some more. I don't see a reason why though..

        if self.DB_TYPE == 'sqlite':

            # NOTE: This is close to fucking hardcoding, I should not have duplicate code but someone else fix it thanks.

            try:
                self.conn = sqlite3.connect(self.SQLITE_FILE)
                self.c = self.conn.cursor()
                self.c.execute(
                    '''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='article_offers';''')
                if self.c.fetchone()[0] == 0:
                    self.c.execute(
                        '''CREATE TABLE article_offers (id INTEGER NOT NULL PRIMARY KEY, name TEXT, brand TEXT, url TEXT,
                            img_url TEXT, discount_price REAL, regular_price REAL, discount REAL, category TEXT, type TEXT, lastModified DATETIME, addedAt DATETIME)''')
            except Exception as e:
                self.logger.error(
                    'There has been an exception while starting the SQLite Pipeline: ' + e)
        elif self.DB_TYPE == 'mysql':

            # NOTE: This isn't working yet, the current problem is checking if a db table is present and create it if not. Its 4am. Gn

            try:
                self.conn = MySQLdb.connect(
                    self.MYSQL_URL, self.MYSQL_USER, self.MYSQL_PASSWORD, self.MYSQL_DB)
                self.c = self.conn.cursor()
                self.c.execute(
                    '''CREATE TABLE article_offers (id INTEGER NOT NULL PRIMARY KEY, name TEXT, brand TEXT, url TEXT,
                            img_url TEXT, discount_price REAL, regular_price REAL, discount REAL, category TEXT, type TEXT, lastModified DATETIME, addedAt DATETIME)''')
            except Exception as e:
                if e.args[0] != 1050:
                    self.logger.critical(
                        'There has been an exception while connecting to the MySQL Database: ' + e.args[0])
                        # quit()

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()

    def process_item(self, item, spider):
        now = datetime.now()
        for product in item:
            try:
                sql_query = f'''INSERT INTO article_offers VALUES ('{product['id']}', '{product['name']}', '{product['brand']}', '{product['url']}', '{product['img_url']}',
                    '{product['discount_price']}', '{product['regular_price']}', '{product['discount']}', '{product['category']}', '{product['type']}', '{now}', '{now}')'''
                self.c.execute(sql_query)
            except sqlite3.IntegrityError:
                self.logger.debug(product['id'] + ' ' + product['name'] +
                                 ' is already present in the database, adjusting values.')
                # Here is where I adjust the values. cba rn.
            except Exception as e:
                if e.args[0] == 1062:
                    self.logger.debug(product['id'] + ' ' + product['name'] +
                                     ' is already present in the database, adjusting values.')
                    # Here is where I adjust the values. cba rn.
                else:
                    self.logger.warning(e)
