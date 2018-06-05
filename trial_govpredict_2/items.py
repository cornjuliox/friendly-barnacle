# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Join, Compose, TakeFirst

# url, country, state, reg_num, address, foreign_principal,
# date, registrant, exhibit_url

# no exhibit urls
# https://efile.fara.gov/pls/apex/f?p=171:200:6715192268005::NO:RP,200:P200_REG_NUMBER,P200_DOC_TYPE,P200_COUNTRY:5788,Exhibit%20AB,CONGO%20(KINSHASA)%20(ZAIRE)

class FaraItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    country = scrapy.Field()
    state = scrapy.Field()
    ref_num = scrapy.Field()
    address = scrapy.Field()
    foreign_principal = scrapy.Field()
    date = scrapy.Field()
    registrant = scrapy.Field()
    exhibit_url = scrapy.Field()


def nullify(x):
    if not x or len(x) == 0:
        return None
    else: 
        return ' '.join(x) 


class FaraItemLoader(ItemLoader):

    default_item_class = FaraItem

    # helpers for Compose
    strip_str = lambda x: [y.strip() for y in x]
    replace_spaces = lambda x: [y.replace('%20', ' ') for y in x]
    replace_latin_spaces = lambda x: [y.replace(u'\xa0', ' ') for y in x]
    join_or_nullify = lambda x: ' '.join([y for y in x if x])

    address_in = Compose(
        strip_str, replace_spaces, replace_latin_spaces, nullify
    )
    address_out = TakeFirst()

    country_in = Compose(strip_str, replace_spaces, replace_latin_spaces)
    country_out = Join()

    date_out = TakeFirst()

    exhibit_url_in = TakeFirst()
    exhibit_url_out = Join()

    foreign_principal_in = (
        Compose(strip_str, replace_spaces, replace_latin_spaces)
    )
    foreign_principal_out = Join()

    ref_num_out = TakeFirst()

    registrant_out = TakeFirst()

    state_out = TakeFirst()

    url_out = TakeFirst()
