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
            conn = sqlite3.connect(self.sqlite_db)
            self.cursor = conn.cursor()
            print(self.cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='dsct_articles';'''))
        except Exception as e:
            print(e)

