# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HelloscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class DmozItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    desc = scrapy.Field()

class HuoYingItem(scrapy.Item):
    url = scrapy.Field()
    pass

class TumblrUserInfoItem(scrapy.Item):
    page = scrapy.Field()
    user_avatar = scrapy.Field()
    user_host = scrapy.Field()
    user_name = scrapy.Field()
    user_description = scrapy.Field()
