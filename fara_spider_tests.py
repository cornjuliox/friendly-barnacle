import unittest
import os
import json

from scrapy.http import HtmlResponse, Request
from scrapy import Item
from trial_govpredict_2.spiders.fara_spider import FaraSpiderSpider


class FaraSpiderTest(unittest.TestCase):

    def fake_response(self, file_name, url=None, rq_meta=None):
        if not url:
            url = 'http://www.google.com'

        request = Request(url=url, meta=rq_meta)
        if not file_name[0] == '/':
            responses_dir = os.path.dirname(os.path.realpath(__file__))
            file_path = os.path.join(responses_dir, file_name)
        else:
            file_path = file_name

        with open(file_path, 'rb') as F:
            file_content = F.read()

        response = HtmlResponse(
            url=url,
            request=request,
            body=file_content,
            encoding='utf-8'
        )

        return response

    def setUp(self):
        self.spider = FaraSpiderSpider()

    def test_01_parse_method(self):
        print('testing parse() method')
        target_url = 'https://efile.fara.gov/pls/apex/f?p=171:1'
        result = self.spider.parse(
            self.fake_response('testfiles/sample1.html')
        )
        self.assertEqual(result.url, target_url)

    def test_02_parse_active_principals_method(self):
        print('testing parse_active_principals() method')
        target = (
            'https://efile.fara.gov/pls/apex/' +
            'f?p=171:130:0::NO:RP,130:P130_DATERANGE:N'
        )
        result = self.spider.parse_active_principals(
            self.fake_response(
                'testfiles/sample2.html',
                'https://efile.fara.gov/pls/apex/f')
            )
        self.assertEqual(result.url, target)

    def test_03_parse_paginate(self):
        print('testing parse_results_page() method')
        results = [x for x in self.spider.parse_paginate(
            self.fake_response('testfiles/sample3.html')
        )]

        total_results = 541
        per_page = 15
        total_requests = int(total_results / per_page) + 1

        self.assertEqual(len(results), total_requests)

    def test_03a_parse_results_page_method(self):
        print('testing parse_results_page() method for item')
        results = [x for x in self.spider.parse_results_page(
            self.fake_response('testfiles/sample3.html')
        )]
        self.assertTrue(results[0].meta.get('data'))

    def test_04_parse_exhibit_url_method(self):
        print('testing parse_exhibit_url() method')
        url = (
            'https://efile.fara.gov/pls/apex/f?p=171:200:0::NO:' +
            'RP,200:P200_REG_NUMBER,P200_DOC_TYPE' +
            ',P200_COUNTRY:6399,Exhibit%20AB,AFGHANISTAN'
        )

        fake_item = {
            'address': 'House #3 MRRD Road Darul Aman Kabul',
            'date': '2014-05-05T00:00:00',
            'foreign_principal': 'Test Test One',
            'ref_num': '5555',
            'registrant': 'test registrant',
            'state': 'CA',
            'url': url
        }

        response = self.fake_response(
            'testfiles/sample3.html',
            url,
            rq_meta={
                'data': fake_item
            }
        )
        result = self.spider.parse_exhibit_url(response)

        self.assertEqual(result['country'], 'AFGHANISTAN')
        self.assertEqual(result['url'], url)
        self.assertIsInstance(result, Item)

    def test_05_validate_exhibit_urls(self):
        with open('sample_fara_spider_principals.json', 'r') as F:
            items = F.readlines()

        for item in items:
            d_item = json.loads(item)
            ref_num = d_item.get('ref_num')
            exhibit_url = d_item.get('exhibit_url')
            main_url = d_item.get('url')

            if exhibit_url:
                self.assertIn(ref_num, exhibit_url)

            self.assertIn(ref_num, main_url)


if __name__ == '__main__':
    unittest.main()
