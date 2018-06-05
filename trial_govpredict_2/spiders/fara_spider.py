# -*- coding: utf-8 -*-
from urllib.parse import urljoin
import datetime

import scrapy
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector

from trial_govpredict_2.items import FaraItemLoader


class FaraSpiderSpider(scrapy.Spider):
    name = 'fara_spider'
    start_urls = ['http://www.fara.gov/quick-search.html']

    def parse(self, response):
        iframe_url = 'https://efile.fara.gov/pls/apex/f?p=171:1'

        return Request(
            url=iframe_url,
            callback=self.parse_active_principals
        )

    def parse_active_principals(self, response):
        url_stub = response.xpath(
            '//a[contains(., "Active Foreign Principals")]//@href'
        ).extract_first()
        new_url = urljoin(response.url, url_stub)

        return Request(
            url=new_url,
            callback=self.parse_paginate
        )

    def parse_paginate(self, response):
        pagination_url = 'https://efile.fara.gov/pls/apex/wwv_flow.show'

        total_results = response.xpath(
            '//td[@class="pagination"]//span//text()'
        ).extract_first().split()[-1]
        total_results = int(total_results) + 15

        for pg in range(1, total_results, 15):
            # fill out the form
            p_instance = response.xpath(
                '//input[@name="p_instance"]//@value'
            ).extract_first()

            p_flow_id = response.xpath(
                '//input[@name="p_flow_id"]//@value'
            ).extract_first()

            p_flow_step_id = response.xpath(
                '//input[@name="p_flow_step_id"]//@value'
            ).extract_first()

            x01 = response.xpath(
                '//input[@id="apexir_WORKSHEET_ID"]//@value'
            ).extract_first()

            x02 = response.xpath(
                '//input[@id="apexir_REPORT_ID"]//@value'
            ).extract_first()

            p_widget_action_mod = (
                'pgR_min_row={}max_rows=15rows_fetched=15'.format(pg)
            )

            form_data = {}
            if response.meta.get('formdata'):
                form_data = response.meta.get('formdata')
                form_data['p_widget_action_mod'] = p_widget_action_mod
            else:
                form_data = {
                    'p_request': 'APXWGT',
                    'p_instance': p_instance,
                    'p_flow_id': p_flow_id,
                    'p_flow_step_id': p_flow_step_id,
                    'p_widget_name': 'worksheet',
                    'p_widget_mod': 'ACTION',
                    'p_widget_action': 'PAGE',
                    'p_widget_action_mod': p_widget_action_mod,
                    # apexir_WORKSHEET_ID
                    'x01': x01,
                    # apexir_REPORT_ID
                    'x02': x02
                }

            yield FormRequest(
                pagination_url,
                formdata=form_data,
                dont_filter=True,
                callback=self.parse_results_page,
                meta={
                    'formdata': form_data
                }
            )

    def parse_results_page(self, response):
        odd = '//table[@class="apexir_WORKSHEET_DATA"]//tr[@class="odd"]'
        even = '//table[@class="apexir_WORKSHEET_DATA"]//tr[@class="even"]'

        rows = response.xpath(odd) + response.xpath(even)

        for row in rows:
            data = {}
            base = './/child::td[contains(@headers, "{}")]//text()'

            # state
            state = base.format('STATE')
            data['state'] = row.xpath(state).extract_first()
            # il.add_xpath('state', state)

            # ref_num
            reg_num = base.format('REG_NUMBER')
            data['ref_num'] = row.xpath(reg_num).extract_first()
            # il.add_xpath('ref_num', reg_num)

            # address
            address = base.format('ADDRESS_1')
            data['address'] = row.xpath(address).extract_first()
            # il.add_xpath('address', address)

            # principal name
            name = base.format('FP_NAME')
            data['foreign_principal'] = row.xpath(name).extract_first()
            # il.add_xpath('foreign_principal', name)

            # registrant
            registrant = base.format('REGISTRANT_NAME')
            data['registrant'] = row.xpath(registrant).extract_first()
            # il.add_xpath('registrant', registrant)

            # url
            link = row.xpath('.//child::td/a/@href').extract_first()
            url = urljoin(response.url, link)
            data['url'] = url
            # il.add_value('url', url)

            # date
            date_path = base.format('FP_REG_DATE')
            date = row.xpath(date_path).extract_first()
            date_obj = datetime.datetime.strptime(date, '%m/%d/%Y')
            data['date'] = date_obj.isoformat()
            # il.add_value('date', date_obj.isoformat())

            yield Request(
                url=url,
                callback=self.parse_exhibit_url,
                meta={
                    'data': data
                }
            )

    def parse_exhibit_url(self, response):
        il = FaraItemLoader()

        # state
        il.add_value('state', response.meta.get('data').get('state'))

        # ref_num
        il.add_value('ref_num', response.meta.get('data').get('ref_num'))

        # address
        il.add_value('address', response.meta.get('data').get('address'))

        # principal name
        il.add_value(
            'foreign_principal',
            response.meta.get('data').get('foreign_principal')
        )

        # url
        il.add_value('url', response.meta.get('data').get('url'))

        # date
        il.add_value('date', response.meta.get('data').get('date'))

        # registrant
        il.add_value('registrant', response.meta.get('data').get('registrant'))

        # country is always at the end of the URL
        country = response.url.split(',')[-1]
        il.add_value('country', country)

        # exhibit url - pick the latest one
        # note that we only need the very first row
        path = (
            '//table[@class="apexir_WORKSHEET_DATA"]' +
            '//tr[@class="even" or @class="odd"]'
        )

        sel = Selector(response=response)
        rows = sel.xpath(path)
        if rows:
            row = rows[0]
            link = row.xpath('.//td[contains(@headers, "DOCLINK")]//a/@href')
            link = link.extract_first()
            il.add_value('exhibit_url', link)
        else:
            il.add_value('exhibit_url', None)

        return il.load_item()
