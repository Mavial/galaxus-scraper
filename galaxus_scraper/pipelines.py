# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3

class GalaxusScraperPipeline:
    def process_item(self, item, spider):
        return item


class SQLitePipeline(object):
    def __init__(self):
        self.sqlite_db = 'articles.db'
        # self.sqlite_url =sqlite_url
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
            self.c.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='article_offers';''')
            if self.c.fetchone()[0] == 0:
                self.c.execute('''CREATE TABLE article_offers (name text, brand text, url text, img_url text, discount_price real, regular_price real, discount real, type text, category text)''')
        except Exception as e:
            print(e)

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()

    def process_item(self, item, spider):
        try:
            sql_query = f'''INSERT INTO article_offers VALUES ('{item['name']}', '{item['brand']}', '{item['url']}', '{item['img_url']}', '{item['discount_price']}', '{item['regular_price']}', '{item['discount']}', '{item['type']}', '{item['category']}')'''
            self.c.execute(sql_query)
        except Exception as e:
            print(e)