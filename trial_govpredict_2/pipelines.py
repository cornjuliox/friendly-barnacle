# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import JsonLinesItemExporter
from scrapy import signals

class TrialGovpredict2Pipeline(object):

    def __init__(self):
        self.files = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        filename = '{}_principals.json'.format(spider.name)
        myfile = open(filename, 'w+b')
        self.files[spider] = myfile
        self.exporter = JsonLinesItemExporter(myfile, export_empty_fields=True)
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        myfile = self.files.pop(spider)
        myfile.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class DefaultItemPipeline(object):

    def process_item(self, item, spider):
        for x in item.fields:
            item.setdefault(x, '')

        return item
